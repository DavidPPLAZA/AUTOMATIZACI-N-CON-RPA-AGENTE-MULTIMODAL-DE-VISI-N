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
