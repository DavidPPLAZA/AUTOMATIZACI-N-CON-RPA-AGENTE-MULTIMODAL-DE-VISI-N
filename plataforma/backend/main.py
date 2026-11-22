"""API de la plataforma: robots, ejecuciones y stream de eventos en tiempo real.

Arrancar (desde la raiz del repo):
    uv run uvicorn plataforma.backend.main:app --port 8000
"""

import ctypes

# Igual que en el notebook: sin "DPI aware", las coordenadas de pyautogui no
# coinciden con los pixeles reales. Tiene que ir antes de importar pyautogui.
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from plataforma.backend import config, flujos, robot  # noqa: E402
from plataforma.backend.ejecuciones import EjecucionEnCurso, gestor  # noqa: E402

app = FastAPI(title="Automatizando la automatización")
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ORIGENES_PERMITIDOS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/estado")
def estado():
    activa = gestor.activa
    return {
        "ok": True,
        "agente_conectado": False,
        "ejecucion_activa": activa.resumen() if activa and activa.estado == "en_curso" else None,
    }


@app.get("/prompt-ejemplo")
def prompt_ejemplo():
    try:
        return {"prompt": config.PROMPT_EJEMPLO.read_text(encoding="utf-8").strip()}
    except FileNotFoundError:
        return {"prompt": ""}


@app.get("/flujos")
def listar_flujos():
    return flujos.listar()


@app.get("/flujos/{id_flujo}")
def ver_flujo(id_flujo: str):
    try:
        return flujos.cargar(id_flujo)
    except FileNotFoundError:
        raise HTTPException(404, "No existe ese robot")


class PeticionRobot(BaseModel):
    flujo: str


@app.post("/ejecuciones/robot")
def ejecutar_robot(peticion: PeticionRobot):
    try:
        flujo = flujos.cargar(peticion.flujo)
    except FileNotFoundError:
        raise HTTPException(404, "No existe ese robot")
    try:
        ejecucion = gestor.lanzar("robot", lambda e: robot.ejecutar(flujo, e))
    except EjecucionEnCurso:
        raise HTTPException(409, "Ya hay una ejecución en marcha: solo hay un ratón.")
    return ejecucion.resumen()


class PeticionAgente(BaseModel):
    prompt: str


@app.post("/ejecuciones/agente")
def ejecutar_agente(peticion: PeticionAgente):
    # el agente sigue en el notebook de experimentos; se enchufa aqui cuando este listo
    raise HTTPException(
        501,
        "El agente todavía no está conectado a la plataforma: de momento vive en el "
        "notebook de experimentos.",
    )


@app.post("/ejecuciones/{id_ejecucion}/detener")
def detener(id_ejecucion: str):
    ejecucion = gestor.ejecuciones.get(id_ejecucion)
    if ejecucion is None:
        raise HTTPException(404, "No existe esa ejecución")
    ejecucion.detener.set()
    return ejecucion.resumen()


@app.websocket("/ws/ejecuciones/{id_ejecucion}")
async def stream_ejecucion(websocket: WebSocket, id_ejecucion: str):
    ejecucion = gestor.ejecuciones.get(id_ejecucion)
    await websocket.accept()
    if ejecucion is None:
        await websocket.send_json({"tipo": "error", "texto": "No existe esa ejecución"})
        await websocket.close()
        return
    cola, pasados = ejecucion.suscribir()
    try:
        for evento in pasados:  # lo que ya paso, por si la web se conecta tarde
            await websocket.send_json(evento)
        if pasados and pasados[-1]["tipo"] == "fin":
            return
        while True:
            evento = await cola.get()
            await websocket.send_json(evento)
            if evento["tipo"] == "fin":
                return
    except WebSocketDisconnect:
        pass
    finally:
        ejecucion.desuscribir(cola)
        try:
            await websocket.close()
        except RuntimeError:
            pass  # ya estaba cerrado
