"use client";

// El perezoso (modelo GLB, con su sudadera y su portatil). El modelo es una
// figura fija (no tiene huesos): solo respira y se balancea muy despacio, y se
// gira suavemente hacia el cursor. El tecleo lo cuentan los efectos del portatil.

import { useEffect, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { useGLTF } from "@react-three/drei";
import * as THREE from "three";
import { AJUSTES, MODELO, PEREZOSO_GIRO, PEREZOSO_POS } from "./constantes";
import { useMirada } from "./animaciones";
import { estado } from "./estado";
import Portatil from "./Portatil";

useGLTF.preload(MODELO);

export default function Perezoso({ tactil }: { tactil: boolean }) {
  const { scene } = useGLTF(MODELO);
  const cuerpo = useRef<THREE.Group>(null);
  const mirada = useMirada(tactil);
  const s = useRef({ giroY: 0, giroX: 0, destacar: 1 });

  // los bits salen de las teclas del portatil, que esta en este grupo
  useEffect(() => {
    estado.objetos.portatil = cuerpo.current;
    return () => {
      estado.objetos.portatil = null;
    };
  }, []);

  useFrame(({ clock }) => {
    const g = cuerpo.current;
    if (!g) return;
    const t = clock.elapsedTime;
    const r = s.current;
    const { cuerpo: Cu, mirada: Mi } = AJUSTES;

    // se gira despacio hacia donde mira
    const m = mirada.current;
    r.giroY += (m.x * Mi.giroY - r.giroY) * Mi.suavizado;
    r.giroX += (-m.y * Mi.giroX - r.giroX) * Mi.suavizado;

    // respiracion (+-1% de escala) y balanceo lateral lentos; nada de temblores
    const respira = 1 + Math.sin((t * 2 * Math.PI) / Cu.periodoRespiracion) * Cu.respiracion;
    const balanceo = Math.sin((t * 2 * Math.PI) / Cu.periodoBalanceo) * Cu.balanceo;
    r.destacar += ((estado.hoverPerezoso ? 1.03 : 1) - r.destacar) * 0.05;
    g.scale.setScalar(r.destacar * respira);
    g.rotation.set(r.giroX, PEREZOSO_GIRO + r.giroY, balanceo);
  });

  return (
    <group ref={cuerpo} position={PEREZOSO_POS} rotation={[0, PEREZOSO_GIRO, 0]}>
      <primitive object={scene} />
      <Portatil />
      {/* zona invisible para el cursor: hover y clic */}
      <mesh
        position={[0, 0, 0.05]}
        scale={[0.38, 0.42, 0.5]}
        onPointerOver={(ev) => {
          ev.stopPropagation();
          estado.hoverPerezoso = true;
          document.body.style.cursor = "pointer";
        }}
        onPointerOut={() => {
          estado.hoverPerezoso = false;
          document.body.style.cursor = "";
        }}
        onClick={(ev) => {
          ev.stopPropagation();
          estado.pedirTurbo = true;
        }}
      >
        <sphereGeometry args={[1, 16, 12]} />
        <meshBasicMaterial transparent opacity={0} depthWrite={false} />
      </mesh>
    </group>
  );
}
