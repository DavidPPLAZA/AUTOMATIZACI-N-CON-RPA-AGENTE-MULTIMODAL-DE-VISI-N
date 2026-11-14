from pathlib import Path

APP_TITLE = "GestCorp 98 - Sistema de Gestión Comercial"
APP_VERSION = "v1.0 (1998)"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "gestcorp98.sqlite3"

# Paleta "Windows 95" para dar el aspecto retro a la app.
BG_COLOR = "#C0C0C0"
TITLE_BG = "#000080"
FONT_FAMILY = "MS Sans Serif"
FONT = (FONT_FAMILY, 9)

DEMO_USER = "admin"
DEMO_PASS = "admin"
