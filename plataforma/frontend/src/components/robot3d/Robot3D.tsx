"use client";

import dynamic from "next/dynamic";
import { useEffect, useSyncExternalStore } from "react";
import { seguirPuntero } from "./estado";

// La escena 3D solo existe en el navegador (WebGL): se carga aparte, sin
// bloquear el resto de la portada.
const Escena = dynamic(() => import("./Escena"), {
  ssr: false,
  loading: () => <Cargando />,
});

function Cargando() {
  return (
    <div className="grid h-full w-full place-items-center">
      <div className="h-24 w-24 animate-pulse rounded-full bg-gradient-to-br from-violeta/30 to-cian/20 blur-sm" />
    </div>
  );
}

// lee una media query del navegador y se actualiza si cambia
function useMedia(consulta: string) {
  return useSyncExternalStore(
    (cb) => {
      const m = window.matchMedia(consulta);
      m.addEventListener("change", cb);
      return () => m.removeEventListener("change", cb);
    },
    () => window.matchMedia(consulta).matches,
    () => false,
  );
}

export default function Robot3D() {
  const quieto = useMedia("(prefers-reduced-motion: reduce)");
  const tactil = useMedia("(pointer: coarse)"); // movil: sin cursor que seguir

  // el buho sigue al cursor por toda la pagina, no solo encima del canvas
  useEffect(() => (tactil ? undefined : seguirPuntero()), [tactil]);

  return (
    <div className="relative aspect-square w-full">
      {/* halo detras del personaje */}
      <div className="pointer-events-none absolute inset-[12%] rounded-full bg-[radial-gradient(circle,rgb(139_92_246/0.28),transparent_65%)] blur-2xl" />
      <Escena quieto={quieto} tactil={tactil} />
    </div>
  );
}
