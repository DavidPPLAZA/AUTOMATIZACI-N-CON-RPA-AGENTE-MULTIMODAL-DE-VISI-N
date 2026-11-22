"use client";

// Escena de la portada: el perezoso teclea en su portatil; cada tecla enciende
// un destello bajo sus garras y lanza un bit de luz a la pantalla holografica,
// donde va apareciendo el codigo. Al completar el bloque, todo se celebra en verde.

import { Suspense, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Environment, Float, Lightformer, Sparkles } from "@react-three/drei";
import * as THREE from "three";
import { C, ESCALA } from "./constantes";
import { useMotorTecleo } from "./animaciones";
import { estado } from "./estado";
import Perezoso from "./Perezoso";
import Pantalla from "./Pantalla";
import Bits from "./Bits";

/** Decide las pulsaciones (va primero para que todos lean el mismo fotograma). */
function Motor() {
  useMotorTecleo();
  return null;
}

/** Chispas extra mientras hay turbo o celebracion. */
function Chispas() {
  const turbo = useRef<THREE.Group>(null);
  const fiesta = useRef<THREE.Group>(null);
  useFrame(() => {
    if (turbo.current) turbo.current.visible = estado.tecleo.turbo > 0.2;
    if (fiesta.current) fiesta.current.visible = estado.tecleo.celebrando > 0.2;
  });
  return (
    <>
      <group ref={turbo} visible={false}>
        <Sparkles count={40} scale={[4, 2.5, 2]} position={[-0.6, -0.6, 1]} size={4} speed={1.6} color={C.rosa} />
        <Sparkles count={40} scale={[4, 2.5, 2]} position={[-0.6, -0.6, 1]} size={4} speed={1.6} color={C.cian} />
      </group>
      <group ref={fiesta} visible={false}>
        <Sparkles count={50} scale={[5, 4, 2]} position={[0.4, 0.2, 0.6]} size={5} speed={1.2} color={C.verde} />
      </group>
    </>
  );
}

export default function Escena({ quieto = false, tactil = false }: { quieto?: boolean; tactil?: boolean }) {
  return (
    <Canvas
      camera={{ position: [0, 0.15, 8.4], fov: 40 }}
      dpr={[1, 2]}
      gl={{ antialias: true, alpha: true }}
      // con "reducir movimiento" se dibuja una sola vez: sin bucles
      frameloop={quieto ? "demand" : "always"}
    >
      <Motor />
      <ambientLight intensity={0.7} />
      <directionalLight position={[2, 4, 5]} intensity={1.8} />
      <pointLight position={[-4, 1, 3]} intensity={16} color={C.violeta} />
      <pointLight position={[4, -1, 3]} intensity={12} color={C.cian} />

      {/* reflejos de los materiales brillantes, sin descargar ningun HDR */}
      <Environment resolution={256} frames={1}>
        <Lightformer intensity={2.2} position={[0, 4, 4]} rotation={[Math.PI / 3, 0, 0]} scale={[8, 2, 1]} />
        <Lightformer intensity={3} position={[-5, 1, 1]} rotation={[0, Math.PI / 2, 0]} scale={[2, 6, 1]} color={C.violeta} />
        <Lightformer intensity={3} position={[5, 0, 1]} rotation={[0, -Math.PI / 2, 0]} scale={[2, 6, 1]} color={C.cian} />
      </Environment>

      <Suspense fallback={null}>
        <Float speed={0.8} rotationIntensity={0.03} floatIntensity={0.25}>
          <group scale={ESCALA}>
            <Perezoso tactil={tactil} />
            <Pantalla />
            <Bits />
          </group>
        </Float>
      </Suspense>

      <Chispas />
      <Sparkles count={40} scale={[8, 6, 4]} size={1.6} speed={0.25} color={C.violeta} opacity={0.6} />
    </Canvas>
  );
}
