"""Localizacion de elementos de UI sobre una captura de pantalla real, con
UI-TARS-7B-DPO. Misma logica (carga del modelo, prompt, parseo de
coordenadas) validada en `vision_evaluation.ipynb`, extraida aqui para
poder reutilizarla desde otros notebooks sin duplicarla.
"""

import re
import time

import mss
import torch
from PIL import Image

_uitars_model = None
_uitars_processor = None


def _load_uitars():
    global _uitars_model, _uitars_processor
    if _uitars_model is None:
        from transformers import AutoProcessor, Qwen2VLForConditionalGeneration

        model_id = "ByteDance-Seed/UI-TARS-7B-DPO"
        _uitars_processor = AutoProcessor.from_pretrained(model_id)
        _uitars_model = Qwen2VLForConditionalGeneration.from_pretrained(
            model_id, torch_dtype=torch.bfloat16, device_map="auto"
        )
    return _uitars_model, _uitars_processor


def _ask_uitars(image: Image.Image, target_desc: str) -> dict:
    model, processor = _load_uitars()
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {
                    "type": "text",
                    "text": f"Click on {target_desc}. Respond with click(start_box='(x,y)').",
                },
            ],
        }
    ]
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = processor(text=[text], images=[image], return_tensors="pt").to(model.device)

    t0 = time.perf_counter()
    output_ids = model.generate(**inputs, max_new_tokens=128)
    elapsed = time.perf_counter() - t0

    raw = processor.batch_decode(
        output_ids[:, inputs["input_ids"].shape[1]:], skip_special_tokens=True
    )[0]
    return {"raw": raw, "elapsed_s": elapsed}


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


def capturar_pantalla() -> Image.Image:
    """Captura el monitor principal con `mss` y lo devuelve como imagen PIL."""
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # [0] es "todos los monitores juntos"
        shot = sct.grab(monitor)
        return Image.frombytes("RGB", shot.size, shot.rgb)


def localizar_elemento_en_pantalla(descripcion: str) -> dict:
    """Hace una captura de pantalla real y le pide a UI-TARS que localice
    el elemento descrito. Devuelve coordenadas absolutas de pantalla (las
    que espera `pyautogui`), listas para pasar a una tool de clic."""
    screenshot = capturar_pantalla()
    width, height = screenshot.size
    resultado = _ask_uitars(screenshot, descripcion)
    rel_x, rel_y = parse_uitars_xy(resultado["raw"])
    return {
        "x": round(rel_x / 1000 * width),
        "y": round(rel_y / 1000 * height),
        "raw": resultado["raw"],
        "elapsed_s": resultado["elapsed_s"],
    }
