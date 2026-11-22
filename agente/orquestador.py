"""El orquestador: LangChain v1 (`create_agent`) + gpt-oss-120b en Groq.

`create_agent` monta el bucle estandar (el LLM decide una tool -> se ejecuta
de verdad -> el resultado vuelve al LLM -> repite) sin escribir el grafo a mano.

Si el agente para antes de tiempo (mensaje vacio, o Groq rechaza su
respuesta) sin haber escrito su RESUMEN FINAL, se le pide que continue con
todo el historial.
"""

import json
import os
import threading

from dotenv import load_dotenv
from groq import BadRequestError
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_groq import ChatGroq

from agente import config
from agente.eventos import emitir
from agente.prompts import SYSTEM_PROMPT
from agente.tools_accion import TOOLS_ACCION
from agente.verificacion import TOOLS_VERIFICACION

MARCA_FIN = "RESUMEN FINAL"
PETICION_CONTINUAR = "No has terminado. Continua con el siguiente paso pendiente del proceso."

_agente = None


def crear_agente():
    """Crea el agente la primera vez y lo reutiliza despues."""
    global _agente
    if _agente is None:
        load_dotenv(config.RAIZ / ".env")  # GROQ_API_KEY
        if not os.environ.get("GROQ_API_KEY"):
            raise RuntimeError(
                "Falta GROQ_API_KEY: rellénala en el archivo .env de la raíz del proyecto "
                "(la consigues en https://console.groq.com/)."
            )
        modelo = ChatGroq(
            model=config.MODELO_LLM, temperature=0, reasoning_effort=config.REASONING_EFFORT
        )
        _agente = create_agent(
            modelo, tools=[*TOOLS_ACCION, *TOOLS_VERIFICACION], system_prompt=SYSTEM_PROMPT
        )
    return _agente


def _texto_resultado(contenido) -> str:
    """Las tools de accion devuelven JSON; para contarlo basta su "resultado"."""
    try:
        return json.loads(contenido)["resultado"]
    except (ValueError, TypeError, KeyError):
        return str(contenido)


def _contar(mensaje: BaseMessage) -> None:
    """Emite un evento por cada cosa nueva que aparece en el historial."""
    if isinstance(mensaje, AIMessage):
        texto = str(mensaje.content).strip()
        if texto:
            emitir("texto_agente", texto=texto)
        for tc in mensaje.tool_calls or []:
            emitir("tool", nombre=tc["name"], args=tc["args"])
    elif isinstance(mensaje, ToolMessage):
        emitir("tool_resultado", nombre=mensaje.name, texto=_texto_resultado(mensaje.content))


def ejecutar(instruccion: str, detener: threading.Event | None = None) -> dict:
    """Ejecuta el agente sobre la app que ya este abierta (y con la region de
    captura fijada). Va contando cada paso con `emitir`. `detener` se mira
    entre paso y paso: si se activa, el agente para ahi.

    Devuelve {"mensajes": historial completo (la grabacion de la que sale el
    flujo RPA), "completado": escribio su RESUMEN FINAL, "detenido": bool}.
    """
    agente = crear_agente()
    mensajes: list = [HumanMessage(instruccion)]
    contados = 0  # cuantos mensajes del historial ya se han emitido
    completado = detenido = False

    for intento in range(config.MAX_REANUDACIONES + 1):
        fallo_groq = False
        try:
            for estado in agente.stream({"messages": mensajes}, stream_mode="values"):
                mensajes = estado["messages"]
                for m in mensajes[contados:]:
                    _contar(m)
                contados = len(mensajes)
                if detener is not None and detener.is_set():
                    detenido = True
                    break
        except BadRequestError as exc:
            # el modelo genero algo que Groq no puede leer (una llamada a tool
            # con JSON roto o una respuesta vacia). Esa respuesta no entra en
            # el historial, asi que se trata igual que una parada a medias
            cuerpo = exc.body if isinstance(exc.body, dict) else {}
            codigo = cuerpo.get("error", {}).get("code", "desconocido")
            emitir("mensaje", texto=f"Groq rechazó la respuesta del modelo ({codigo}).")
            fallo_groq = True

        if detenido:
            emitir("mensaje", texto="Agente detenido por el usuario.")
            break
        if not fallo_groq and MARCA_FIN in str(mensajes[-1].content):
            completado = True
            break
        if intento == config.MAX_REANUDACIONES:
            emitir("mensaje", texto="El agente sigue parando sin terminar; me rindo.")
            break
        emitir("mensaje", texto="El agente paró sin terminar; le pido que continúe.")
        mensajes = [*mensajes, HumanMessage(PETICION_CONTINUAR)]
        contados = len(mensajes)  # la peticion de continuar ya se ha contado arriba

    return {"mensajes": mensajes, "completado": completado, "detenido": detenido}
