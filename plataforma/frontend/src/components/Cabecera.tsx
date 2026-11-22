"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Bot, LayoutGrid, Sparkles } from "lucide-react";
import { Logo } from "./ui";

const ENLACES = [
  { href: "/estudio", texto: "Estudio", icono: Sparkles },
  { href: "/robots", texto: "Robots", icono: Bot },
];

export default function Cabecera() {
  const ruta = usePathname();
  return (
    <header className="sticky top-0 z-20 border-b border-borde bg-fondo/70 backdrop-blur-md">
      <div className="max-w-6xl mx-auto px-5 h-14 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2.5 font-semibold tracking-tight">
          <Logo />
          <span className="hidden sm:inline">
            Automatizando <span className="text-tenue font-normal">la automatización</span>
          </span>
        </Link>
        <nav className="flex items-center gap-1">
          {ENLACES.map(({ href, texto, icono: Icono }) => {
            const activo = ruta.startsWith(href);
            return (
              <Link
                key={href}
                href={href}
                className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm transition-colors ${
                  activo ? "bg-panel-2 text-texto" : "text-tenue hover:text-texto hover:bg-panel"
                }`}
              >
                <Icono size={15} />
                {texto}
              </Link>
            );
          })}
          <Link
            href="/"
            className={`ml-1 rounded-lg p-1.5 transition-colors ${
              ruta === "/" ? "text-texto" : "text-tenue hover:text-texto"
            }`}
            aria-label="Inicio"
          >
            <LayoutGrid size={16} />
          </Link>
        </nav>
      </div>
    </header>
  );
}
