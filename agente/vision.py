"""Vision sobre capturas de pantalla reales con UI-TARS-7B-DPO: localizar
elementos de UI (misma logica de carga, prompt y parseo de coordenadas
validada en `vision_evaluation.ipynb`) y hacerle preguntas sobre lo que se
ve, para verificar el efecto de cada accion.

Copia de `experiments/vision_tools.py` (que se queda alli porque lo usan los
notebooks de experimentos).
"""

import re
import time

import mss
import torch
from PIL import Image

from agente import config
from agente.eventos import emitir

_uitars_model = None
_uitars_processor = None
_region_captura: dict | None = None


def _load_uitars():
    global _uitars_model, _uitars_processor
    if _uitars_model is None:
        from transformers import AutoProcessor, Qwen2VLForConditionalGeneration

        model_id = config.MODELO_VISION
        _uitars_processor = AutoProcessor.from_pretrained(model_id)
        if not torch.cuda.is_available():
            raise RuntimeError("UI-TARS necesita GPU y torch no ve ninguna (CUDA no disponible)")
        # "cuda:0" y no "auto": con "auto", si la VRAM no llega, accelerate manda
        # capas a la CPU sin avisar y cada inferencia pasa a ser lentisima. Asi,
        # o cabe entero en la GPU o falla con un error claro.
        _uitars_model = Qwen2VLForConditionalGeneration.from_pretrained(
            model_id, torch_dtype=torch.bfloat16, device_map="cuda:0"
        )
    return _uitars_model, _uitars_processor


def precargar_modelo_vision() -> None:
    """Carga UI-TARS en memoria si no lo esta ya. Llamar a esto de
    antemano (antes de abrir la app objetivo) evita que la primera llamada
    a `localizar_elemento_en_pantalla` se quede varios segundos cargando el
    modelo justo en medio de la automatizacion.
    """
    model, _ = _load_uitars()
    dispositivos = {str(p.device) for p in model.parameters()}
    vram = torch.cuda.memory_allocated(0) / 2**30
    emitir(
        "mensaje",
        texto=f"UI-TARS en {', '.join(sorted(dispositivos))} "
        f"({torch.cuda.get_device_name(0)}, {vram:.1f} GB de VRAM).",
    )


def _generate_uitars(image: Image.Image, prompt_text: str, max_new_tokens: int = 128) -> str:
    model, processor = _load_uitars()
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": prompt_text},
            ],
        }
    ]
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = processor(text=[text], images=[image], return_tensors="pt").to(model.device)
    output_ids = model.generate(**inputs, max_new_tokens=max_new_tokens)
    return processor.batch_decode(
        output_ids[:, inputs["input_ids"].shape[1]:], skip_special_tokens=True
    )[0]


def _ask_uitars(image: Image.Image, target_desc: str) -> dict:
    t0 = time.perf_counter()
    raw = _generate_uitars(image, f"Click on {target_desc}. Respond with click(start_box='(x,y)').")
    elapsed = time.perf_counter() - t0
    return {"raw": raw, "elapsed_s": elapsed}


def preguntar_sobre_pantalla(
    pregunta: str, x: int | None = None, y: int | None = None, ancho: int = 300, alto: int = 100
) -> str:
    """En vez de pedirle a UI-TARS coordenadas de clic, le hace una
    pregunta normal en lenguaje natural sobre lo que ve (su model card
    reporta benchmarks de pregunta-respuesta sobre pantallas, WebSRC y
    ScreenQA, y en la practica responde bien). Si se dan (x, y), solo mira
    un recorte (ancho x alto) alrededor de esas coordenadas; si no, mira la
    captura completa.
    """
    if x is not None and y is not None:
        imagen = _recortar_alrededor(x, y, ancho, alto)
    else:
        imagen = capturar_pantalla()
    return _generate_uitars(imagen, pregunta).strip()


def parse_uitars_xy(raw: str) -> tuple[float, float]:
    """Extrae (x, y) relativos (escala 0-1000) del formato de UI-TARS.

    Ver `vision_evaluation.ipynb`, seccion 3, para la explicacion completa
    de por que es 0-1000 sobre la imagen original y no pixeles de una
    imagen redimensionada internamente (eso es Qwen2.5-VL, no este modelo).
    """
    m = re.search(r"start_box='?\(?\s*(-?\d+)\s*,\s*(-?\d+)\s*\)?'?", raw)
    if m:
        return float(m.group(1)), float(m.group(2))
    nums = re.findall(r"-?\d+\.?\d*", raw)
    if len(nums) >= 2:
        return float(nums[0]), float(nums[1])
    raise ValueError(f"no pude extraer coordenadas de: {raw!r}")


def fijar_region_captura(left: int, top: int, width: int, height: int) -> None:
    """Limita todas las capturas (y por tanto todo lo que ve UI-TARS) a esta
    zona de la pantalla, p.ej. la ventana de la app objetivo. Sin esto el
    modelo veria tambien lo que haya al lado (el notebook) y podria
    localizar o leer texto de ahi en vez de la app.
    """
    global _region_captura
    _region_captura = {"left": left, "top": top, "width": width, "height": height}


def _origen_captura() -> tuple[int, int]:
    """Esquina superior izquierda de lo que captura `capturar_pantalla`,
    en coordenadas absolutas de pantalla."""
    if _region_captura is not None:
        return _region_captura["left"], _region_captura["top"]
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        return monitor["left"], monitor["top"]


def capturar_pantalla() -> Image.Image:
    """Captura la region fijada con `fijar_region_captura` (o el monitor
    principal si no se ha fijado ninguna) y la devuelve como imagen PIL."""
    with mss.mss() as sct:
        region = _region_captura or sct.monitors[1]  # monitors[0] es "todos juntos"
        shot = sct.grab(region)
        return Image.frombytes("RGB", shot.size, shot.rgb)


def _recortar_alrededor(x: int, y: int, ancho: int, alto: int) -> Image.Image:
    """Captura y recorta la zona (ancho x alto) centrada en (x, y), que
    vienen en coordenadas absolutas de pantalla."""
    screenshot = capturar_pantalla()
    origen_x, origen_y = _origen_captura()
    cx, cy = x - origen_x, y - origen_y
    left = max(0, cx - ancho // 2)
    top = max(0, cy - alto // 2)
    right = min(screenshot.width, cx + ancho // 2)
    bottom = min(screenshot.height, cy + alto // 2)
    return screenshot.crop((left, top, right, bottom))


def localizar_elemento_en_pantalla(descripcion: str) -> dict:
    """Hace una captura de pantalla real y le pide a UI-TARS que localice
    el elemento descrito. Devuelve coordenadas absolutas de pantalla (las
    que espera `pyautogui`), listas para pasar a una tool de clic."""
    screenshot = capturar_pantalla()
    width, height = screenshot.size
    origen_x, origen_y = _origen_captura()
    resultado = _ask_uitars(screenshot, descripcion)
    rel_x, rel_y = parse_uitars_xy(resultado["raw"])
    return {
        "x": origen_x + round(rel_x / 1000 * width),
        "y": origen_y + round(rel_y / 1000 * height),
        "raw": resultado["raw"],
        "elapsed_s": resultado["elapsed_s"],
    }
