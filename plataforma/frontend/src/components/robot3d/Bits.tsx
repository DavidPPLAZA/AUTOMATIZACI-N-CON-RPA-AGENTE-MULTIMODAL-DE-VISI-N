"use client";

// Por cada tecla pulsada sale un "bit" de luz que vuela en arco desde la tecla
// del portatil hasta el cursor de la pantalla: asi se ve que lo que teclea acaba en el codigo.

import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { AJUSTES, C, PORTATIL } from "./constantes";
import { estado } from "./estado";

const MAX = 28; // bits a la vez como maximo
const COLORES = [C.cian, C.rosa, C.violeta, C.cian];

type Bit = { vivo: boolean; t0: number; desde: THREE.Vector3; control: THREE.Vector3; giro: number };

const destino = new THREE.Vector3();
const a = new THREE.Vector3();
const b = new THREE.Vector3();

export default function Bits() {
  const grupo = useRef<THREE.Group>(null);
  const mallas = useRef<(THREE.Mesh | null)[]>([]);
  const s = useRef({
    vistas: 0,
    sig: 0,
    bits: Array.from({ length: MAX }, (): Bit => ({ vivo: false, t0: 0, desde: new THREE.Vector3(), control: new THREE.Vector3(), giro: 0 })),
  });

  useFrame(({ clock }) => {
    const g = grupo.current;
    const portatil = estado.objetos.portatil;
    if (!g || !portatil) return;
    const t = clock.elapsedTime;
    const r = s.current;
    const k = estado.tecleo;
    const B = AJUSTES.bits;

    // destino: el cursor de la pantalla, pasado a las coordenadas de este grupo
    g.worldToLocal(destino.copy(estado.objetos.cursorPantalla));

    // nueva tecla -> nuevo bit desde esa tecla
    if (k.pulsaciones !== r.vistas) {
      r.vistas = k.pulsaciones;
      {
        const bit = r.bits[r.sig];
        r.sig = (r.sig + 1) % MAX;
        bit.vivo = true;
        bit.t0 = t;
        bit.giro = Math.random() * Math.PI;
        g.worldToLocal(portatil.localToWorld(bit.desde.set(k.punto.x, PORTATIL.tecladoY + 0.03, k.punto.z)));
        bit.control.copy(bit.desde).lerp(destino, 0.5);
        bit.control.y += B.arco + Math.random() * 0.15;
        bit.control.z += 0.1;
      }
    }

    r.bits.forEach((bit, i) => {
      const m = mallas.current[i];
      if (!m) return;
      const p = (t - bit.t0) / B.vuelo;
      if (!bit.vivo || p >= 1) {
        bit.vivo = false;
        m.visible = false;
        return;
      }
      m.visible = true;
      // curva de Bezier: desde -> control -> destino (el destino se mueve con la pantalla)
      const e = 1 - Math.pow(1 - p, 2);
      a.copy(bit.desde).lerp(bit.control, e);
      b.copy(bit.control).lerp(destino, e);
      m.position.copy(a.lerp(b, e));
      m.rotation.set(bit.giro + t * 4, bit.giro + t * 3, 0);
      m.scale.setScalar(Math.sin(Math.min(p * 4, 1) * Math.PI * 0.5) * (1 - p * 0.6));
    });
  });

  return (
    <group ref={grupo}>
      {Array.from({ length: MAX }, (_, i) => (
        <mesh
          key={i}
          ref={(m) => {
            mallas.current[i] = m;
          }}
          visible={false}
        >
          <boxGeometry args={[0.022, 0.022, 0.022]} />
          <meshStandardMaterial color={COLORES[i % 4]} emissive={COLORES[i % 4]} emissiveIntensity={5} toneMapped={false} />
        </mesh>
      ))}
    </group>
  );
}
