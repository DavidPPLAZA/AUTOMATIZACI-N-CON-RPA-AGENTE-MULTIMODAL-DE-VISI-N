"use client";

import { useEffect, useRef } from "react";
import type { Evento } from "@/lib/api";
import { useEjecucion } from "@/lib/useEjecucion";
import { LineaPaso, Tarjeta } from "./ui";
import { CabeceraEjecucion, Consola, Errores, Metrica } from "./ejecucion";

// Muestra la ejecucion de un robot en tiempo real: progreso, pasos y consola.
export default function PanelEjecucion({ id }: { id: string }) {
  const { eventos, terminada, estadoFinal } = useEjecucion(id);
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
      <CabeceraEjecucion
        id={id}
        terminada={terminada}
        estadoFinal={estadoFinal}
        subtitulo={inicio?.tipo === "inicio" ? inicio.titulo : undefined}
      />

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

      <Errores eventos={eventos} />
      <Consola eventos={eventos} />
    </Tarjeta>
  );
}
