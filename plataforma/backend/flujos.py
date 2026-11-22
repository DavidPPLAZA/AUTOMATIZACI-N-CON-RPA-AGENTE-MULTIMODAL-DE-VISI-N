"""Lectura y borrado de los robots (flujos RPA en JSON) guardados en disco."""

import json
import re
from pathlib import Path

from agente.config import DIR_FLUJOS


def _titulo(instruccion: str, id_flujo: str) -> str:
    """Titulo corto a partir del OBJETIVO del prompt, o el nombre del fichero."""
    m = re.search(r"OBJETIVO:\s*(.+?)(?:\.\s|PASO\s*1)", instruccion, flags=re.S)
    if m:
        objetivo = " ".join(m.group(1).split())
        return objetivo[0].upper() + objetivo[1:]
    return id_flujo.replace("_", " ")


def _ruta(id_flujo: str) -> Path:
    # el id es el nombre del fichero sin extension; nada de rutas
    if not re.fullmatch(r"[\w\-]+", id_flujo):
        raise FileNotFoundError(id_flujo)
    ruta = DIR_FLUJOS / f"{id_flujo}.json"
    if not ruta.is_file():
        raise FileNotFoundError(id_flujo)
    return ruta


def cargar(id_flujo: str) -> dict:
    datos = json.loads(_ruta(id_flujo).read_text(encoding="utf-8"))
    instruccion = datos.get("instruccion", "")
    return {
        "id": id_flujo,
        "titulo": _titulo(instruccion, id_flujo),
        "fecha": datos.get("fecha"),
        "instruccion": instruccion,
        "ventana": datos["ventana"],
        "pasos": datos["pasos"],
    }


def listar() -> list[dict]:
    if not DIR_FLUJOS.is_dir():
        return []
    flujos = []
    for ruta in DIR_FLUJOS.glob("*.json"):
        try:
            f = cargar(ruta.stem)
        except (ValueError, KeyError):
            continue  # fichero roto: no lo listamos
        flujos.append({k: f[k] for k in ("id", "titulo", "fecha")} | {"n_pasos": len(f["pasos"])})
    # los mas recientes primero (sin fecha, al final)
    return sorted(flujos, key=lambda f: f["fecha"] or "", reverse=True)


def borrar(id_flujo: str) -> None:
    """Borra el fichero del robot. No se puede deshacer."""
    _ruta(id_flujo).unlink()
