"use client";

import Link from "next/link";
import { useEffect, useRef } from "react";
import {
  ArrowRight,
  Bot,
  Brain,
  Eraser,
  Eye,
  Info,
  ListChecks,
  MousePointerClick,
  ShieldCheck,
  Type,
  Wrench,
  type LucideIcon,
} from "lucide-react";
import type { Evento } from "@/lib/api";
import { useEjecucion } from "@/lib/useEjecucion";
import { Tarjeta } from "./ui";
import { CabeceraEjecucion, Consola, Errores, Metrica } from "./ejecucion";

// Lo que se pinta en la linea de tiempo. Cada llamada a una herramienta se
// junta con su resultado y con lo que UI-TARS leyo mientras tanto.
type Item =
  | { tipo: "tool"; nombre: string; args: Record<string, unknown>; resultado: string | null; lecturas: { frase: string; respuesta: string }[] }
  | { tipo: "texto"; texto: string }
  | { tipo: "mensaje"; texto: string };

function agrupar(eventos: Evento[]): { items: Item[]; robot: string | null } {
  const items: Item[] = [];
  let robot: string | null = null;
  const pendiente = () =>
    [...items].reverse().find((i): i is Extract<Item, { tipo: "tool" }> => i.tipo === "tool" && i.resultado === null);
  for (const e of eventos) {
    if (e.tipo === "tool") items.push({ tipo: "tool", nombre: e.nombre, args: e.args, resultado: null, lecturas: [] });
    else if (e.tipo === "lectura") pendiente()?.lecturas.push({ frase: e.frase, respuesta: e.respuesta });
    else if (e.tipo === "tool_resultado") {
      const t = items.find((i): i is Extract<Item, { tipo: "tool" }> => i.tipo === "tool" && i.resultado === null && i.nombre === e.nombre);
      if (t) t.resultado = e.texto;
    } else if (e.tipo === "texto_agente") items.push({ tipo: "texto", texto: e.texto });
    else if (e.tipo === "mensaje") items.push({ tipo: "mensaje", texto: e.texto });
    else if (e.tipo === "robot_guardado") robot = e.id;
  }
  return { items, robot };
}

const ICONOS: Record<string, LucideIcon> = {
  pulsar: MousePointerClick,
  rellenar_campo: Type,
  borrar_campo: Eraser,
  seleccionar_en_desplegable: ListChecks,
};

const esVerificacion = (nombre: string) => nombre.startsWith("verificar_");

// Muestra en tiempo real lo que hace el agente: que razona, que herramienta
// usa, que lee UI-TARS al verificar y, al final, el robot que ha generado.
export default function MenteAgente({ id }: { id: string }) {
  const { eventos, terminada, estadoFinal } = useEjecucion(id);
  const finLista = useRef<HTMLDivElement>(null);
  const { items, robot } = agrupar(eventos);

  const tools = items.filter((i) => i.tipo === "tool");
  const acciones = tools.filter((t) => !esVerificacion(t.nombre)).length;
  const verificaciones = tools.length - acciones;
  const tiempo = eventos.length ? eventos[eventos.length - 1].t : 0;

  useEffect(() => {
    finLista.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [eventos.length]);

  return (
    <Tarjeta className="aparecer flex flex-col gap-5">
      <CabeceraEjecucion
        id={id}
        terminada={terminada}
        estadoFinal={estadoFinal}
        textoEnCurso="El agente está trabajando…"
        subtitulo="GestCorp 98 se mueve sola en la otra mitad de la pantalla"
      />

      <div className="grid grid-cols-3 gap-2 text-center">
        <Metrica valor={String(acciones)} texto="acciones" />
        <Metrica valor={String(verificaciones)} texto="verificaciones" />
        <Metrica valor={`${tiempo.toFixed(0)} s`} texto="tiempo" />
      </div>

      <div className="flex max-h-[60vh] flex-col gap-1 overflow-y-auto pr-1">
        {items.map((item, i) => (
          <div key={i} className="aparecer">
            {item.tipo === "tool" ? (
              <LineaTool item={item} />
            ) : item.tipo === "texto" ? (
              <div className="flex gap-3 rounded-xl px-3 py-2.5">
                <Brain size={16} className="mt-0.5 shrink-0 text-violet-300" />
                <p className="whitespace-pre-wrap text-sm text-texto/90">{item.texto}</p>
              </div>
            ) : (
              <p className="flex items-center gap-2 px-3 py-1.5 text-xs text-tenue">
                <Info size={13} className="shrink-0" /> {item.texto}
              </p>
            )}
          </div>
        ))}
        <div ref={finLista} />
      </div>

      <Errores eventos={eventos} />

      {robot && (
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-bien/40 bg-bien/10 px-4 py-3">
          <p className="flex items-center gap-2 text-sm text-bien">
            <Bot size={16} /> Robot generado: ya se puede repetir sin IA.
          </p>
          <Link
            href={`/robots/${robot}`}
            className="inline-flex items-center gap-2 rounded-xl border border-borde-2 bg-panel px-4 py-2.5 text-sm font-medium hover:bg-panel-2"
          >
            Ver robot <ArrowRight size={15} />
          </Link>
        </div>
      )}

      <Consola eventos={eventos} />
    </Tarjeta>
  );
}

function LineaTool({ item }: { item: Extract<Item, { tipo: "tool" }> }) {
  const verif = esVerificacion(item.nombre);
  const Icono = verif ? ShieldCheck : (ICONOS[item.nombre] ?? Wrench);
  const enCurso = item.resultado === null;
  // las verificaciones empiezan por "SI:" o "NO:"
  const mal = verif && item.resultado?.startsWith("NO");
  const anillo = enCurso
    ? "border-cian/60 bg-cian/10 text-cian latido"
    : mal
      ? "border-mal/40 bg-mal/10 text-mal"
      : "border-bien/40 bg-bien/10 text-bien";
  const args = Object.entries(item.args)
    .filter(([, v]) => v !== "" && v != null)
    .map(([k, v]) => `${k}: ${String(v)}`);

  return (
    <div className={`flex items-start gap-3 rounded-xl px-3 py-2.5 ${enCurso ? "bg-panel-2" : ""}`}>
      <span className={`mt-0.5 grid h-7 w-7 shrink-0 place-items-center rounded-lg border ${anillo}`}>
        <Icono size={14} />
      </span>
      <div className="min-w-0 flex-1">
        <p className="font-mono text-xs font-medium">{item.nombre}</p>
        {args.map((a) => (
          <p key={a} className="text-xs text-tenue">{a}</p>
        ))}
        {item.lecturas.map((l, i) => (
          <p key={i} className="mt-1 flex items-start gap-1.5 text-xs text-tenue">
            <Eye size={12} className="mt-0.5 shrink-0 text-cian" />
            <span>
              {l.frase} <code className="rounded bg-cian/10 px-1 text-cian">{l.respuesta || "(vacío)"}</code>
            </span>
          </p>
        ))}
        {item.resultado && (
          <p className={`mt-1 whitespace-pre-wrap text-xs ${mal ? "text-mal" : "text-texto/80"}`}>{item.resultado}</p>
        )}
      </div>
    </div>
  );
}
