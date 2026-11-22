"use client";

// Efectos sobre el portatil que ya trae el modelo (va dentro del grupo del
// perezoso, asi que se mueve con el):
// - destellos de luz bajo las garras con cada tecla
// - la luz de la pantalla iluminandole la cara, que parpadea al teclear
// - un logo luminoso detras de la tapa
// - un resplandor de colores en el suelo, bajo el portatil
// En turbo todo brilla mas; al terminar un bloque de codigo, todo se pone verde.

import { useRef, type Ref } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { AJUSTES, C, PORTATIL } from "./constantes";
import { estado } from "./estado";

const VIOLETA = new THREE.Color(C.violeta);
const CIAN = new THREE.Color(C.cian);
const ROSA = new THREE.Color(C.rosa);
const VERDE = new THREE.Color(C.verde);
const COLORES = [CIAN, ROSA, VIOLETA];
const tmp = new THREE.Color();
const arcoiris = new THREE.Color();

// Degradado radial (blanco en el centro -> transparente) para los brillos.
// Se crea una sola vez, en el navegador, y lo comparten todos.
let degradado: THREE.CanvasTexture | null = null;
function texturaBrillo() {
  if (!degradado) {
    const c = document.createElement("canvas");
    c.width = c.height = 128;
    const ctx = c.getContext("2d")!;
    const g = ctx.createRadialGradient(64, 64, 0, 64, 64, 64);
    g.addColorStop(0, "rgba(255,255,255,1)");
    g.addColorStop(0.35, "rgba(255,255,255,0.45)");
    g.addColorStop(1, "rgba(255,255,255,0)");
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, 128, 128);
    degradado = new THREE.CanvasTexture(c);
  }
  return degradado;
}

/** Material de brillo: suma luz (aditivo), sin tapar nada de detras. */
function Brillo({ refMat, opacidad = 1 }: { refMat?: Ref<THREE.MeshBasicMaterial>; opacidad?: number }) {
  return (
    <meshBasicMaterial
      ref={refMat}
      transparent
      opacity={opacidad}
      depthWrite={false}
      blending={THREE.AdditiveBlending}
      toneMapped={false}
    />
  );
}

const DESTELLOS = 10;

export default function Portatil() {
  const destellos = useRef<(THREE.Mesh | null)[]>([]);
  const luz = useRef<THREE.PointLight>(null);
  const logo = useRef<THREE.MeshBasicMaterial>(null);
  const halo = useRef<THREE.MeshBasicMaterial>(null);
  const suelo = useRef<THREE.MeshBasicMaterial>(null);
  const s = useRef({
    vistas: 0,
    sig: 0,
    flash: 0,
    nacidos: Array.from({ length: DESTELLOS }, () => -10),
    listo: false,
  });

  useFrame(({ clock }) => {
    const t = clock.elapsedTime;
    const k = estado.tecleo;
    const r = s.current;
    const T = AJUSTES.tecleo;

    // la textura de brillo se pone una vez (no se puede crear durante el render)
    if (!r.listo) {
      const tex = texturaBrillo();
      const mats = [logo.current, halo.current, suelo.current, ...destellos.current.map((d) => d?.material as THREE.MeshBasicMaterial | undefined)];
      for (const m of mats) {
        if (!m) continue;
        m.map = tex;
        m.needsUpdate = true;
      }
      r.listo = true;
    }

    // nueva tecla -> nuevo destello donde se ha pulsado
    if (k.pulsaciones !== r.vistas) {
      r.vistas = k.pulsaciones;
      const d = destellos.current[r.sig];
      if (d) {
        d.position.set(k.punto.x, PORTATIL.tecladoY + 0.004, k.punto.z);
        (d.material as THREE.MeshBasicMaterial).color.copy(COLORES[r.sig % 3]);
        r.nacidos[r.sig] = t;
      }
      r.sig = (r.sig + 1) % DESTELLOS;
      r.flash = 1;
    }
    r.flash *= 0.85;

    destellos.current.forEach((d, i) => {
      if (!d) return;
      const p = (t - r.nacidos[i]) / T.destello;
      d.visible = p >= 0 && p < 1;
      if (!d.visible) return;
      d.scale.setScalar(0.02 + p * 0.06 * (1 + k.turbo * 0.6));
      (d.material as THREE.MeshBasicMaterial).opacity = (1 - p) * (0.9 + k.turbo * 0.4);
    });

    // color comun: ola violeta <-> cian, arcoiris en turbo, verde al celebrar
    const ola = 0.5 + 0.5 * Math.sin(t * 1.3);
    tmp.copy(VIOLETA).lerp(CIAN, ola);
    if (k.turbo > 0.01) tmp.lerp(arcoiris.setHSL((t * 0.5) % 1, 0.85, 0.6), k.turbo);
    tmp.lerp(VERDE, k.celebrando);

    // la luz de la pantalla sobre su cara: parpadea un poco con cada tecla
    if (luz.current) {
      luz.current.color.copy(tmp).lerp(CIAN, 0.4);
      luz.current.intensity = T.luzPantalla * (1 + r.flash * 0.6 + k.turbo * 0.8 + k.celebrando * 0.5);
    }
    // logo de la tapa
    if (logo.current) {
      logo.current.color.copy(tmp);
      logo.current.opacity = 0.85 + r.flash * 0.15;
    }
    if (halo.current) {
      halo.current.color.copy(tmp);
      halo.current.opacity = 0.35 + 0.15 * Math.sin(t * 2.4) + r.flash * 0.2 + k.turbo * 0.3;
    }
    // resplandor en el suelo
    if (suelo.current) {
      suelo.current.color.copy(tmp);
      suelo.current.opacity = 0.45 + 0.1 * Math.sin(t * 1.7) + k.turbo * 0.35 + k.celebrando * 0.3;
    }
  });

  const { logo: L, suelo: S, pantalla: P } = PORTATIL;
  return (
    <group>
      {/* destellos bajo las garras */}
      {Array.from({ length: DESTELLOS }, (_, i) => (
        <mesh
          key={i}
          ref={(m) => {
            destellos.current[i] = m;
          }}
          rotation={[-Math.PI / 2, 0, 0]}
          visible={false}
        >
          <planeGeometry args={[1, 1]} />
          <Brillo />
        </mesh>
      ))}

      {/* luz de la pantalla, delante de ella, iluminando la cara y las garras */}
      <pointLight ref={luz} position={[P[0], P[1], P[2]]} distance={2.6} decay={2} intensity={AJUSTES.tecleo.luzPantalla} color={C.cian} />

      {/* logo luminoso detras de la tapa */}
      <group position={[L.pos[0], L.pos[1], L.pos[2]]} rotation={[L.giro, 0, 0]}>
        <mesh>
          <planeGeometry args={[0.07, 0.07]} />
          <Brillo refMat={logo} />
        </mesh>
        <mesh position={[0, 0, -0.001]}>
          <planeGeometry args={[0.26, 0.26]} />
          <Brillo refMat={halo} opacidad={0.4} />
        </mesh>
      </group>

      {/* resplandor bajo el portatil */}
      <mesh position={[S.centro[0], S.y, S.centro[1]]} rotation={[-Math.PI / 2, 0, 0]} scale={[1.5, 1, 1]}>
        <planeGeometry args={[S.radio * 2, S.radio * 2]} />
        <Brillo refMat={suelo} opacidad={0.5} />
      </mesh>
    </group>
  );
}
