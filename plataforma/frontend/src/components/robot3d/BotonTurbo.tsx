"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { estado } from "./estado";

/** Enlace que pone al perezoso a teclear en modo turbo mientras el cursor (o el foco) esta encima. */
export default function BotonTurbo({ href, className, children }: { href: string; className?: string; children: ReactNode }) {
  const turbo = (si: boolean) => () => {
    estado.botonTurbo = si;
  };
  return (
    <Link
      href={href}
      className={className}
      onMouseEnter={turbo(true)}
      onMouseLeave={turbo(false)}
      onFocus={turbo(true)}
      onBlur={turbo(false)}
    >
      {children}
    </Link>
  );
}
