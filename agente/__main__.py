"""Atajo de depuracion: lanzar el agente desde la terminal, sin la web.
Lo normal es usarlo desde la plataforma (Estudio -> "Lanzar agente").

    uv run python -m agente experiments/prompts/login_alta_cliente.txt
    uv run python -m agente --robot experiments/flujos/flujo_X.json
"""

import json
import sys
from pathlib import Path

from agente import reproductor, sesion


def main() -> None:
    args = sys.argv[1:]
    if len(args) == 2 and args[0] == "--robot":
        flujo = json.loads(Path(args[1]).read_text(encoding="utf-8"))
        print(reproductor.reproducir(flujo))
    elif len(args) == 1:
        sesion.ejecutar_agente(Path(args[0]).read_text(encoding="utf-8").strip())
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
