"""Una ejecucion completa del agente, de principio a fin (lo que hacia el
notebook): cargar UI-TARS, abrir GestCorp 98, ejecutar la instruccion, grabar
el robot y cerrar la app.

La usan la plataforma web (`plataforma/backend/main.py`) y la terminal
(`python -m agente`). Lo que va pasando se cuenta con `eventos.emitir`.
"""

import threading
import time
from pathlib import Path

from agente import grabacion, orquestador, ventana, vision
from agente.eventos import emitir


def ejecutar_agente(instruccion: str, detener: threading.Event | None = None) -> dict:
    """Devuelve {"completado": bool, "detenido": bool, "flujo": ruta del robot
    guardado o None}."""
    # UI-TARS tarda en cargar: mejor antes de abrir la app que en mitad del
    # flujo. Solo la primera vez; despues ya esta en memoria.
    emitir("mensaje", texto="Cargando UI-TARS en la GPU…")
    t0 = time.perf_counter()
    vision.precargar_modelo_vision()
    emitir("mensaje", texto=f"UI-TARS listo ({time.perf_counter() - t0:.1f} s).")

    emitir("mensaje", texto="Abriendo GestCorp 98…")
    v = ventana.abrir()
    try:
        # que UI-TARS vea solo la app, no lo que haya en la otra mitad
        r = v.rect
        vision.fijar_region_captura(r["left"], r["top"], r["ancho"], r["alto"])

        resultado = orquestador.ejecutar(instruccion, detener)
        ruta: Path | None = None
        if resultado["completado"]:
            ruta = grabacion.guardar_flujo(resultado["mensajes"], instruccion, r)
            emitir("robot_guardado", id=ruta.stem)
        elif not resultado["detenido"]:
            emitir("mensaje", texto="El agente no completó el objetivo: no se guarda el robot.")
        return {"completado": resultado["completado"], "detenido": resultado["detenido"],
                "flujo": ruta}
    finally:
        time.sleep(1)  # que se vea el resultado de la ultima accion
        v.cerrar()
