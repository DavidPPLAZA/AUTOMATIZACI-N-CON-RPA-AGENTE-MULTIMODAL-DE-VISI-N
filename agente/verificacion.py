"""Tools de verificacion: comprobar un formulario ANTES de enviarlo.

UI-TARS SOLO LEE, campo a campo (una frase corta por campo para que la
complete, con la zona y el nombre del campo, sin darle el valor esperado).
La comparacion con lo que pidio el usuario la hace este codigo, de forma
determinista, y devuelve al agente SI/NO y, por campo, BIEN o MAL.
"""

from langchain_core.tools import tool

from agente import vision
from agente.eventos import emitir


def _leer_campo(frase: str) -> str:
    """Le pide a UI-TARS (captura de la ventana entera) que complete `frase`
    (p.ej. 'En la parte de abajo, en "Alta de cliente", el campo "NIF" es:')
    con lo que hay escrito. Solo lee: no le damos el valor esperado (para que
    no tienda a darnos la razon) y no compara nada."""
    pregunta = (
        "Responde solo con el texto que hay escrito, sin comillas ni "
        "explicaciones. Si no hay nada escrito, responde VACIO.\n" + frase
    )
    respuesta = vision.preguntar_sobre_pantalla(pregunta)
    emitir("lectura", frase=frase, respuesta=respuesta)
    return respuesta


def _normalizar(texto: str, etiqueta: str) -> str:
    """Limpia lo que no es contenido del campo: espacios, comillas, un punto
    final y la etiqueta si UI-TARS la copia (p.ej. "Nombre: David")."""
    t = " ".join(texto.split()).strip("\"'`«»“”‘’").rstrip(".").strip()
    if t.lower().startswith(etiqueta.lower() + ":"):
        t = t[len(etiqueta) + 1:].strip()
    return "" if t.upper() == "VACIO" or t.upper() == "VACÍO" else t


def _verificar_campos(campos: list[tuple[str, str, str, str]]) -> str:
    """campos: (etiqueta, valor pedido, descripcion de donde mirar, tipo),
    con tipo "texto" (hueco donde se escribe) o "desplegable".
    UI-TARS lee cada campo por separado y aqui se compara de forma
    determinista con lo pedido (sin distinguir mayusculas)."""
    lineas, todo_bien = [], True
    for etiqueta, pedido, donde, tipo in campos:
        leido = _normalizar(_leer_campo(donde), etiqueta)
        if leido.casefold() == pedido.strip().casefold():
            lineas.append(f"- {etiqueta}: BIEN (hay escrito '{leido}')")
        else:
            todo_bien = False
            if tipo == "desplegable":
                como = (
                    f"Es un desplegable: corrígelo con seleccionar_en_desplegable "
                    f"eligiendo '{pedido}'."
                )
            else:
                como = (
                    f"Es un campo de texto: corrígelo con borrar_campo y después "
                    f"rellenar_campo con '{pedido}'."
                )
            lineas.append(
                f"- {etiqueta}: MAL. Hay escrito '{leido or 'nada (vacío)'}' y el usuario "
                f"pidió '{pedido}'. {como}"
            )
    cabecera = "SI: todos los campos están bien." if todo_bien else "NO: hay campos mal."
    return cabecera + "\n" + "\n".join(lineas)


@tool
def verificar_alta_cliente(
    nombre: str = "", nif: str = "", email: str = "", telefono: str = "", ciudad: str = ""
) -> str:
    """Comprueba que el formulario "Alta de cliente" contiene lo que te pidio
    el usuario. Usala cuando hayas rellenado todos los campos que te pidio y
    ANTES de pulsar "Añadir cliente". Pasa SOLO los campos que te pidio
    rellenar, con su valor exacto. Devuelve SI o NO y, campo a campo, si
    esta BIEN o MAL y que hay escrito.
    """
    campos = [
        (etiqueta, valor,
         f'En la parte de abajo, en "Alta de cliente", el campo "{etiqueta}" es:',
         "texto")
        for etiqueta, valor in [
            ("Nombre", nombre), ("NIF", nif), ("Email", email),
            ("Teléfono", telefono), ("Ciudad", ciudad),
        ]
        if valor  # solo los campos que el agente dice que le pidieron
    ]
    if not campos:
        return "No me has pasado ningún campo: pasa los valores que te pidió el usuario."
    return _verificar_campos(campos)


@tool
def verificar_pedido(cliente: str, producto: str, cantidad: str) -> str:
    """Comprueba que el formulario "Nuevo pedido" tiene el cliente, el
    producto y la cantidad que te pidio el usuario. Usala cuando lo hayas
    rellenado todo y ANTES de pulsar "Crear pedido". Devuelve SI o NO y,
    campo a campo, si esta BIEN o MAL y que hay escrito.
    """
    def frase(etiqueta: str) -> str:
        return f'En la parte de abajo, en "Nuevo pedido", el campo "{etiqueta}" es:'
    return _verificar_campos([
        ("Cliente", cliente, frase("Cliente"), "desplegable"),
        ("Producto", producto, frase("Producto"), "desplegable"),
        ("Cantidad", str(cantidad), frase("Cantidad"), "texto"),
    ])


TOOLS_VERIFICACION = [verificar_alta_cliente, verificar_pedido]
