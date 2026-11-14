# Agente RPA con Visión para Automatización de Apps Legacy

Proyecto de portfolio: un agente construido con **LangGraph** que automatiza una app de
escritorio "legacy" mediante **RPA** (`pyautogui`), y que cuando algo falla se recupera
usando **OCR** y un **modelo de visión local (Ollama)**. Incluye una web de control para
lanzar tareas, observar al agente en directo y provocar fallos a propósito ("modo caos")
para demostrar la capacidad de recuperación.

## Las 4 piezas

1. **GestCorp 98** — app legacy en Tkinter de una distribuidora, con aspecto de los años 90.
2. **Tareas RPA objetivo** sobre esa app: alta de cliente, crear pedido, leer un dato de un
   informe.
3. **Agente LangGraph** — ejecutar paso → verificar → si falla, diagnosticar y recuperar por
   capas (caché de coordenadas → OCR → modelo de visión) → pedir ayuda al humano si no lo
   consigue → aprender (guardar la nueva solución como skill).
4. **Web de control** (FastAPI + WebSocket) — lanzar tareas, ver la pantalla en directo con
   los clics marcados, línea de tiempo de pasos, aprobar/rechazar acciones del agente, y un
   panel de "modo caos" para forzar fallos.

## Stack

Python 3.12 (gestionado por `uv`), Tkinter, `pyautogui`, `mss`, OCR, LangGraph, Ollama,
FastAPI. Desarrollo en Windows.

## Hoja de ruta (commits pequeños, Conventional Commits)

### Fase 1 — GestCorp 98 (app legacy)

- [x] `chore:` inicializar proyecto con `uv`, `pyproject.toml`, `.gitignore`
- [x] `docs:` añadir `PROJECT.md` y `CLAUDE.md`
- [ ] `feat:` capa de datos SQLite (esquema `clientes` / `pedidos` / `facturas`) + seed de
      datos de prueba
- [ ] `feat:` ventana de login de GestCorp 98
- [ ] `feat:` ventana principal con `Notebook` y las 4 pestañas vacías
- [ ] `feat:` pestaña Clientes (listar + alta)
- [ ] `feat:` pestaña Pedidos (listar + crear pedido)
- [ ] `feat:` pestaña Facturación (listado, solo lectura por ahora)
- [ ] `feat:` pestaña Informes (mostrar un dato calculado, p. ej. total de ventas)

> Hueco reservado para más adelante: paquete `gestcorp98/chaos/` con el "modo caos"
> (controlado desde la web de la fase 4). No se crea nada todavía.

### Fase 2 — Tareas RPA objetivo (NO tocar aún)

- [ ] Definir y automatizar: alta de cliente
- [ ] Definir y automatizar: crear pedido
- [ ] Definir y automatizar: leer un dato de un informe

### Fase 3 — Agente LangGraph (NO tocar aún)

- [ ] Grafo base: ejecutar paso → verificar resultado
- [ ] Capa de recuperación 1: caché de coordenadas conocidas
- [ ] Capa de recuperación 2: OCR sobre la pantalla
- [ ] Capa de recuperación 3: modelo de visión local (Ollama)
- [ ] Punto de parada: pedir ayuda al humano si ninguna capa funciona
- [ ] Aprendizaje: guardar la solución encontrada como nueva "skill" reutilizable

### Fase 4 — Web de control (NO tocar aún)

- [ ] Backend FastAPI + WebSocket: lanzar tareas del agente
- [ ] Streaming de la pantalla en directo con los clics marcados
- [ ] Línea de tiempo de los pasos del agente
- [ ] Aprobar / rechazar acciones del agente desde la web
- [ ] Panel de "modo caos" (conectado al hueco reservado en `gestcorp98/chaos/`)

## Reglas de trabajo

Ver [`CLAUDE.md`](./CLAUDE.md).
