"use client";

import { useEffect, useState } from "react";
import { Cpu, Eye, Play, RotateCcw, Unplug } from "lucide-react";
import { api, ErrorApi } from "@/lib/api";
import { Boton, Etiqueta, Tarjeta, TituloSeccion } from "@/components/ui";
import MenteAgente from "@/components/MenteAgente";

export default function Estudio() {
  const [ejemplo, setEjemplo] = useState("");
  const [prompt, setPrompt] = useState("");
  const [aviso, setAviso] = useState<string | null>(null);
  const [lanzando, setLanzando] = useState(false);
  const [ejecucion, setEjecucion] = useState<string | null>(null);

  useEffect(() => {
    api
      .promptEjemplo()
      .then(({ prompt }) => {
        setEjemplo(prompt);
        setPrompt((actual) => actual || prompt);
      })
      .catch((e: ErrorApi) => setAviso(e.message));
    // si el agente ya estaba trabajando (p.ej. se recargo la pagina), engancharse
    api
      .estado()
      .then(({ ejecucion_activa }) => {
        if (ejecucion_activa?.modo === "agente") setEjecucion(ejecucion_activa.id);
      })
      .catch(() => {});
  }, []);

  async function lanzar() {
    setLanzando(true);
    setAviso(null);
    try {
      const e = await api.lanzarAgente(prompt);
      setEjecucion(e.id);
    } catch (e) {
      setAviso((e as ErrorApi).message);
    } finally {
      setLanzando(false);
    }
  }

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6">
      <TituloSeccion
        titulo="Estudio"
        subtitulo="Describe el proceso. El agente lo ejecuta en GestCorp 98 y lo convierte en un robot."
      />

      <Tarjeta className="flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <label htmlFor="prompt" className="text-sm font-medium">
            Instrucciones
          </label>
          <div className="flex items-center gap-2">
            <Etiqueta color="violeta">App: GestCorp 98</Etiqueta>
            {ejemplo && prompt !== ejemplo && (
              <button
                onClick={() => setPrompt(ejemplo)}
                className="flex items-center gap-1 text-xs text-tenue hover:text-texto"
              >
                <RotateCcw size={12} /> Ejemplo
              </button>
            )}
          </div>
        </div>
        <textarea
          id="prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          rows={12}
          spellCheck={false}
          placeholder="OBJETIVO: … PASO 1: …"
          className="w-full resize-y rounded-xl border border-borde-2 bg-black/30 p-4 font-mono text-[13px] leading-relaxed text-texto outline-none transition focus:border-violeta/60 focus:ring-4 focus:ring-violeta/15"
        />
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap gap-2">
            <Etiqueta><Cpu size={11} /> gpt-oss-120b · Groq</Etiqueta>
            <Etiqueta><Eye size={11} /> UI-TARS-7B · GPU</Etiqueta>
          </div>
          <Boton onClick={lanzar} disabled={!prompt.trim() || lanzando}>
            <Play size={15} /> Lanzar agente
          </Boton>
        </div>
        {aviso && (
          <div className="flex items-start gap-2 rounded-xl border border-aviso/40 bg-aviso/10 px-3 py-2.5 text-sm text-aviso">
            <Unplug size={16} className="mt-0.5 shrink-0" />
            {aviso}
          </div>
        )}
      </Tarjeta>

      {ejecucion ? (
        <MenteAgente key={ejecucion} id={ejecucion} />
      ) : (
        <Tarjeta className="flex flex-col items-center gap-2 py-10 text-center">
          <span className="grid h-12 w-12 place-items-center rounded-2xl border border-borde-2 bg-panel text-tenue">
            <Eye size={20} />
          </span>
          <p className="text-sm font-medium">Mente del agente</p>
          <p className="max-w-sm text-xs text-tenue">
            Aquí verás en tiempo real cada herramienta que usa el agente, sus verificaciones y
            correcciones. Mientras tanto, GestCorp 98 se moverá sola en la otra mitad de la pantalla.
          </p>
        </Tarjeta>
      )}
    </div>
  );
}
