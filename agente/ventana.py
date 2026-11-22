"""Abrir y cerrar GestCorp 98 en su mitad de la pantalla.

Como proceso aparte: `root.mainloop()` de Tkinter bloquearia a quien la abre.
"""

import ctypes
import ctypes.wintypes
import subprocess
import sys
import time

import pygetwindow as gw

from agente import config


class VentanaGestCorp:
    def __init__(self, proceso: subprocess.Popen, ventana):
        self.proceso = proceso
        self.ventana = ventana
        # copia en numeros fijos de donde quedo la ventana: `ventana` lee su
        # posicion en vivo de Windows y deja de valer en cuanto la app se
        # cierra, pero para guardar el flujo hace falta la de la grabacion
        self.rect = {"left": ventana.left, "top": ventana.top,
                     "ancho": ventana.width, "alto": ventana.height}

    @property
    def origen(self) -> tuple[int, int]:
        return self.ventana.left, self.ventana.top

    def activar(self) -> None:
        try:
            self.ventana.activate()
        except Exception:
            # pygetwindow a veces lanza aqui aunque el cambio de foco SI
            # funcione (restriccion de Windows sobre quien puede robar el foco)
            pass
        time.sleep(0.5)

    def cerrar(self) -> None:
        self.proceso.terminate()
        try:
            self.proceso.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proceso.kill()


def _area_util() -> ctypes.wintypes.RECT:
    """Zona util de la pantalla, sin la barra de tareas (SPI_GETWORKAREA)."""
    area = ctypes.wintypes.RECT()
    ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(area), 0)
    return area


def abrir(ancho: int | None = None, alto: int | None = None) -> VentanaGestCorp:
    """Lanza GestCorp 98 y la coloca en su mitad de la pantalla.

    Sin tamaño: ocupa esa mitad entera (lo que usa el agente). Con tamaño: el
    de la grabacion de un flujo, para que sus coordenadas valgan (el robot).
    """
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

    area = _area_util()
    mitad = (area.right - area.left) // 2
    x = area.left if config.LADO_GESTCORP == "izquierda" else area.left + mitad

    ventana.restore()  # arranca maximizada: hay que restaurarla para moverla
    time.sleep(0.5)
    ventana.moveTo(x, area.top)
    ventana.resizeTo(ancho or mitad, alto or (area.bottom - area.top))
    time.sleep(0.5)
    v = VentanaGestCorp(proceso, ventana)
    v.activar()
    return v
