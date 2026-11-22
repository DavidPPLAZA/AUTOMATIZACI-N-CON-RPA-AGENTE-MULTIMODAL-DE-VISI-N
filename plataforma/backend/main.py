"""API de la plataforma: lanzar el agente y los robots, y stream de eventos en
tiempo real. Todo lo que mueve GestCorp 98 vive en el paquete `agente`; aqui
solo se lanza en un hilo y se reenvia lo que cuenta a la web.

Arrancar (desde la raiz del repo):
    uv run uvicorn plataforma.backend.main:app --port 8000
"""

# importar `agente` lo primero: al importarse fija el "DPI awareness" de
# Windows, que tiene que ir antes de que nadie use pyautogui/mss
from agente import eventos, reproductor, sesion

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from plataforma.backend import config, flujos
from plataforma.backend.ejecuciones import Ejecucion, EjecucionEnCurso, gestor

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
        "agente_conectado": True,
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


@app.delete("/flujos/{id_flujo}")
def borrar_flujo(id_flujo: str):
    try:
        flujos.borrar(id_flujo)
    except FileNotFoundError:
        raise HTTPException(404, "No existe ese robot")
    return {"ok": True}


def _lanzar(modo: str, trabajo) -> dict:
    """Lanza `trabajo(ejecucion)` en un hilo con los eventos del paquete
    `agente` redirigidos a esa ejecucion (y de ahi al WebSocket)."""

    def con_eventos(ejecucion: Ejecucion) -> None:
        eventos.fijar_emisor(ejecucion.emitir)
        try:
            trabajo(ejecucion)
        finally:
            eventos.fijar_emisor(eventos.imprimir)

    try:
        return gestor.lanzar(modo, con_eventos).resumen()
    except EjecucionEnCurso:
        raise HTTPException(409, "Ya hay una ejecución en marcha: solo hay un ratón.")


class PeticionRobot(BaseModel):
    flujo: str


@app.post("/ejecuciones/robot")
def ejecutar_robot(peticion: PeticionRobot):
    try:
        flujo = flujos.cargar(peticion.flujo)
    except FileNotFoundError:
        raise HTTPException(404, "No existe ese robot")

    def trabajo(ejecucion: Ejecucion) -> None:
        ejecucion.emitir("inicio", modo="robot", titulo=flujo["titulo"], total=len(flujo["pasos"]))
        if reproductor.reproducir(flujo, ejecucion.detener) == "detenida":
            ejecucion.estado = "detenida"

    return _lanzar("robot", trabajo)


class PeticionAgente(BaseModel):
    prompt: str


@app.post("/ejecuciones/agente")
def ejecutar_agente(peticion: PeticionAgente):
    prompt = peticion.prompt.strip()
    if not prompt:
        raise HTTPException(422, "El prompt está vacío.")

    def trabajo(ejecucion: Ejecucion) -> None:
        ejecucion.emitir("inicio", modo="agente")
        resultado = sesion.ejecutar_agente(prompt, ejecucion.detener)
        if resultado["detenido"]:
            ejecucion.estado = "detenida"
        elif not resultado["completado"]:
            ejecucion.estado = "error"

    return _lanzar("agente", trabajo)


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
