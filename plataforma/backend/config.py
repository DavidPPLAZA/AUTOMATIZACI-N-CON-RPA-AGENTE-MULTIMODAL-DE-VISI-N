"""Ajustes del backend de la plataforma. Lo del agente y GestCorp 98 (modelos,
ventana, pausas, carpeta de robots) vive en `agente/config.py`."""

from agente.config import RAIZ

# prompt de ejemplo que se precarga en el Estudio
PROMPT_EJEMPLO = RAIZ / "experiments" / "prompts" / "login_alta_cliente.txt"

# el frontend (Next.js en desarrollo) que puede llamar a esta API
ORIGENES_PERMITIDOS = ["http://localhost:3000", "http://127.0.0.1:3000"]
