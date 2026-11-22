"""Ejecuciones (de un robot, y mas adelante del agente) y su stream de eventos.

Una ejecucion corre en un hilo aparte (pyautogui bloquea) y va publicando
eventos. Cada cliente WebSocket se suscribe y recibe primero los eventos que
ya ocurrieron y despues los nuevos en tiempo real.

Solo puede haber UNA ejecucion activa: solo hay un raton y un teclado.
"""

import asyncio
import threading
import time
import uuid
from datetime import datetime


class EjecucionEnCurso(Exception):
    pass


class Ejecucion:
    def __init__(self, modo: str):
        self.id = uuid.uuid4().hex[:12]
        self.modo = modo  # "robot" | "agente"
        self.estado = "en_curso"  # "en_curso" | "ok" | "error" | "detenida"
        self.inicio = datetime.now().isoformat(timespec="seconds")
        self.eventos: list[dict] = []
        self.detener = threading.Event()
        self._t0 = time.perf_counter()
        # cada suscriptor (un WebSocket) con el bucle de eventos en el que vive su cola
        self._suscriptores: dict[asyncio.Queue, asyncio.AbstractEventLoop] = {}
        self._lock = threading.Lock()

    def emitir(self, tipo: str, **datos) -> None:
        """Publica un evento. Se puede llamar desde cualquier hilo."""
        evento = {"tipo": tipo, "t": round(time.perf_counter() - self._t0, 2), **datos}
        with self._lock:
            self.eventos.append(evento)
            colas = list(self._suscriptores.items())
        for cola, loop in colas:
            if not loop.is_closed():
                loop.call_soon_threadsafe(cola.put_nowait, evento)

    def suscribir(self) -> tuple[asyncio.Queue, list[dict]]:
        cola: asyncio.Queue = asyncio.Queue()
        with self._lock:
            self._suscriptores[cola] = asyncio.get_running_loop()
            pasados = list(self.eventos)
        return cola, pasados

    def desuscribir(self, cola: asyncio.Queue) -> None:
        with self._lock:
            self._suscriptores.pop(cola, None)

    def resumen(self) -> dict:
        return {"id": self.id, "modo": self.modo, "estado": self.estado, "inicio": self.inicio}


class Gestor:
    def __init__(self):
        self.ejecuciones: dict[str, Ejecucion] = {}
        self.activa: Ejecucion | None = None
        self._lock = threading.Lock()

    def lanzar(self, modo: str, trabajo) -> Ejecucion:
        """`trabajo(ejecucion)` corre en un hilo; si lanza una excepcion, la
        ejecucion termina con un evento de error."""
        with self._lock:
            if self.activa is not None and self.activa.estado == "en_curso":
                raise EjecucionEnCurso(self.activa.id)
            ejecucion = Ejecucion(modo)
            self.ejecuciones[ejecucion.id] = ejecucion
            self.activa = ejecucion

        def correr():
            try:
                trabajo(ejecucion)
                if ejecucion.estado == "en_curso":
                    ejecucion.estado = "ok"
            except Exception as exc:  # el error se cuenta en la web, no se pierde
                ejecucion.estado = "error"
                ejecucion.emitir("error", texto=f"{type(exc).__name__}: {exc}")
            finally:
                ejecucion.emitir("fin", estado=ejecucion.estado)

        threading.Thread(target=correr, daemon=True).start()
        return ejecucion


gestor = Gestor()
