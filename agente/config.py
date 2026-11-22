"""Ajustes del agente: modelos, ventana de GestCorp 98, pausas y carpetas."""

from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

# robots (flujos RPA en JSON) que salen de cada ejecucion del agente
DIR_FLUJOS = RAIZ / "experiments" / "flujos"

# --- modelos ---
# orquestador: gpt-oss-120b en Groq. reasoning_effort="low" para que "piense"
# menos antes de cada tool: esos tokens tambien cuentan para el limite diario.
MODELO_LLM = "openai/gpt-oss-120b"
REASONING_EFFORT = "low"
# vision: localiza elementos y lee lo que hay escrito (siempre en GPU)
MODELO_VISION = "ByteDance-Seed/UI-TARS-7B-DPO"

# si el agente para sin escribir su RESUMEN FINAL, cuantas veces se le pide que siga
MAX_REANUDACIONES = 5

# --- la app ---
TITULO_VENTANA = "GestCorp 98 - Sistema de Gestión Comercial"
# en que mitad de la pantalla se abre GestCorp; lo que mira el usuario va en la otra
LADO_GESTCORP = "derecha"  # "izquierda" | "derecha"

# --- pausas ---
# al abrir un desplegable, tiempo para que se pinte la lista antes de buscar la opcion
PAUSA_DESPLEGABLE = 0.7
# robot (RPA puro): la UI necesita un momento tras cada paso (cambiar de
# pestaña, abrir una lista...)
PAUSA_CLICK = 1.0
PAUSA_ESCRIBIR = 0.3
