// Animaciones de la escena, separadas para poder ajustarlas sin tocar los modelos.
// Los valores vienen de AJUSTES en constantes.ts.
import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { AJUSTES, PORTATIL } from "./constantes";
import { estado } from "./estado";

export const azar = (a: number, b: number) => a + Math.random() * (b - a);
export const limitar = (v: number, a = -1, b = 1) => Math.min(b, Math.max(a, v));

/** Motor de tecleo: decide cuando se pulsa una tecla y cual. Las manos se
 *  alternan casi siempre (izquierda, derecha...) como al escribir de verdad.
 *  Todo lo demas (destellos, luz, bits, pantalla) reacciona a `estado.tecleo`. */
export function useMotorTecleo() {
  const s = useRef({ siguiente: 0.6, turboHasta: 0 });
  useFrame(({ clock }) => {
    const t = clock.elapsedTime;
    const T = AJUSTES.tecleo;
    const k = estado.tecleo;
    const r = s.current;

    if (estado.pedirTurbo) {
      estado.pedirTurbo = false;
      r.turboHasta = t + T.duracionTurbo;
    }
    const enTurbo = t < r.turboHasta || estado.botonTurbo;
    k.turbo += ((enTurbo ? 1 : 0) - k.turbo) * 0.08;

    // mientras la pantalla celebra, las manos descansan
    if (k.celebrando > 0.5) {
      r.siguiente = t + 0.3;
      return;
    }
    // si el ordenador va lento (pocos fotogramas), se recuperan las pulsaciones atrasadas
    for (let n = 0; n < 3 && t >= r.siguiente; n++) {
      const ritmo = T.porSegundo + (T.turbo - T.porSegundo) * k.turbo;
      r.siguiente += azar(0.55, 1.45) / ritmo;
      const lado: -1 | 1 = Math.random() < 0.8 ? (k.lado === 1 ? -1 : 1) : k.lado;
      // un punto al azar bajo la garra que toca
      const [mx, mz] = PORTATIL.manos[lado === -1 ? 0 : 1];
      const a = Math.random() * Math.PI * 2;
      const d = Math.sqrt(Math.random()) * PORTATIL.radioMano;
      k.punto.x = mx + Math.cos(a) * d;
      k.punto.z = mz + Math.sin(a) * d * 0.6;
      k.lado = lado;
      k.pulsaciones++;
    }
    if (t > r.siguiente + 1) r.siguiente = t; // no acumular retraso infinito (pestaña en segundo plano)
  });
}

/** A donde quiere mirar el perezoso, de -1 a 1 en x/y.
 *  Con raton: el cursor, en cualquier parte de la pagina.
 *  En tactil (o si aun no se ha movido el raton): un punto al azar cada pocos segundos. */
export function useMirada(tactil: boolean) {
  const s = useRef({ x: 0, y: 0, cambio: 0 });
  useFrame(({ clock, gl }) => {
    const r = s.current;
    if (tactil || !estado.puntero.hay) {
      if (clock.elapsedTime > r.cambio) {
        r.x = azar(-0.7, 0.7);
        r.y = azar(-0.4, 0.5);
        r.cambio = clock.elapsedTime + azar(...AJUSTES.mirada.tactilCada);
      }
      return;
    }
    const rect = gl.domElement.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height * 0.4; // a la altura de la cabeza
    r.x = limitar((estado.puntero.x - cx) / (rect.width * 0.6));
    r.y = limitar(-(estado.puntero.y - cy) / (rect.height * 0.6));
  });
  return s;
}
