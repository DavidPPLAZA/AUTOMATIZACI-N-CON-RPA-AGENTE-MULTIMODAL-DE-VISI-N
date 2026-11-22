"""Ajustes del backend de la plataforma."""

from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

# robots (flujos RPA) que genera el agente en el notebook de experimentos
DIR_FLUJOS = RAIZ / "experiments" / "flujos"
# prompt de ejemplo que se precarga en el Estudio
PROMPT_EJEMPLO = RAIZ / "experiments" / "prompts" / "login_alta_cliente.txt"

TITULO_VENTANA = "GestCorp 98 - Sistema de Gestión Comercial"
# en que mitad de la pantalla se abre GestCorp; la web va en la otra mitad
LADO_GESTCORP = "derecha"  # "izquierda" | "derecha"

# pausas del robot entre pasos (la UI de GestCorp necesita un momento para
# reaccionar: cambiar de pestaña, abrir una lista...)
PAUSA_CLICK = 1.0
PAUSA_ESCRIBIR = 0.3

# el frontend (Next.js en desarrollo) que puede llamar a esta API
ORIGENES_PERMITIDOS = ["http://localhost:3000", "http://127.0.0.1:3000"]
