"""Genera el ground truth de 3 capturas para evaluar modelos de vision,
sobre el proceso "iniciar sesion y dar de alta un cliente" en GestCorp 98.

Usa la base de datos real del proyecto tal cual: solo lee su estado para
mostrarlo en pantalla, nunca inserta ni modifica filas.
"""
import ctypes
import ctypes.wintypes as wintypes
import json
import sys
import time
import tkinter as tk
from pathlib import Path
from tkinter import ttk

import mss
import mss.tools

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gestcorp98 import config, database
from gestcorp98.ui.login_window import LoginFrame
from gestcorp98.ui.main_window import MainWindow

# Sin esto, en pantallas con escalado de Windows > 100% las coordenadas que
# reporta Tkinter no coinciden con los pixeles reales de la captura.
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()

OUT_DIR = Path(__file__).resolve().parent / "ground_truth"
OUT_DIR.mkdir(parents=True, exist_ok=True)

with mss.MSS() as _sct:
    _monitor = _sct.monitors[0]  # pantalla completa (todos los monitores)
MONITOR_LEFT = _monitor["left"]
MONITOR_TOP = _monitor["top"]

coords: dict[str, dict[str, list[int]]] = {}


def full_screenshot(name: str) -> None:
    with mss.MSS() as sct:
        shot = sct.grab(_monitor)
        mss.tools.to_png(shot.rgb, shot.size, output=str(OUT_DIR / name))
    print("captura guardada:", OUT_DIR / name)


def widget_center(widget) -> list[int]:
    x = widget.winfo_rootx() + widget.winfo_width() // 2 - MONITOR_LEFT
    y = widget.winfo_rooty() + widget.winfo_height() // 2 - MONITOR_TOP
    return [x, y]


# ---- utilidades Win32: en Windows, messagebox.showwarning() abre el
# dialogo NATIVO de Windows (clase "#32770"), no una ventana de Tkinter,
# asi que hay que localizarlo y leer su boton con la API de Windows. ----
user32 = ctypes.windll.user32

user32.FindWindowW.restype = wintypes.HWND
user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]

WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
user32.EnumChildWindows.argtypes = [wintypes.HWND, WNDENUMPROC, wintypes.LPARAM]
user32.EnumChildWindows.restype = wintypes.BOOL

user32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetClassNameW.restype = ctypes.c_int

user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
user32.GetWindowRect.restype = wintypes.BOOL

user32.SendMessageW.argtypes = [wintypes.HWND, ctypes.c_uint, wintypes.WPARAM, wintypes.LPARAM]
user32.SendMessageW.restype = ctypes.c_void_p

BM_CLICK = 0x00F5


def find_window_by_title(title: str, timeout: float = 2.0) -> int:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        hwnd = user32.FindWindowW(None, title)
        if hwnd:
            return hwnd
        time.sleep(0.05)
    return 0


def find_child_button(dialog_hwnd: int) -> int:
    found = []

    def callback(hwnd, _lparam):
        buf = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, buf, 256)
        if buf.value == "Button":
            found.append(hwnd)
        return True

    user32.EnumChildWindows(dialog_hwnd, WNDENUMPROC(callback), 0)
    return found[0] if found else 0


def hwnd_center(hwnd: int) -> list[int]:
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    x = (rect.left + rect.right) // 2 - MONITOR_LEFT
    y = (rect.top + rect.bottom) // 2 - MONITOR_TOP
    return [x, y]


def main() -> None:
    conn = database.get_connection()
    database.init_db(conn)  # solo crea tablas si faltan; no inserta filas

    root = tk.Tk()
    root.title(config.APP_TITLE)
    root.configure(bg=config.BG_COLOR)
    root.state("zoomed")
    root.attributes("-topmost", True)

    holder = {}

    def on_login_success():
        for widget in root.winfo_children():
            widget.destroy()
        mw = MainWindow(root, conn)
        mw.pack(fill="both", expand=True)
        holder["mw"] = mw

    login = LoginFrame(root, on_success=on_login_success)
    login.pack(fill="both", expand=True)
    root.lift()
    root.focus_force()
    root.update()
    time.sleep(0.5)
    root.update()

    # --- Paso 1: login con "Usuario" ya relleno, "Contraseña" vacia ---
    box = next(c for c in login.winfo_children() if isinstance(c, tk.Frame))
    entrar_btn = next(c for c in box.winfo_children() if isinstance(c, tk.Button))

    full_screenshot("01_login.png")
    coords["01_login.png"] = {
        "usuario_field": widget_center(login.user_entry),
        "contraseña_field": widget_center(login.pass_entry),
        "entrar_button": widget_center(entrar_btn),
    }

    # Completar el login de verdad para llegar a la pestaña Clientes.
    login.pass_entry.insert(0, config.DEMO_PASS)
    login._try_login()
    root.update()
    time.sleep(0.3)
    root.update()

    mw = holder["mw"]
    notebook = next(c for c in mw.winfo_children() if isinstance(c, ttk.Notebook))
    clientes_tab = notebook.nametowidget(notebook.tabs()[0])
    notebook.select(0)
    root.update()

    form = next(c for c in clientes_tab.winfo_children() if isinstance(c, ttk.LabelFrame))
    anadir_btn = next(c for c in form.winfo_children() if isinstance(c, ttk.Button))

    # --- Paso 2: formulario "Alta de cliente" vacio, recien entrado ---
    full_screenshot("02_alta_cliente.png")
    coords["02_alta_cliente.png"] = {
        "nombre_field": widget_center(clientes_tab.entries["nombre"]),
        "nif_field": widget_center(clientes_tab.entries["nif"]),
        "anadir_button": widget_center(anadir_btn),
    }

    # --- Paso 3: popup nativo "Datos incompletos" ---
    def capture_popup():
        hwnd = find_window_by_title("Datos incompletos")
        if not hwnd:
            print("AVISO: no se encontro la ventana del popup nativo")
            return
        btn_hwnd = find_child_button(hwnd)
        full_screenshot("03_popup_validacion.png")
        if btn_hwnd:
            coords["03_popup_validacion.png"] = {
                "popup_aceptar_button": hwnd_center(btn_hwnd),
            }
            user32.SendMessageW(btn_hwnd, BM_CLICK, 0, 0)  # cierra el popup
        else:
            print("AVISO: no se encontro el boton del popup")

    # Se programa ANTES de disparar el popup: el messagebox bloquea este
    # hilo con su propio bucle modal, pero sigue despachando los mensajes
    # WM_TIMER de Tkinter, asi que este callback se ejecuta mientras el
    # popup sigue visible.
    root.after(500, capture_popup)
    clientes_tab._add_cliente()  # nombre y NIF vacios -> dispara el popup

    root.update()

    json_path = OUT_DIR / "alta_cliente.json"
    json_path.write_text(json.dumps(coords, ensure_ascii=False, indent=2), encoding="utf-8")
    print("JSON guardado:", json_path)

    root.destroy()
    conn.close()


if __name__ == "__main__":
    main()
