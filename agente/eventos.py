"""Como cuenta el agente lo que va haciendo.

Todo el paquete llama a `emitir(tipo, **datos)` en vez de hacer `print`. Quien
lo use decide a donde va: por defecto se imprime en la terminal; la plataforma
lo cambia con `fijar_emisor` para mandarlo a la web por WebSocket.

Tipos de evento:
    tool            el agente llama a una tool        nombre, args
    tool_resultado  lo que la tool le devuelve         nombre, texto
    lectura         UI-TARS lee un campo al verificar  frase, respuesta
    texto_agente    texto que escribe el LLM           texto
    mensaje         aviso del propio programa          texto
    paso / paso_ok  pasos del robot (RPA puro)         indice, total, accion, elemento, ...
"""

from collections.abc import Callable

Emisor = Callable[..., None]


def imprimir(tipo: str, **datos) -> None:
    """Emisor por defecto: una linea legible por evento."""
    if tipo == "tool":
        print(f">> {datos['nombre']}({datos['args']})")
    elif tipo == "tool_resultado":
        print(f"   = {datos['texto']}")
    elif tipo == "lectura":
        print(f"   [UI-TARS] {datos['frase']} -> {datos['respuesta']!r}")
    elif tipo == "texto_agente":
        print(f"\n[agente] {datos['texto']}\n")
    elif tipo == "paso":
        texto = f" <- '{datos['texto']}'" if datos.get("texto") else ""
        print(f"{datos['indice'] + 1:2}. {datos['accion']:8} {datos['elemento']}{texto}")
    elif tipo == "paso_ok":
        pass  # en la terminal basta con la linea de "paso"
    else:
        print(f">> {datos.get('texto', datos)}")


_emisor: Emisor = imprimir


def fijar_emisor(emisor: Emisor) -> None:
    global _emisor
    _emisor = emisor


def emitir(tipo: str, **datos) -> None:
    _emisor(tipo, **datos)
