# Reglas de colaboración en este proyecto

Contexto completo del proyecto (visión, piezas, hoja de ruta): ver [`PROJECT.md`](./PROJECT.md).

## Git

- **Nunca** hagas `git commit` ni `git push` sin que el usuario lo pida explícitamente en
  ese momento. Una aprobación de código o de un plan no es una orden de commit.
- Commits pequeños, con [Conventional Commits](https://www.conventionalcommits.org/):
  `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`. Un commit = un paso lógico de
  la hoja de ruta, no varios a la vez.

## Ritmo de trabajo

- Avanza **paso a paso**. No te adelantes a fases futuras del roadmap en `PROJECT.md` (p.
  ej. no toques las piezas 2, 3 o 4 mientras se trabaja la pieza 1) salvo que el usuario lo
  pida explícitamente.
- Dentro de la fase/pieza actual, tampoco encadenes varios pasos sin pausa: completa un
  paso, explica qué hiciste, y espera antes de seguir con el siguiente si no está ya
  aprobado.
- Antes de escribir código nuevo de un módulo o componente (no solo al empezar una pieza
  entera), propón su estructura o diseño y espera aprobación del usuario.

## Explicaciones

- El usuario está aprendiendo. Después de cada paso, explica brevemente **qué** hiciste y
  **por qué**, en términos sencillos — no asumas que conoce de antemano la herramienta o
  librería usada.
- Prioriza la claridad sobre la exhaustividad: una explicación corta y concreta es mejor
  que un resumen largo.

## Stack y entorno

- Python 3.12, gestionado con `uv` (no usar `pip`/`venv` manual).
- Tkinter (GestCorp 98), `pyautogui` + `mss` (RPA), OCR, LangGraph, Ollama (visión local),
  FastAPI + WebSocket (web de control).
- Desarrollo en Windows.
