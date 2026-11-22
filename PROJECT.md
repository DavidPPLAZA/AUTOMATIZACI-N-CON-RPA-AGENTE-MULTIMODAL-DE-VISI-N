# Plataforma Agéntica de Automatización (RPA + Visión)

## Objetivo final

Una **plataforma a la que le explicas, en lenguaje natural (texto o audio), el flujo que
quieres automatizar** en una aplicación cualquiera — "quiero automatizar el alta de cliente
en mi ERP: entra aquí, haz login, rellena este campo, pulsa aquí, comprueba esto, y al
final dame un informe de lo que has visto" — y por debajo:

1. Un agente **entiende esa explicación** y la descompone en pasos concretos (acción,
   elemento objetivo, qué comprobar).
2. Un agente con **herramientas de visión** (el mejor enfoque de localización de elementos
   de UI que salga de `experiments/`) sabe encontrar esos elementos en pantalla, sea cual
   sea la aplicación.
3. Un agente **escribe el código RPA** que ejecuta cada paso, lo **ejecuta de verdad**, se
   **autoverifica** con el agente de visión y, si falla, **se autocorrige** iterando sobre
   su propio código.
4. El resultado es un **ejecutable reutilizable** de esa automatización, más el informe que
   el usuario pidió, y una plataforma donde gestionar todas las automatizaciones generadas
   (lanzarlas, revisar su historial, corregirlas).

En corto: **una plataforma agéntica de visión + RPA con la que automatizas la propia tarea
de automatizar** — no es un bot fijo para una app concreta, es la fábrica que construye esos
bots a partir de una explicación en lenguaje natural.

## Piezas

1. **GestCorp 98** — app legacy en Tkinter con aspecto de los años 90. Es el **banco de
   pruebas**: el primer caso real sobre el que validar todo el pipeline (puntos 2-4) antes
   de generalizarlo a otras apps. No es el objetivo final, es el conejillo de indias.
2. **Agente de visión (grounding)** — localizar cualquier elemento de una UI (botón, campo
   de texto vacío, icono) a partir de su descripción, de forma fiable y barata. Es lo que se
   está decidiendo en `experiments/`: comparando qwen2.5vl, RapidOCR, OmniParser
   (detector YOLOv8 + captioner), y como alternativas más pesadas Molmo / UI-TARS / ShowUI.
   El hallazgo hasta ahora: el detector de OmniParser localiza cajas muy precisas (incluso en
   campos vacíos), y el cuello de botella real es *identificar qué caja es cuál* — ahí
   RapidOCR (emparejar cada caja con el texto más cercano) pinta mejor que el captioner de
   Florence-2.
3. **Intérprete de flujos en lenguaje natural** — recibe la explicación del usuario (texto,
   o audio transcrito) y la convierte en una lista estructurada de pasos: qué acción, sobre
   qué elemento (descrito en lenguaje natural, para que lo resuelva la pieza 2), y qué
   verificar después.
4. **Agente generador y verificador de código RPA** — por cada paso, genera el código
   (`pyautogui` + el agente de visión de la pieza 2), lo ejecuta, verifica el resultado
   (de nuevo con visión), y si falla diagnostica y corrige su propio código hasta que el
   flujo completo funciona de forma robusta. Al final empaqueta un ejecutable reutilizable.
5. **Plataforma / web de gestión** — subir la explicación de un flujo (texto o audio), ver
   en directo cómo se genera y verifica la automatización, lanzar y gestionar las
   automatizaciones ya generadas, y consultar los informes que cada ejecución produce.

## Stack

Python 3.12 (gestionado por `uv`), Tkinter (banco de pruebas), `pyautogui`, `mss`, OCR
(RapidOCR), modelos de visión/grounding (Ollama / Hugging Face — en evaluación en
`experiments/`), LangGraph, transcripción de audio (a decidir), FastAPI. Desarrollo en
Windows. Esta lista crecerá a medida que se construyan las piezas 3 y 4.

## Hoja de ruta (commits pequeños, Conventional Commits)

### Fase 1 — GestCorp 98 (banco de pruebas)

- [x] `chore:` inicializar proyecto con `uv`, `pyproject.toml`, `.gitignore`
- [x] `docs:` añadir `PROJECT.md` y `CLAUDE.md`
- [x] `feat:` capa de datos SQLite (esquema `clientes` / `pedidos` / `facturas`) + seed de
      datos de prueba
