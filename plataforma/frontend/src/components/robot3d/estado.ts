// Estado que comparten la pagina (HTML) y la escena 3D. Es un objeto mutable
// normal: la escena lo lee en cada fotograma, asi que no provoca renders de React.
import * as THREE from "three";

export const estado = {
  // posicion del cursor en la pagina (px); `hay` = ya se ha movido alguna vez
  puntero: { x: 0, y: 0, hay: false },
  // el cursor esta encima del boton "Crear automatizacion" -> turbo
  botonTurbo: false,
  // el cursor esta encima del perezoso
  hoverPerezoso: false,
  // alguien ha hecho clic en el perezoso: la escena lo convierte en turbo
  pedirTurbo: false,

  // ---- lo que escribe el motor de tecleo y leen las piezas de la escena
  tecleo: {
    pulsaciones: 0, // contador total de teclas pulsadas
    punto: { x: 0, z: 0 }, // donde se ha pulsado (sobre el teclado del portatil)
    lado: 1 as -1 | 1, // mano que ha pulsado
    turbo: 0, // 0..1, suavizado
    celebrando: 0, // 0..1 mientras la pantalla muestra el check
  },
  // posiciones en coordenadas de la escena, para que los bits sepan a donde volar
  objetos: {
    portatil: null as THREE.Object3D | null, // el grupo del modelo: los bits salen de aqui
    cursorPantalla: new THREE.Vector3(),
  },
};

export function seguirPuntero() {
  const mover = (e: PointerEvent) => {
    estado.puntero.x = e.clientX;
    estado.puntero.y = e.clientY;
    estado.puntero.hay = true;
  };
  window.addEventListener("pointermove", mover, { passive: true });
  return () => window.removeEventListener("pointermove", mover);
}
