"""El agente de RPA + vision que en `experiments/agentic_pipeline.ipynb` vive
en celdas, como paquete de Python para usarlo desde la terminal y la plataforma.
"""

import ctypes

# En Windows, si el proceso no se declara "DPI aware", las coordenadas de
# pyautogui no coinciden 1:1 con los pixeles que captura mss. Tiene que hacerse
# antes de usar mss/pyautogui, por eso va aqui: al importar cualquier parte
# del paquete ya queda hecho.
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # PROCESS_SYSTEM_DPI_AWARE
except Exception:
    pass  # no es Windows, o el proceso ya lo tenia fijado
