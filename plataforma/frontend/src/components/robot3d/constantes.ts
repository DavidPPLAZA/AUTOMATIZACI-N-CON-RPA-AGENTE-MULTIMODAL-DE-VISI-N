// Colores, colocacion y TODOS los valores ajustables de la escena del perezoso.

export const MODELO = "/perezoso-dev.glb";

export const C = {
  violeta: "#8b5cf6",
  cian: "#22d3ee",
  rosa: "#e879f9",
  verde: "#34d399",
  cristal: "#0d0a1f", // fondo de la pantalla holografica
};

/* ------------------------------------------------------------ AJUSTES */
// Toca estos numeros para cambiar como se mueve la escena.
export const AJUSTES = {
  tecleo: {
    porSegundo: 7, // pulsaciones por segundo en reposo
    turbo: 20, // pulsaciones por segundo en modo turbo (clic / boton)
    duracionTurbo: 3, // segundos de turbo tras hacer clic en el perezoso
    destello: 0.35, // segundos que dura el destello de cada tecla
    luzPantalla: 1.2, // brillo de la luz de la pantalla sobre su cara
  },
  // el cuerpo NO reacciona a las teclas: solo respira y se balancea despacio
  cuerpo: {
    respiracion: 0.01, // la escala varia +-1%
    periodoRespiracion: 4, // segundos por respiracion
    balanceo: 0.025, // inclinacion lateral maxima (radianes)
    periodoBalanceo: 7, // segundos por balanceo
  },
  mirada: {
    giroY: 0.3, // cuanto se gira hacia el cursor (radianes)
    giroX: 0.1,
    suavizado: 0.03, // 0..1: mas alto = sigue mas rapido
    tactilCada: [1.8, 3.5] as const, // en movil mira a un sitio al azar cada X s
  },
  bits: {
    vuelo: 0.75, // segundos que tarda un bit en llegar a la pantalla
    arco: 0.35, // altura del arco que dibujan
  },
  pantalla: {
    pausaFinal: 1.6, // segundos que se ve el check verde antes de empezar otro bloque
  },
};

/* ---------------------------------------------------------- colocacion */
// Todo esta en "unidades del modelo": el perezoso (con su portatil) mide ~0.8
// de alto y esta centrado en 0; el portatil queda delante, hacia +z.
export const ESCALA = 3.5;
export const PEREZOSO_POS: [number, number, number] = [0.16, -0.1, 0];
// giro base: de tres cuartos, para ver la cara y el portatil de lado
export const PEREZOSO_GIRO = -0.6;
// la pantalla holografica: flota sobre el portatil, a la altura de su cabeza,
// girada hacia el, como si la proyectara el portatil
export const PANTALLA_POS: [number, number, number] = [-0.34, 0.2, -0.02];
export const PANTALLA_GIRO = 0.42;
export const PANTALLA_TAM: [number, number] = [0.58, 0.4];

/* -------------------------------------------------------------- portatil */
// Medido sobre el modelo (unidades del modelo, antes de girarlo).
export const PORTATIL = {
  tecladoY: -0.355, // altura de las teclas
  manos: [
    [-0.08, 0.29],
    [0.08, 0.29],
  ] as const, // [x, z] de cada garra sobre el teclado
  radioMano: 0.05, // zona de teclas que pulsa cada garra
  pantalla: [0, -0.22, 0.38] as const, // delante de la pantalla (de donde sale su luz)
  logo: { pos: [0, -0.24, 0.475] as const, giro: 0.32 }, // detras de la tapa
  suelo: { y: -0.39, centro: [0, 0.28] as const, radio: 0.32 }, // resplandor bajo el portatil
};
