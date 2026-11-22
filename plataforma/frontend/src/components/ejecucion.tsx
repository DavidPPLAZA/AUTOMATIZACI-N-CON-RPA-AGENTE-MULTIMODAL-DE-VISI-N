"use client";

// Piezas comunes de los paneles de ejecucion (robot y agente).
import { useState, type ReactNode } from "react";
import { CheckCircle2, ChevronDown, CircleStop, Loader2, TerminalSquare, XCircle } from "lucide-react";
import { api, type Evento, type ResumenEjecucion } from "@/lib/api";
import { Boton, Etiqueta } from "./ui";

// Icono + estado + boton Detener mientras sigue en marcha.
export function CabeceraEjecucion({
  id,
  terminada,
  estadoFinal,
  subtitulo,
  textoEnCurso = "Ejecutando…",
}: {
  id: string;
  terminada: boolean;
  estadoFinal: ResumenEjecucion["estado"] | null;
  subtitulo?: ReactNode;
  textoEnCurso?: string;
}) {
  const titulo = !terminada
    ? textoEnCurso
    : estadoFinal === "ok"
      ? "Completado"
      : estadoFinal === "detenida"
        ? "Detenido"
        : "Ha fallado";
  return (
    <div className="flex items-center justify-between gap-3">
      <div className="flex items-center gap-2.5">
        {!terminada ? (
          <Loader2 size={18} className="animate-spin text-cian" />
        ) : estadoFinal === "ok" ? (
          <CheckCircle2 size={18} className="text-bien" />
        ) : (
          <XCircle size={18} className="text-mal" />
        )}
        <div>
          <p className="text-sm font-medium">{titulo}</p>
          {subtitulo && <p className="text-xs text-tenue">{subtitulo}</p>}
        </div>
      </div>
      {!terminada && (
        <Boton variante="peligro" onClick={() => api.detener(id).catch(() => {})}>
          <CircleStop size={15} /> Detener
        </Boton>
      )}
    </div>
  );
}

export function Metrica({ valor, texto, color }: { valor: string; texto: string; color?: string }) {
  return (
    <div className="rounded-xl border border-borde bg-panel py-2">
      <p className={`font-mono text-lg font-semibold ${color ?? ""}`}>{valor}</p>
      <p className="text-[11px] uppercase tracking-wider text-tenue">{texto}</p>
    </div>
  );
}

// Todos los eventos en crudo, plegada por defecto.
export function Consola({ eventos }: { eventos: Evento[] }) {
  const [abierta, setAbierta] = useState(false);
  return (
    <div className="rounded-xl border border-borde">
      <button
        onClick={() => setAbierta((v) => !v)}
        className="flex w-full items-center justify-between px-3 py-2 text-xs text-tenue hover:text-texto"
      >
        <span className="flex items-center gap-2">
          <TerminalSquare size={14} /> Consola <Etiqueta>{eventos.length} eventos</Etiqueta>
        </span>
        <ChevronDown size={14} className={`transition-transform ${abierta ? "rotate-180" : ""}`} />
      </button>
      {abierta && (
        <pre className="max-h-64 overflow-auto border-t border-borde bg-black/40 p-3 font-mono text-[11px] leading-relaxed text-tenue">
          {eventos.map((e) => `[${e.t.toFixed(2).padStart(6)}s] ${JSON.stringify(e)}`).join("\n")}
        </pre>
      )}
    </div>
  );
}

export function Errores({ eventos }: { eventos: Evento[] }) {
  return (
    <>
      {eventos.map((e, i) =>
        e.tipo === "error" ? (
          <div key={i} className="rounded-xl border border-mal/40 bg-mal/10 px-3 py-2 font-mono text-xs text-mal">
            {e.texto}
          </div>
        ) : null,
      )}
    </>
  );
}
