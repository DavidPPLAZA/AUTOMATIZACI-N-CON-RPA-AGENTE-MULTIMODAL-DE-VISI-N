"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { ArrowLeft, Download, Zap } from "lucide-react";
import { api, API, ErrorApi, formatearFecha, type Flujo } from "@/lib/api";
import { Boton, Etiqueta, LineaPaso, Tarjeta } from "@/components/ui";
import PanelEjecucion from "@/components/PanelEjecucion";

export default function DetalleRobot() {
  const { id } = useParams<{ id: string }>();
  const [flujo, setFlujo] = useState<Flujo | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [ejecucion, setEjecucion] = useState<string | null>(null);
  const [verPrompt, setVerPrompt] = useState(false);

  useEffect(() => {
    api.flujo(id).then(setFlujo).catch((e: ErrorApi) => setError(e.message));
  }, [id]);

  async function ejecutar() {
    setError(null);
    try {
      const e = await api.ejecutarRobot(id);
      setEjecucion(e.id);
    } catch (e) {
      setError((e as ErrorApi).message);
    }
  }

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6">
      <Link href="/robots" className="flex w-fit items-center gap-1.5 text-sm text-tenue hover:text-texto">
        <ArrowLeft size={15} /> Robots
      </Link>

      {flujo && (
        <>
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">{flujo.titulo}</h1>
            <div className="mt-2 flex flex-wrap gap-2">
              <Etiqueta color="violeta">{flujo.pasos.length} pasos</Etiqueta>
              <Etiqueta>{formatearFecha(flujo.fecha)}</Etiqueta>
              <Etiqueta>ventana {flujo.ventana.ancho}×{flujo.ventana.alto}</Etiqueta>
            </div>
          </div>

          <div className="flex flex-wrap gap-3">
            <Boton onClick={ejecutar} disabled={flujo.pasos.length === 0}>
              <Zap size={15} /> Ejecutar robot
            </Boton>
            <a href={`${API}/flujos/${flujo.id}`} download={`${flujo.id}.json`} target="_blank" rel="noreferrer">
              <Boton variante="secundario">
                <Download size={15} /> JSON
              </Boton>
            </a>
          </div>
        </>
      )}

      {error && <p className="rounded-xl border border-mal/40 bg-mal/10 px-3 py-2.5 text-sm text-mal">{error}</p>}

      {ejecucion && <PanelEjecucion key={ejecucion} id={ejecucion} />}

      {flujo && (
        <>
          <Tarjeta>
            <p className="mb-2 text-sm font-medium">Pasos del robot</p>
            {flujo.pasos.length === 0 && <p className="text-sm text-tenue">Este flujo no tiene pasos.</p>}
            <div className="-mx-3 flex flex-col">
              {flujo.pasos.map((p, i) => <LineaPaso key={i} paso={p} indice={i} />)}
            </div>
          </Tarjeta>

          {flujo.instruccion && (
            <Tarjeta>
              <button onClick={() => setVerPrompt((v) => !v)} className="text-sm font-medium hover:text-cian">
                {verPrompt ? "Ocultar" : "Ver"} instrucciones originales
              </button>
              {verPrompt && (
                <p className="mt-3 whitespace-pre-wrap font-mono text-xs leading-relaxed text-tenue">{flujo.instruccion}</p>
              )}
            </Tarjeta>
          )}
        </>
      )}
    </div>
  );
}
