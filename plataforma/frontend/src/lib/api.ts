// Cliente del backend (FastAPI). Todo lo que la web sabe del backend pasa por aqui.

export const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
export const WS = API.replace(/^http/, "ws");

export type ResumenFlujo = {
  id: string;
  titulo: string;
  fecha: string | null;
  n_pasos: number;
};

export type Paso = {
  accion: "click" | "escribir";
  elemento: string;
  x: number;
  y: number;
  texto?: string;
};

export type Flujo = {
  id: string;
  titulo: string;
  fecha: string | null;
  instruccion: string;
  ventana: { ancho: number; alto: number };
  pasos: Paso[];
};

export type ResumenEjecucion = {
  id: string;
  modo: "robot" | "agente";
  estado: "en_curso" | "ok" | "error" | "detenida";
  inicio: string;
};

export type EstadoBackend = {
  ok: boolean;
  agente_conectado: boolean;
  ejecucion_activa: ResumenEjecucion | null;
};

// Eventos que llegan por el WebSocket ("contrato" con el backend).
export type Evento = { t: number } & (
  | { tipo: "inicio"; modo: "robot" | "agente"; titulo?: string; total?: number }
  | { tipo: "paso"; indice: number; total: number; accion: Paso["accion"]; elemento: string; texto?: string | null; x: number; y: number }
  | { tipo: "paso_ok"; indice: number }
  // del agente: herramienta que llama, lo que le devuelve, lo que lee UI-TARS
  // al verificar, lo que escribe el LLM y el robot que se guarda al terminar
  | { tipo: "tool"; nombre: string; args: Record<string, unknown> }
  | { tipo: "tool_resultado"; nombre: string; texto: string }
  | { tipo: "lectura"; frase: string; respuesta: string }
  | { tipo: "texto_agente"; texto: string }
  | { tipo: "robot_guardado"; id: string }
  | { tipo: "mensaje"; texto: string }
  | { tipo: "error"; texto: string }
  | { tipo: "fin"; estado: ResumenEjecucion["estado"] }
);

export class ErrorApi extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function pedir<T>(ruta: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API}${ruta}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...init?.headers },
      cache: "no-store",
    });
  } catch {
    throw new ErrorApi(0, "No hay conexión con el backend. ¿Está arrancado en el puerto 8000?");
  }
  if (!res.ok) {
    const cuerpo = await res.json().catch(() => null);
    throw new ErrorApi(res.status, cuerpo?.detail ?? `Error ${res.status}`);
  }
  return res.json();
}

export const api = {
  estado: () => pedir<EstadoBackend>("/estado"),
  promptEjemplo: () => pedir<{ prompt: string }>("/prompt-ejemplo"),
  flujos: () => pedir<ResumenFlujo[]>("/flujos"),
  flujo: (id: string) => pedir<Flujo>(`/flujos/${encodeURIComponent(id)}`),
  borrarFlujo: (id: string) => pedir<{ ok: boolean }>(`/flujos/${encodeURIComponent(id)}`, { method: "DELETE" }),
  ejecutarRobot: (flujo: string) =>
    pedir<ResumenEjecucion>("/ejecuciones/robot", { method: "POST", body: JSON.stringify({ flujo }) }),
  lanzarAgente: (prompt: string) =>
    pedir<ResumenEjecucion>("/ejecuciones/agente", { method: "POST", body: JSON.stringify({ prompt }) }),
  detener: (id: string) => pedir<ResumenEjecucion>(`/ejecuciones/${id}/detener`, { method: "POST" }),
};

// Borrar un robot elimina su JSON del disco: no se puede deshacer, asi que se pregunta antes.
export function confirmarBorrado(titulo: string, fecha: string | null): boolean {
  return window.confirm(`¿Eliminar el robot «${titulo}» (${formatearFecha(fecha)})?\n\nSe borra su archivo y no se puede deshacer.`);
}

export function formatearFecha(iso: string | null): string {
  if (!iso) return "sin fecha";
  return new Date(iso).toLocaleString("es-ES", { dateStyle: "medium", timeStyle: "short" });
}
