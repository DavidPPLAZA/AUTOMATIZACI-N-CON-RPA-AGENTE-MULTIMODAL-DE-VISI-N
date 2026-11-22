# Plataforma — «Automatizando la automatización»

Web para lanzar el agente, ver en tiempo real lo que hace y ejecutar los robots (flujos
RPA) que genera.

```
plataforma/
  backend/    FastAPI + WebSocket (Python, uv)  → http://localhost:8000
  frontend/   Next.js + TypeScript + Tailwind   → http://localhost:3000
```

## Arrancar

Dos terminales:

```bash
# 1) backend, desde la raiz del repo
uv run uvicorn plataforma.backend.main:app --port 8000

# 2) frontend
cd plataforma/frontend
npm install   # solo la primera vez
npm run dev
```

Pon el navegador en la mitad izquierda de la pantalla: GestCorp 98 se abre en la derecha
(`LADO_GESTCORP` en `backend/config.py`). Mientras se ejecuta un robot, el ratón es suyo.

## Estado

- **Robots:** funcionan de verdad. Lee los flujos de `experiments/flujos/`, los reproduce con
  pyautogui y manda cada paso por WebSocket.
- **Agente:** la interfaz está montada, pero `POST /ejecuciones/agente` responde 501. El
  agente sigue en `experiments/agentic_pipeline.ipynb` hasta que esté pulido.

## Mascota 3D de la portada (el perezoso)

**De dónde sale el modelo** (`frontend/public/perezoso-dev.glb`):

1. **Imagen inicial:** generada con **ChatGPT** (versión gratuita): un perezoso con sudadera
   negra tecleando en un portátil.
2. **De imagen a 3D:** esa imagen se pasó por un **Space de Hugging Face de "image to 3D"**,
   que devuelve directamente el `.glb` con textura. <!-- TODO: anotar qué Space/modelo exacto -->

**A tener en cuenta:**

- **Es una figura fija.** El GLB es una sola malla, sin esqueleto ni animaciones. No se le
  pueden mover la cabeza ni los brazos como a un personaje "riggeado". Por eso la vida se la
  dan:
  - el cuerpo entero, que respira, se balancea despacio y se gira un poco hacia el cursor;
  - efectos alrededor: destellos bajo las garras, logo luminoso en la tapa, resplandor bajo el
    portátil, bits de luz y una pantalla holográfica con código.

  Si algún día se quisiera mover la cabeza, la vía sería deformar la malla en el shader. Se
  probó la idea y se descartó: así como está gusta.
- **Pesa ~20 MB y tiene ~370 000 vértices.** Funciona en escritorio, pero tarda en cargar y es
  pesado para móvil. Se puede comprimir (meshopt + texturas a 1024) con:
  `npx @gltf-transform/cli optimize public/perezoso-dev.glb public/perezoso.glb --compress meshopt --texture-size 1024`
  y cambiar `MODELO` en `src/components/robot3d/constantes.ts`.
- **Medidas del modelo.** Los efectos se colocan con medidas tomadas sobre este GLB concreto
  (constante `PORTATIL`: altura del teclado, posición de las garras, logo, suelo). **Si se
  cambia el modelo, hay que volver a medir.**
- **Licencias.** Antes de publicar el repo o las capturas, revisa los términos de uso de la
  imagen de ChatGPT y la licencia del modelo de Hugging Face usado para pasarla a 3D.

**Dónde tocar:** todo lo ajustable (posiciones, tiempos, brillos) está en
`frontend/src/components/robot3d/constantes.ts`. Cada pieza tiene su archivo:

| Archivo | Qué es |
|---|---|
| `Perezoso.tsx` | el modelo |
| `Portatil.tsx` | los efectos del portátil |
| `Pantalla.tsx` | la pantalla holográfica |
| `Bits.tsx` | los bits de luz |
| `animaciones.ts` | el motor de tecleo y la mirada |

## API

| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/estado` | backend vivo, agente conectado, ejecución activa |
| GET | `/prompt-ejemplo` | prompt que se precarga en el Estudio |
| GET | `/flujos`, `/flujos/{id}` | robots guardados |
| POST | `/ejecuciones/robot` `{flujo}` | ejecuta un robot (409 si ya hay una ejecución) |
| POST | `/ejecuciones/agente` `{prompt}` | lanza el agente (aún no: 501) |
| POST | `/ejecuciones/{id}/detener` | para la ejecución en el siguiente paso |
| WS | `/ws/ejecuciones/{id}` | eventos en tiempo real: `inicio`, `paso`, `paso_ok`, `mensaje`, `error`, `fin` |