- [x] `feat:` ventana de login de GestCorp 98
- [x] `feat:` ventana principal con `Notebook` y las 4 pestañas
- [x] `feat:` pestaña Clientes (listar + alta + borrar con clic derecho)
- [x] `feat:` pestaña Pedidos (listar + crear pedido + borrar con clic derecho)
- [x] `feat:` pestaña Facturación (listado, solo lectura por ahora)
- [x] `feat:` pestaña Informes (mostrar un dato calculado, p. ej. total de ventas)

> Hueco reservado para más adelante: paquete `gestcorp98/chaos/` con un "modo caos" para
> poner a prueba la robustez del pipeline de automatización. No se crea nada todavía.

### Fase 2 — Agente de visión / grounding (HECHA: UI-TARS, en `experiments/`)

- [x] Evaluar qwen2.5vl:7b (Ollama) sobre los 3 enfoques de prompt — descartado: ancla su
      propio formato de coordenadas y no responde fiable a instrucciones de unidad
- [x] Evaluar RapidOCR — buen baseline para botones, insuficiente solo para campos vacíos
- [x] Evaluar el detector YOLOv8 de OmniParser — cajas muy precisas, incluso en vacíos
- [x] Evaluar UI-TARS-7B-DPO — **elegido**: localiza muy bien (coordenadas en escala 0-1000
      sobre la imagen original) y además responde preguntas sobre la pantalla, lo que sirve
      para verificar
- [ ] ~~Combinar detector de OmniParser + RapidOCR~~ — no hizo falta tras UI-TARS
- [x] Extraer el enfoque ganador como herramienta reutilizable: `experiments/vision_tools.py`
      (localizar, preguntar, captura limitada a la ventana, siempre en GPU)

### Fase 3 — Intérprete de flujos en lenguaje natural (PROTOTIPO en `experiments/agentic_pipeline.ipynb`)

> Hoy el propio agente orquestador (gpt-oss-120b en Groq + tools) interpreta la instrucción en
> texto y la ejecuta paso a paso; no hay todavía una fase separada que la convierta en una lista
> de pasos editable. Lo aprendido está en
> [`docs/aprendizajes-agente-rpa.md`](./docs/aprendizajes-agente-rpa.md).

- [ ] Transcripción de audio a texto (si el input es audio)
- [ ] Parseo de la explicación en lenguaje natural a una lista estructurada de pasos
      (acción, descripción del elemento objetivo, verificación esperada)
- [ ] Validación/edición de esos pasos por el usuario antes de generar código

### Fase 4 — Agente generador y verificador de código RPA (PROTOTIPO en `experiments/agentic_pipeline.ipynb`)

> Conseguido el 2026-11-22: el agente ejecuta el flujo completo (login → alta de cliente →
> pedido con desplegables) con tools deterministas, **verifica cada formulario** (UI-TARS lee,
> Python compara) y se autocorrige; de su grabación sale un flujo JSON
> (`experiments/flujos/`) que se reproduce con RPA puro, sin IA. Falta lo de abajo.

- [ ] Grafo LangGraph: por paso, generar código → ejecutar → verificar con el agente de
      visión (fase 2) → si falla, diagnosticar y corregir el propio código → reintentar
- [ ] Capas de recuperación dentro de cada paso: caché de coordenadas conocidas → agente de
      visión → pedir ayuda al humano si ninguna capa funciona
- [ ] Aprendizaje: guardar la solución encontrada como "skill" reutilizable
- [ ] Empaquetar el flujo verificado como ejecutable reutilizable + generación del informe
      pedido por el usuario

### Fase 5 — Plataforma / web de gestión (V1 en `plataforma/`: FastAPI + Next.js)

> Hecho: la web lista los robots grabados y los ejecuta en directo (WebSocket). Falta conectar el
> agente (hoy vive en el notebook).

- [x] Backend FastAPI + WebSocket (ejecución de robots en directo)
- [ ] Subir una explicación de flujo (texto o audio) y lanzar el agente desde la web
- [ ] Streaming en directo de la generación/verificación del flujo (pantalla + clics + pasos)
- [ ] Aprobar/rechazar pasos o código generado desde la web
- [ ] Gestión de automatizaciones ya generadas: lanzar, ver historial, ver informes
- [ ] Panel de "modo caos" (conectado al hueco reservado en `gestcorp98/chaos/`) para probar
      la robustez del pipeline

## Reglas de trabajo

Ver [`CLAUDE.md`](./CLAUDE.md).
