"""Tools de accion del agente.

Cada tool hace POR DENTRO, de forma determinista, todo lo que antes eran
varios pasos del agente (localizar con UI-TARS -> clic -> escribir). La
descripcion de QUE buscar y DONDE la escribe el agente (sale del user prompt,
que es lo que cambia de una app a otra); el codigo solo localiza y actua.

Todas devuelven un JSON con:
  "resultado": texto para el agente
  "acciones":  lo que se hizo fisicamente, con coordenadas -> de aqui sale
               el flujo RPA determinista (`grabacion.py`)

El docstring de cada tool es lo que el LLM lee para decidir cuando usarla.
"""

import json
import time

import pyautogui
import pyperclip
from langchain_core.tools import tool

from agente import config, vision


def _localizar(descripcion: str) -> tuple[int, int]:
    c = vision.localizar_elemento_en_pantalla(descripcion)
    return c["x"], c["y"]


def _salida(resultado: str, acciones: list[dict]) -> str:
    return json.dumps({"resultado": resultado, "acciones": acciones}, ensure_ascii=False)


@tool
def pulsar(descripcion: str) -> str:
    """Pulsa un boton o una pestaña. `descripcion` le dice al modelo de vision
    que buscar y donde, p.ej. "el botón Añadir cliente, debajo del formulario
    Alta de cliente".
    """
    x, y = _localizar(descripcion)
    pyautogui.click(x, y)
    return _salida(f"pulsado: {descripcion}",
                   [{"accion": "click", "elemento": descripcion, "x": x, "y": y}])


@tool
def rellenar_campo(descripcion: str, texto: str) -> str:
    """Escribe `texto` en un campo de texto. `descripcion` le dice al modelo
    de vision que campo es y donde esta. Usala para rellenar campos. No borra
    lo que hubiera antes: al corregir un campo que la verificacion dice que
    esta mal, llama primero a `borrar_campo` y luego a esta.
    """
    x, y = _localizar(descripcion)
    pyautogui.click(x, y)
    pyautogui.press("end")
    # pegar en vez de teclear: typewrite se salta en silencio los caracteres
    # que no estan en su lista de teclas (tildes, ñ, ...)
    pyperclip.copy(texto)
    pyautogui.hotkey("ctrl", "v")
    return _salida(f"escrito '{texto}' en: {descripcion}",
                   [{"accion": "escribir", "elemento": descripcion, "x": x, "y": y, "texto": texto}])


@tool
def borrar_campo(descripcion: str) -> str:
    """Vacia un campo de texto. Usa la misma `descripcion` que usaste para
    rellenarlo. Usala solo para corregir un campo que la verificacion dice
    que esta mal, justo antes de `rellenar_campo`.
    """
    x, y = _localizar(descripcion)
    pyautogui.click(x, y)
    # ir al final y borrar hacia atras. NO usamos Shift+Home para seleccionar
    # todo: pyautogui en Windows manda Home como tecla del teclado numerico y,
    # con Bloq Num activado, Windows suelta el Shift y no selecciona nada.
    pyautogui.press("end")
    pyautogui.press("backspace", presses=50)
    return _salida(f"vaciado: {descripcion}",
                   [{"accion": "borrar", "elemento": descripcion, "x": x, "y": y}])


@tool
def seleccionar_en_desplegable(desplegable: str, opcion: str) -> str:
    """Elige una opcion de un desplegable: lo abre y hace clic en la opcion.
    `desplegable` le dice al modelo de vision que desplegable es y donde esta;
    `opcion` es el texto exacto de la opcion, p.ej. "Palet de madera estándar".
    """
    x1, y1 = _localizar(desplegable)
    pyautogui.click(x1, y1)
    time.sleep(config.PAUSA_DESPLEGABLE)  # dar tiempo a que se pinte la lista
    # que la lista esta abierta solo lo sabe esta tool (la acaba de abrir)
    x2, y2 = _localizar(
        f"la opción '{opcion}' dentro de la lista desplegable que está abierta"
    )
    pyautogui.click(x2, y2)
    return _salida(
        f"seleccionado '{opcion}' en: {desplegable}",
        [{"accion": "click", "elemento": desplegable, "x": x1, "y": y1},
         {"accion": "click", "elemento": f"opción {opcion}", "x": x2, "y": y2}],
    )


TOOLS_ACCION = [pulsar, rellenar_campo, borrar_campo, seleccionar_en_desplegable]
NOMBRES_TOOLS_ACCION = tuple(t.name for t in TOOLS_ACCION)
