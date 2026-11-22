"use client";

import { useEffect, useRef, useState } from "react";
import { CheckCircle2, ChevronDown, CircleStop, Loader2, TerminalSquare, XCircle } from "lucide-react";
import { api, type Evento } from "@/lib/api";
import { useEjecucion } from "@/lib/useEjecucion";
import { Boton, Etiqueta, LineaPaso, Tarjeta } from "./ui";

// Muestra una ejecucion en tiempo real: progreso, linea de tiempo y consola.
export default function PanelEjecucion({ id }: { id: string }) {
  const { eventos, terminada, estadoFinal } = useEjecucion(id);
  const [consolaAbierta, setConsolaAbierta] = useState(false);
  const finLista = useRef<HTMLDivElement>(null);

  const inicio = eventos.find((e) => e.tipo === "inicio");
  const pasos = eventos.filter((e): e is Extract<Evento, { tipo: "paso" }> => e.tipo === "paso");
  const hechos = new Set(eventos.filter((e) => e.tipo === "paso_ok").map((e) => (e as { indice: number }).indice));
  const total = inicio && inicio.tipo === "inicio" ? (inicio.total ?? 0) : 0;
  const errores = eventos.filter((e) => e.tipo === "error");
  const tiempo = eventos.length ? eventos[eventos.length - 1].t : 0;
  const progreso = total ? (hechos.size / total) * 100 : 0;

  useEffect(() => {
    finLista.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [pasos.length]);

  return (
    <Tarjeta className="aparecer flex flex-col gap-5">
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
            <p className="text-sm font-medium">
              {!terminada ? "Ejecutando…" : estadoFinal === "ok" ? "Completado" : estadoFinal === "detenida" ? "Detenido" : "Ha fallado"}
            </p>
            {inicio?.tipo === "inicio" && inicio.titulo && <p className="text-xs text-tenue">{inicio.titulo}</p>}
          </div>
        </div>
        {!terminada && (
          <Boton variante="peligro" onClick={() => api.detener(id).catch(() => {})}>
            <CircleStop size={15} /> Detener
          </Boton>
        )}
      </div>

      <div className="grid grid-cols-3 gap-2 text-center">
        <Metrica valor={`${hechos.size}/${total || "–"}`} texto="pasos" />
        <Metrica valor={`${tiempo.toFixed(1)} s`} texto="tiempo" />
        <Metrica valor={String(errores.length)} texto="errores" color={errores.length ? "text-mal" : undefined} />
      </div>

      <div className="h-1.5 overflow-hidden rounded-full bg-panel-2">
        <div className="h-full rounded-full bg-gradient-to-r from-violeta to-cian transition-all duration-500" style={{ width: `${progreso}%` }} />
      </div>

      <div className="flex max-h-[45vh] flex-col overflow-y-auto">
        {pasos.length === 0 && !terminada && <p className="py-4 text-center text-sm text-tenue">Abriendo GestCorp 98…</p>}
        {pasos.map((p) => (
          <div key={p.indice} className="aparecer">
            <LineaPaso
              paso={{ accion: p.accion, elemento: p.elemento, texto: p.texto ?? undefined }}
              indice={p.indice}
              estado={hechos.has(p.indice) ? "hecho" : "activo"}
            />
          </div>
        ))}
        <div ref={finLista} />
      </div>

      {errores.map((e, i) => (
        <div key={i} className="rounded-xl border border-mal/40 bg-mal/10 px-3 py-2 font-mono text-xs text-mal">
          {"texto" in e ? e.texto : ""}
        </div>
      ))}

      <div className="rounded-xl border border-borde">
        <button
          onClick={() => setConsolaAbierta((v) => !v)}
          className="flex w-full items-center justify-between px-3 py-2 text-xs text-tenue hover:text-texto"
        >
          <span className="flex items-center gap-2">
            <TerminalSquare size={14} /> Consola <Etiqueta>{eventos.length} eventos</Etiqueta>
          </span>
          <ChevronDown size={14} className={`transition-transform ${consolaAbierta ? "rotate-180" : ""}`} />
        </button>
        {consolaAbierta && (
          <pre className="max-h-64 overflow-auto border-t border-borde bg-black/40 p-3 font-mono text-[11px] leading-relaxed text-tenue">
            {eventos.map((e) => `[${e.t.toFixed(2).padStart(6)}s] ${JSON.stringify(e)}`).join("\n")}
          </pre>
        )}
      </div>
    </Tarjeta>
  );
}

function Metrica({ valor, texto, color }: { valor: string; texto: string; color?: string }) {
  return (
    <div className="rounded-xl border border-borde bg-panel py-2">
      <p className={`font-mono text-lg font-semibold ${color ?? ""}`}>{valor}</p>
      <p className="text-[11px] uppercase tracking-wider text-tenue">{texto}</p>
    </div>
  );
}
