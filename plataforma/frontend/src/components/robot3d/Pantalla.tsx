"use client";

// Pantalla holografica, como el monitor del perezoso: en ella aparece, letra a
// letra, el codigo que va tecleando. Cada pulsacion escribe un caracter. Cuando
// el bloque esta completo sale "✓ listo", se celebra y empieza otro bloque.
//
// El texto se dibuja en un <canvas> 2D (con la fuente Geist Mono de la web) que
// se usa como textura del cristal: nitido, sin cargas extra y solo se redibuja
// cuando cambia algo.

import { useEffect, useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Line } from "@react-three/drei";
import * as THREE from "three";
import { AJUSTES, C, PANTALLA_GIRO, PANTALLA_POS, PANTALLA_TAM } from "./constantes";
import { estado } from "./estado";

const CODIGO = [
  "def automatizar(flujo):",
  "  for paso in flujo.pasos:",
  "    ojo = mirar(paso)",
  "    clic(ojo.x, ojo.y)",
  "    verificar(paso)",
  '  return "ok"',
];
const CLAVES = new Set(["def", "for", "in", "return"]);
const TEXTO = "#e2e8f0";

type Token = { desde: number; hasta: number; color: string };
/** Resaltado de sintaxis sencillo: claves, funciones, textos y simbolos. */
function colorear(linea: string): Token[] {
  const tokens: Token[] = [];
  for (const m of linea.matchAll(/(\s+)|("[^"]*")|([A-Za-z_]\w*)|(.)/g)) {
    const desde = m.index ?? 0;
    const hasta = desde + m[0].length;
    let color = TEXTO;
    if (m[2]) color = C.verde;
    else if (m[3]) color = CLAVES.has(m[3]) ? C.violeta : linea[hasta] === "(" ? C.cian : TEXTO;
    else if (m[4]) color = C.rosa;
    tokens.push({ desde, hasta, color });
  }
  return tokens;
}

// cada linea: sangria (sale de golpe) + cuerpo (se teclea letra a letra)
const LINEAS = (() => {
  let cuenta = 0;
  return CODIGO.map((texto) => {
    const sangria = texto.length - texto.trimStart().length;
    const l = { texto, sangria, inicio: cuenta, largo: texto.length - sangria, tokens: colorear(texto) };
    cuenta += l.largo;
    return l;
  });
})();
const TOTAL = LINEAS.reduce((s, l) => s + l.largo, 0);

const [W, H] = PANTALLA_TAM;
// lienzo 2D (en pixeles) con la misma proporcion que la pantalla
const PX_ANCHO = 1024;
const PX_ALTO = Math.round((PX_ANCHO * H) / W);
const LETRA = 54;
const ALTO_LINEA = 80;
const CODIGO_X = 104;
const CODIGO_Y = 132;

/** pixel del lienzo -> coordenadas locales de la pantalla */
const aLocal = (px: number, py: number) => [(px / PX_ANCHO - 0.5) * W, (0.5 - py / PX_ALTO) * H] as const;

// lienzo y textura: se crean una vez (solo en el navegador) y se reutilizan
let grafico: { lienzo: HTMLCanvasElement; textura: THREE.CanvasTexture } | null = null;
function obtenerGrafico() {
  if (!grafico) {
    const lienzo = document.createElement("canvas");
    lienzo.width = PX_ANCHO;
    lienzo.height = PX_ALTO;
    const textura = new THREE.CanvasTexture(lienzo);
    textura.colorSpace = THREE.SRGBColorSpace;
    textura.anisotropy = 8;
    grafico = { lienzo, textura };
  }
  return grafico;
}

function fuenteMono() {
  const css = getComputedStyle(document.documentElement).getPropertyValue("--font-geist-mono").trim();
  return css || "ui-monospace, Consolas, monospace";
}

/** Dibuja la pantalla y devuelve donde queda el cursor (en pixeles). */
function dibujar(escritos: number, celebrando: boolean, fuente: string) {
  const { lienzo, textura } = obtenerGrafico();
  const ctx = lienzo.getContext("2d")!;
  ctx.clearRect(0, 0, PX_ANCHO, PX_ALTO);
  ctx.fillStyle = "rgba(13, 10, 31, 0.86)";
  ctx.fillRect(0, 0, PX_ANCHO, PX_ALTO);

  // barra de titulo
  [C.rosa, "#f59e0b", C.verde].forEach((c, i) => {
    ctx.beginPath();
    ctx.arc(36 + i * 30, 34, 9, 0, Math.PI * 2);
    ctx.fillStyle = c;
    ctx.fill();
  });
  ctx.textBaseline = "middle";
  ctx.textAlign = "center";
  ctx.font = `32px ${fuente}`;
  ctx.fillStyle = "#94a3b8";
  ctx.fillText("agente.py", PX_ANCHO / 2, 35);
  ctx.fillStyle = "rgba(139, 92, 246, 0.5)";
  ctx.fillRect(16, 68, PX_ANCHO - 32, 2);

  // codigo
  let cursorX = CODIGO_X;
  let cursorY = CODIGO_Y;
  LINEAS.forEach((l, i) => {
    const y = CODIGO_Y + i * ALTO_LINEA;
    ctx.textAlign = "right";
    ctx.font = `40px ${fuente}`;
    ctx.fillStyle = "#475569";
    ctx.fillText(String(i + 1), CODIGO_X - 30, y);

    const visibles = Math.max(0, Math.min(escritos - l.inicio, l.largo));
    if (visibles === 0) return;
    const limite = l.sangria + visibles;
    ctx.textAlign = "left";
    ctx.font = `${LETRA}px ${fuente}`;
    let x = CODIGO_X;
    for (const tk of l.tokens) {
      if (tk.desde >= limite) break;
      const trozo = l.texto.slice(tk.desde, Math.min(tk.hasta, limite));
      ctx.fillStyle = tk.color;
      ctx.fillText(trozo, x, y);
      x += ctx.measureText(trozo).width;
    }
    cursorX = x;
    cursorY = y;
  });

  if (celebrando) {
    ctx.textAlign = "right";
    ctx.font = `600 44px ${fuente}`;
    ctx.fillStyle = C.verde;
    ctx.shadowColor = C.verde;
    ctx.shadowBlur = 18;
    ctx.fillText("✓ listo", PX_ANCHO - 40, PX_ALTO - 46);
    ctx.shadowBlur = 0;
  }
  textura.needsUpdate = true;
  return [cursorX, cursorY] as const;
}

export default function Pantalla() {
  const cursor = useRef<THREE.Mesh>(null);
  const marco = useRef<THREE.Group>(null);
  const barrido = useRef<THREE.Mesh>(null);
  const s = useRef({ base: 0, finHasta: -1, dibujado: "", fuente: "" });

  const cristal = useRef<THREE.MeshBasicMaterial>(null);

  // cuando termine de cargar la fuente de la web, redibujar con ella
  useEffect(() => {
    document.fonts?.ready.then(() => {
      s.current.fuente = fuenteMono();
      s.current.dibujado = "";
    });
  }, []);

  const bordes = useMemo(() => {
    const p: [number, number, number][] = [[-W / 2, -H / 2, 0], [W / 2, -H / 2, 0], [W / 2, H / 2, 0], [-W / 2, H / 2, 0], [-W / 2, -H / 2, 0]];
    const col: [number, number, number][] = p.map(([x, y]) => {
      const c = new THREE.Color(C.violeta).lerp(new THREE.Color(C.cian), (x / W + y / H + 1) / 2);
      return [c.r, c.g, c.b];
    });
    return { p, col };
  }, []);

  const cursorPx = useRef<readonly [number, number]>([CODIGO_X, CODIGO_Y]);

  useFrame(({ clock }) => {
    const t = clock.elapsedTime;
    const k = estado.tecleo;
    const r = s.current;

    // tras el check, empieza un bloque nuevo
    if (r.finHasta > 0 && t > r.finHasta) {
      r.finHasta = -1;
      r.base = k.pulsaciones;
    }
    const escritos = r.finHasta > 0 ? TOTAL : Math.min(k.pulsaciones - r.base, TOTAL);
    if (escritos >= TOTAL && r.finHasta < 0) r.finHasta = t + AJUSTES.pantalla.pausaFinal;
    const celebrando = r.finHasta > 0;
    k.celebrando += ((celebrando ? 1 : 0) - k.celebrando) * 0.12;

    // redibujar solo si ha cambiado algo
    const clave = `${escritos}|${celebrando}|${r.fuente}`;
    if (clave !== r.dibujado) {
      r.dibujado = clave;
      cursorPx.current = dibujar(escritos, celebrando, r.fuente || fuenteMono());
      if (cristal.current && !cristal.current.map) {
        cristal.current.map = obtenerGrafico().textura;
        cristal.current.needsUpdate = true;
      }
    }

    // cursor parpadeante (en 3D, para que brille); los bits vuelan hasta aqui
    if (cursor.current) {
      const [x, y] = aLocal(cursorPx.current[0] + 6, cursorPx.current[1]);
      cursor.current.position.set(x, y, 0.002);
      cursor.current.visible = !celebrando && Math.sin(t * 9) > -0.2;
      cursor.current.getWorldPosition(estado.objetos.cursorPantalla);
    }
    if (marco.current) marco.current.scale.setScalar(1 + k.celebrando * 0.015);
    // linea de barrido que baja (despacio) por la pantalla
    if (barrido.current) barrido.current.position.y = H / 2 - ((t * 0.12) % 1) * H;
  });

  return (
    <group position={PANTALLA_POS} rotation={[0, PANTALLA_GIRO, 0]}>
      <mesh>
        <planeGeometry args={[W, H]} />
        <meshBasicMaterial ref={cristal} transparent depthWrite={false} toneMapped={false} />
      </mesh>
      <group ref={marco}>
        <Line points={bordes.p} vertexColors={bordes.col} lineWidth={2} transparent opacity={0.95} toneMapped={false} />
      </group>
      <mesh ref={cursor}>
        <planeGeometry args={[0.006, (LETRA * 1.15 * H) / PX_ALTO]} />
        <meshBasicMaterial color={C.cian} toneMapped={false} />
      </mesh>
      <mesh ref={barrido} position={[0, 0, 0.003]}>
        <planeGeometry args={[W, 0.01]} />
        <meshBasicMaterial color={C.cian} transparent opacity={0.05} depthWrite={false} />
      </mesh>
      <pointLight position={[0, 0, 0.3]} color={C.cian} intensity={1.5} distance={3} />
    </group>
  );
}
