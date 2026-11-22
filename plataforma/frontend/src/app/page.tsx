import Link from "next/link";
import { ArrowRight, Bot, Eye, FileJson, MessageSquareText, MousePointerClick, ShieldCheck } from "lucide-react";
import { Tarjeta } from "@/components/ui";

const PASOS = [
  {
    icono: MessageSquareText,
    titulo: "Descríbelo",
    texto: "Explicas el proceso en lenguaje natural, como se lo contarías a un compañero.",
  },
  {
    icono: Eye,
    titulo: "El agente lo hace",
    texto: "Mira la pantalla con un modelo de visión, hace clic, escribe, verifica cada formulario y se corrige.",
  },
  {
    icono: Bot,
    titulo: "Tu robot, listo",
    texto: "Cada acción queda grabada en un flujo RPA que se repite en segundos, sin IA.",
  },
];

const PILARES = [
  { icono: MousePointerClick, titulo: "Herramientas de clics", texto: "pulsar, rellenar campos y elegir en desplegables sobre la app real." },
  { icono: Eye, titulo: "Herramientas de visión", texto: "UI-TARS localiza cada elemento y lee lo escrito para verificar." },
  { icono: ShieldCheck, titulo: "Determinista", texto: "El robot final no improvisa: repite exactamente los mismos pasos." },
  { icono: FileJson, titulo: "Auditable", texto: "Cada paso, coordenada y verificación queda registrado en JSON." },
];

export default function Portada() {
  return (
    <div className="flex flex-col gap-16 py-6">
      <section className="aparecer flex flex-col items-start gap-6 pt-6">
        <span className="rounded-full border border-borde-2 bg-panel px-3 py-1 text-xs text-tenue">
          Agente · RPA · Visión
        </span>
        <h1 className="text-5xl font-semibold leading-[1.05] tracking-tight sm:text-6xl">
          <span className="texto-degradado">Automatizando</span>
          <br />
          la automatización
        </h1>
        <p className="max-w-xl text-lg leading-relaxed text-tenue">
          Agente orquestador con herramientas de clics y herramientas de visión para diseñar
          automatizaciones <span className="text-texto">deterministas</span> y{" "}
          <span className="text-texto">auditables</span>.
        </p>
        <div className="flex flex-wrap gap-3">
          <Link
            href="/estudio"
            className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-violeta to-cian px-5 py-3 text-sm font-medium text-white shadow-[0_8px_30px_-8px] shadow-violeta/60 transition hover:brightness-110"
          >
            Crear automatización <ArrowRight size={16} />
          </Link>
          <Link
            href="/robots"
            className="inline-flex items-center gap-2 rounded-xl border border-borde-2 bg-panel px-5 py-3 text-sm font-medium transition hover:bg-panel-2"
          >
            <Bot size={16} /> Ver robots
          </Link>
        </div>
      </section>

      <section className="flex flex-col gap-3">
        {PASOS.map(({ icono: Icono, titulo, texto }, i) => (
          <div key={titulo} className="aparecer" style={{ animationDelay: `${150 + i * 120}ms` }}>
            <Tarjeta className="flex items-start gap-4">
              <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-violeta/15 text-violet-300">
                <Icono size={18} />
              </span>
              <div>
                <p className="text-sm font-medium">
                  <span className="mr-2 font-mono text-xs text-tenue">0{i + 1}</span>
                  {titulo}
                </p>
                <p className="mt-1 text-sm text-tenue">{texto}</p>
              </div>
            </Tarjeta>
          </div>
        ))}
      </section>

      <section>
        <h2 className="mb-4 text-sm font-medium uppercase tracking-widest text-tenue">Cómo funciona</h2>
        <div className="grid gap-3 sm:grid-cols-2">
          {PILARES.map(({ icono: Icono, titulo, texto }) => (
            <div key={titulo} className="rounded-2xl border border-borde bg-panel p-4">
              <Icono size={18} className="text-cian" />
              <p className="mt-3 text-sm font-medium">{titulo}</p>
              <p className="mt-1 text-xs leading-relaxed text-tenue">{texto}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
