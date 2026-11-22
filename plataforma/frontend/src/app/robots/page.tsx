"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Bot, ChevronRight, Footprints, Trash2 } from "lucide-react";
import { api, confirmarBorrado, ErrorApi, formatearFecha, type ResumenFlujo } from "@/lib/api";
import { TituloSeccion } from "@/components/ui";

export default function Robots() {
  const [flujos, setFlujos] = useState<ResumenFlujo[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.flujos().then(setFlujos).catch((e: ErrorApi) => setError(e.message));
  }, []);

  async function borrar(f: ResumenFlujo) {
    if (!confirmarBorrado(f.titulo, f.fecha)) return;
    try {
      await api.borrarFlujo(f.id);
      setFlujos((actual) => actual?.filter((x) => x.id !== f.id) ?? null);
    } catch (e) {
      setError((e as ErrorApi).message);
    }
  }

  return (
    <div className="mx-auto w-full max-w-3xl">
      <TituloSeccion
        titulo="Robots"
        subtitulo="Flujos RPA generados por el agente. Se ejecutan sin IA, siempre igual."
      />
      {error && <p className="rounded-xl border border-mal/40 bg-mal/10 px-3 py-2.5 text-sm text-mal">{error}</p>}
      {!flujos && !error && (
        <div className="flex flex-col gap-3">
          {[0, 1, 2].map((i) => <div key={i} className="h-20 animate-pulse rounded-2xl bg-panel" />)}
        </div>
      )}
      {flujos?.length === 0 && <p className="text-sm text-tenue">Todavía no hay robots. Créalos desde el Estudio.</p>}
      <div className="flex flex-col gap-3">
        {flujos?.map((f, i) => (
          <div key={f.id} className="aparecer flex items-center gap-2" style={{ animationDelay: `${i * 60}ms` }}>
            <Link
              href={`/robots/${f.id}`}
              className="group flex min-w-0 flex-1 items-center gap-4 rounded-2xl border border-borde bg-panel p-4 transition hover:border-violeta/40 hover:bg-panel-2"
            >
              <span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-gradient-to-br from-violeta/25 to-cian/15 text-violet-200">
                <Bot size={20} />
              </span>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium">{f.titulo}</p>
                <p className="mt-1 flex items-center gap-3 text-xs text-tenue">
                  <span className="flex items-center gap-1"><Footprints size={12} /> {f.n_pasos} pasos</span>
                  <span>{formatearFecha(f.fecha)}</span>
                </p>
              </div>
              <ChevronRight size={18} className="text-tenue transition group-hover:translate-x-0.5 group-hover:text-texto" />
            </Link>
            <button
              onClick={() => borrar(f)}
              title="Eliminar robot"
              aria-label={`Eliminar robot ${f.titulo}`}
              className="grid h-11 w-11 shrink-0 place-items-center rounded-xl border border-borde text-tenue transition hover:border-mal/40 hover:bg-mal/10 hover:text-mal"
            >
              <Trash2 size={16} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
