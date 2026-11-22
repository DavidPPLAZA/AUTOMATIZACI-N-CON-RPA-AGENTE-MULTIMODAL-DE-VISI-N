// Piezas visuales reutilizables (sin estado).
import type { ReactNode } from "react";
import { MousePointerClick, Type } from "lucide-react";
import type { Paso } from "@/lib/api";

export function Logo({ size = 28 }: { size?: number }) {
  return (
    <span
      className="grid place-items-center rounded-lg bg-gradient-to-br from-violeta to-cian shadow-[0_0_20px_-4px] shadow-violeta/60"
      style={{ width: size, height: size }}
    >
      <svg viewBox="0 0 24 24" width={size * 0.6} height={size * 0.6} fill="none" stroke="white" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
        {/* un cursor dentro de un ojo: clics + vision */}
        <path d="M2 12s3.6-6.5 10-6.5S22 12 22 12" />
        <path d="M10 10l7 3-3 1-1 3z" fill="white" />
      </svg>
    </span>
  );
}

export function Tarjeta({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <div className={`borde-degradado rounded-2xl bg-panel p-5 backdrop-blur-sm ${className}`}>{children}</div>
  );
}

export function Etiqueta({ children, color = "tenue" }: { children: ReactNode; color?: "tenue" | "violeta" | "cian" | "bien" | "aviso" | "mal" }) {
  const colores = {
    tenue: "text-tenue border-borde-2",
    violeta: "text-violet-300 border-violeta/40 bg-violeta/10",
    cian: "text-cian border-cian/40 bg-cian/10",
    bien: "text-bien border-bien/40 bg-bien/10",
    aviso: "text-aviso border-aviso/40 bg-aviso/10",
    mal: "text-mal border-mal/40 bg-mal/10",
  };
  return (
    <span className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[11px] font-medium ${colores[color]}`}>
      {children}
    </span>
  );
}

export function TituloSeccion({ titulo, subtitulo, accion }: { titulo: string; subtitulo?: string; accion?: ReactNode }) {
  return (
    <div className="mb-6 flex items-end justify-between gap-4">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">{titulo}</h1>
        {subtitulo && <p className="mt-1 text-sm text-tenue">{subtitulo}</p>}
      </div>
      {accion}
    </div>
  );
}

export function Boton({
  children,
  onClick,
  disabled,
  variante = "primario",
  className = "",
}: {
  children: ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  variante?: "primario" | "secundario" | "peligro";
  className?: string;
}) {
  const estilos = {
    primario:
      "bg-gradient-to-r from-violeta to-cian text-white shadow-[0_8px_30px_-8px] shadow-violeta/60 hover:brightness-110",
    secundario: "border border-borde-2 bg-panel text-texto hover:bg-panel-2",
    peligro: "border border-mal/40 bg-mal/10 text-mal hover:bg-mal/20",
  };
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium transition-all disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:brightness-100 ${estilos[variante]} ${className}`}
    >
      {children}
    </button>
  );
}

// Una linea legible de un paso del robot: icono + que hace + donde.
export function LineaPaso({ paso, indice, estado = "pendiente" }: { paso: Pick<Paso, "accion" | "elemento" | "texto">; indice: number; estado?: "pendiente" | "activo" | "hecho" }) {
  const Icono = paso.accion === "click" ? MousePointerClick : Type;
  const anillo =
    estado === "activo"
      ? "border-cian/60 bg-cian/10 text-cian latido"
      : estado === "hecho"
        ? "border-bien/40 bg-bien/10 text-bien"
        : "border-borde-2 bg-panel text-tenue";
  return (
    <div className={`flex items-start gap-3 rounded-xl px-3 py-2.5 transition-colors ${estado === "activo" ? "bg-panel-2" : ""}`}>
      <span className={`mt-0.5 grid h-7 w-7 shrink-0 place-items-center rounded-lg border ${anillo}`}>
        <Icono size={14} />
      </span>
      <div className="min-w-0 flex-1">
        <div className="flex items-baseline gap-2 text-sm">
          <span className="font-mono text-xs text-tenue">{String(indice + 1).padStart(2, "0")}</span>
          <span className="font-medium">{paso.accion === "click" ? "Clic" : "Escribir"}</span>
          {paso.texto != null && (
            <code className="truncate rounded bg-violeta/15 px-1.5 py-0.5 font-mono text-xs text-violet-200">
              “{paso.texto}”
            </code>
          )}
        </div>
        <p className="truncate text-xs text-tenue">{paso.elemento}</p>
      </div>
    </div>
  );
}
