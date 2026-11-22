"""Ejecutar un robot: reproducir un flujo RPA con pyautogui (sin IA)."""

import time

import pyautogui
import pyperclip

from plataforma.backend import config, gestcorp
from plataforma.backend.ejecuciones import Ejecucion


def _paso(ventana: gestcorp.VentanaGestCorp, paso: dict) -> None:
    ox, oy = ventana.origen
    x, y = ox + paso["x"], oy + paso["y"]
    if paso["accion"] == "click":
        pyautogui.click(x, y)
        time.sleep(config.PAUSA_CLICK)
    else:  # "escribir": vaciar el campo y pegar (como las tools del agente)
        pyautogui.click(x, y)
        pyautogui.press("end")
        pyautogui.press("backspace", presses=50)
        pyperclip.copy(paso["texto"])
        pyautogui.hotkey("ctrl", "v")
        time.sleep(config.PAUSA_ESCRIBIR)


def ejecutar(flujo: dict, ejecucion: Ejecucion) -> None:
    pasos = flujo["pasos"]
    ejecucion.emitir("inicio", modo="robot", flujo=flujo["id"], titulo=flujo["titulo"],
                     total=len(pasos))
    ejecucion.emitir("mensaje", texto="Abriendo GestCorp 98…")
    ventana = gestcorp.abrir(flujo["ventana"]["ancho"], flujo["ventana"]["alto"])
    try:
        for i, paso in enumerate(pasos):
            if ejecucion.detener.is_set():
                ejecucion.estado = "detenida"
                ejecucion.emitir("mensaje", texto="Ejecución detenida por el usuario.")
                return
            ejecucion.emitir("paso", indice=i, total=len(pasos), accion=paso["accion"],
                             elemento=paso["elemento"], texto=paso.get("texto"),
                             x=paso["x"], y=paso["y"])
            _paso(ventana, paso)
            ejecucion.emitir("paso_ok", indice=i)
        ejecucion.emitir("mensaje", texto=f"Robot completado: {len(pasos)} pasos.")
    finally:
        time.sleep(1.5)  # que se vea el resultado antes de cerrar
        ventana.cerrar()
