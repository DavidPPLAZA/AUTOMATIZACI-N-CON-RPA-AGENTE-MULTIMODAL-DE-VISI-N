"""Abrir y cerrar GestCorp 98 en su mitad de la pantalla."""

import ctypes
import ctypes.wintypes
import subprocess
import sys
import time

import pygetwindow as gw

from plataforma.backend import config


class VentanaGestCorp:
    def __init__(self, proceso: subprocess.Popen, ventana):
        self.proceso = proceso
        self.ventana = ventana

    @property
    def origen(self) -> tuple[int, int]:
        return self.ventana.left, self.ventana.top

    def cerrar(self) -> None:
        self.proceso.terminate()
        try:
            self.proceso.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proceso.kill()


def abrir(ancho: int, alto: int) -> VentanaGestCorp:
    """Lanza GestCorp 98 y la coloca en su mitad de la pantalla con el tamaño
    dado (el de la grabacion del flujo, para que las coordenadas valgan)."""
    proceso = subprocess.Popen([sys.executable, "-m", "gestcorp98.main"], cwd=config.RAIZ)
    ventana = None
    for _ in range(20):
        time.sleep(0.5)
        candidatas = gw.getWindowsWithTitle(config.TITULO_VENTANA)
        if candidatas:
            ventana = candidatas[0]
            break
    if ventana is None:
        proceso.terminate()
        raise RuntimeError(f"no encontré la ventana '{config.TITULO_VENTANA}' tras 10 s")

    # zona util de la pantalla, sin la barra de tareas (SPI_GETWORKAREA)
    area = ctypes.wintypes.RECT()
    ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(area), 0)
    mitad = (area.right - area.left) // 2
    x = area.left if config.LADO_GESTCORP == "izquierda" else area.left + mitad

    ventana.restore()  # arranca maximizada: hay que restaurarla para moverla
    time.sleep(0.5)
    ventana.moveTo(x, area.top)
    ventana.resizeTo(ancho, alto)
    time.sleep(0.5)
    try:
        ventana.activate()
    except Exception:
        pass  # pygetwindow lanza a veces aunque el foco cambie bien
    time.sleep(0.5)
    return VentanaGestCorp(proceso, ventana)
