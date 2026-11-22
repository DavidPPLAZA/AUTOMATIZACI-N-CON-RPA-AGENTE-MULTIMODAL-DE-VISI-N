"""Reproducir un flujo con RPA puro: pyautogui y coordenadas grabadas, sin
agente ni vision (por eso va mucho mas rapido)."""

import threading
import time

import pyautogui
import pyperclip

from agente import config, ventana
from agente.eventos import emitir


def _paso(v: ventana.VentanaGestCorp, paso: dict) -> None:
    ox, oy = v.origen  # coordenadas relativas a la ventana -> absolutas
    x, y = ox + paso["x"], oy + paso["y"]
    if paso["accion"] == "click":
        pyautogui.click(x, y)
        time.sleep(config.PAUSA_CLICK)
    else:  # "escribir": vaciar el campo y pegar (como borrar_campo + rellenar_campo)
        pyautogui.click(x, y)
        pyautogui.press("end")
        pyautogui.press("backspace", presses=50)
        pyperclip.copy(paso["texto"])
        pyautogui.hotkey("ctrl", "v")
        time.sleep(config.PAUSA_ESCRIBIR)


def reproducir(flujo: dict, detener: threading.Event | None = None) -> str:
    """Abre GestCorp 98 con el tamaño de la grabacion, ejecuta los pasos y la
    cierra. Devuelve "ok" o "detenida" (si `detener` se activa entre pasos)."""
    pasos = flujo["pasos"]
    emitir("mensaje", texto="Abriendo GestCorp 98…")
    v = ventana.abrir(flujo["ventana"]["ancho"], flujo["ventana"]["alto"])
    try:
        for i, paso in enumerate(pasos):
            if detener is not None and detener.is_set():
                emitir("mensaje", texto="Ejecución detenida por el usuario.")
                return "detenida"
            emitir("paso", indice=i, total=len(pasos), accion=paso["accion"],
                   elemento=paso["elemento"], texto=paso.get("texto"),
                   x=paso["x"], y=paso["y"])
            _paso(v, paso)
            emitir("paso_ok", indice=i)
        emitir("mensaje", texto=f"Robot completado: {len(pasos)} pasos.")
        return "ok"
    finally:
        time.sleep(1.5)  # que se vea el resultado antes de cerrar
        v.cerrar()
