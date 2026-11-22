"""Del agente al RPA determinista: extraer los pasos buenos de una ejecucion.

El historial de mensajes del agente es la GRABACION de toda la ejecucion:
cada tool que llamo, con sus argumentos y lo que le devolvio. De ahi sale un
flujo de clics fijo, sin agente ni vision:

- las tools de accion devuelven las acciones fisicas que hicieron (clic o
  escritura, con coordenadas): esos son los pasos. Un desplegable son dos clics.
- las verificaciones se quedan fuera: el RPA no tiene vision.

Limpieza de redundancias:
- cada escritura se reproduce como borrar + escribir, asi que los "borrar"
  del agente sobran.
- si un mismo campo se escribio varias veces seguidas (una correccion tras
  verificar), solo vale la ultima.
- dos clics identicos seguidos cuentan como uno.

Las coordenadas se guardan relativas a la ventana, y cada grabacion va a su
propio fichero `flujo_AAAAMMDD_HHMMSS.json`: ninguna sobrescribe a otra.
"""

import json
from datetime import datetime
from pathlib import Path

from langchain_core.messages import AIMessage, BaseMessage, ToolMessage

from agente import config
from agente.tools_accion import NOMBRES_TOOLS_ACCION


def extraer_pasos(mensajes: list[BaseMessage], origen_x: int, origen_y: int) -> list[dict]:
    """Acciones fisicas de las tools de accion, en coordenadas relativas a la
    ventana (cuya esquina estaba en origen_x, origen_y durante la grabacion)."""
    resultados = {m.tool_call_id: m.content for m in mensajes if isinstance(m, ToolMessage)}
    pasos = []
    for m in mensajes:
        if not isinstance(m, AIMessage):
            continue
        for tc in m.tool_calls or []:
            if tc["name"] not in NOMBRES_TOOLS_ACCION or tc["id"] not in resultados:
                continue  # las verificaciones no pasan al flujo
            try:
                acciones = json.loads(resultados[tc["id"]])["acciones"]
            except (ValueError, KeyError):
                continue  # la tool fallo (error, no JSON)
            for acc in acciones:
                if acc["accion"] == "borrar":
                    continue  # al reproducir, cada escritura vacia antes el campo
                paso = {"accion": acc["accion"], "elemento": acc["elemento"],
                        "x": acc["x"] - origen_x, "y": acc["y"] - origen_y}
                if acc["accion"] == "escribir":
                    paso["texto"] = acc["texto"]
                pasos.append(paso)
    return pasos


def limpiar(pasos: list[dict]) -> list[dict]:
    """Quita las redundancias (ver docstring del modulo)."""
    limpios: list[dict] = []
    for paso in pasos:
        previo = limpios[-1] if limpios else None
        if paso["accion"] == "click" and previo == paso:
            continue  # dos clics identicos seguidos
        if paso["accion"] == "escribir":
            # mismo campo (mismas coordenadas o misma descripcion) ya escrito
            # desde el ultimo clic -> solo vale la ultima escritura. Asi se
            # descartan tambien las que cayeron en un sitio equivocado y la
            # verificacion obligo a repetir en el bueno.
            for i in range(len(limpios) - 1, -1, -1):
                if limpios[i]["accion"] == "click":
                    break
                mismas_coords = (limpios[i]["x"], limpios[i]["y"]) == (paso["x"], paso["y"])
                mismo_campo = paso["elemento"] != "?" and limpios[i]["elemento"] == paso["elemento"]
                if mismas_coords or mismo_campo:
                    del limpios[i]
                    break
        limpios.append(paso)
    return limpios


def guardar_flujo(
    mensajes: list[BaseMessage], instruccion: str, rect_ventana: dict,
    directorio: Path = config.DIR_FLUJOS,
) -> Path:
    """Convierte la grabacion en un flujo RPA y lo guarda en su propio fichero.
    `rect_ventana`: {"left", "top", "ancho", "alto"} de la ventana durante la
    grabacion. Devuelve la ruta del fichero."""
    pasos = limpiar(extraer_pasos(mensajes, rect_ventana["left"], rect_ventana["top"]))
    fecha = datetime.now()
    flujo = {
        "fecha": fecha.isoformat(timespec="seconds"),
        "instruccion": instruccion,  # el prompt que se le dio al agente
        "ventana": {"ancho": rect_ventana["ancho"], "alto": rect_ventana["alto"]},
        "pasos": pasos,
    }
    ruta = Path(directorio) / f"flujo_{fecha:%Y%m%d_%H%M%S}.json"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(flujo, ensure_ascii=False, indent=2), encoding="utf-8")
    return ruta
