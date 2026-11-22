# Agente + visión + RPA: cómo llegamos al flujo completo

Registro de lo que hemos construido y, sobre todo, **lo que hemos aprendido** hasta conseguir
que un agente haga de principio a fin una tarea real en GestCorp 98 y que esa ejecución se
convierta en un **RPA determinista** que la repite sin IA.

> Estado a 2026-11-22: flujo completo conseguido. El agente inicia sesión, da de alta un
> cliente, crea un pedido (con dos desplegables) y verifica cada formulario antes de enviarlo.
> De su grabación sale `experiments/flujos/flujo_20261122_181730.json`, que se reproduce con
> `pyautogui` puro, sin agente ni visión.

Código: `experiments/agentic_pipeline.ipynb` (tools, agente, extracción y reproducción) y
`experiments/vision_tools.py` (UI-TARS). Prompt de ejemplo: `experiments/prompts/login_alta_cliente.txt`.

---

## 1. La idea en una imagen

```
 instrucción en lenguaje natural (user prompt)
        │
        ▼
 ┌──────────────────────────────┐      decide QUÉ hacer y lo DESCRIBE
 │ Agente orquestador (LLM)     │      ("el botón Entrar en la ventana de login")
 │ gpt-oss-120b en Groq         │
 └──────────────┬───────────────┘
                │ llama a una tool
                ▼
 ┌──────────────────────────────┐      hace el CÓMO, siempre igual (determinista):
 │ Tool (Python)                │      captura → UI-TARS localiza → pyautogui actúa
 │ pulsar / rellenar_campo / …  │      y devuelve las acciones físicas con coordenadas
 └──────────────┬───────────────┘
                │ antes de enviar un formulario
                ▼
 ┌──────────────────────────────┐      UI-TARS SOLO LEE cada campo,
 │ Verificación determinista    │      Python compara con lo pedido → SI / NO + qué corregir
 └──────────────┬───────────────┘
                │ al terminar
                ▼
 grabación (mensajes) → extraer pasos → flujo JSON → RPA puro (sin IA, mucho más rápido)
```

El reparto de papeles es la clave de todo lo demás:

| Quién | Qué hace | Qué NO hace |
|---|---|---|
| LLM orquestador | Lee la instrucción, decide el siguiente paso, describe el elemento | No calcula coordenadas, no "imagina" resultados |
| UI-TARS | Localiza un elemento descrito / lee lo que hay en un campo | No conoce la app ni el objetivo; no compara |
| Código de las tools | Clic, escribir, borrar, abrir desplegables, comparar valores | No decide nada |
| RPA final | Repite las acciones grabadas | No usa IA |

---

## 2. Visión: por qué UI-TARS y cómo usarlo bien

Se evaluaron varios enfoques en `experiments/vision_evaluation.ipynb` contra un ground truth
real. Resumen:

- **qwen2.5vl (Ollama)**: descartado. Usa su propio formato de coordenadas y no se puede saber
  a qué resolución redimensionó la imagen.
- **RapidOCR**: bueno para botones con texto, pero no sirve para campos vacíos. Para *leer*
  campos también falló (leía `"seon]"` donde ponía `"Lucas"`).
- **OmniParser**: cajas muy precisas, pero su captioner (Florence-2) no sirve para saber qué
  caja es cuál.
- **UI-TARS-7B-DPO**: el elegido. Localiza muy bien y además **entiende preguntas** sobre la
  pantalla, así que sirve también para verificar.

Detalles que hay que respetar (están en `vision_tools.py`):

- **Escala 0-1000.** UI-TARS devuelve coordenadas relativas de 0 a 1000 sobre la imagen
  *original*: `x = x_rel / 1000 * ancho`. No hay que reconstruir ningún tamaño interno.
- **DPI awareness en Windows** antes de usar `mss`/`pyautogui`. Sin esto, las coordenadas de
  la captura y las del ratón no coinciden 1:1.
- **Capturar solo la ventana de la app** (`fijar_region_captura`). Si ve también el notebook,
  puede localizar o leer texto de ahí.
- **Siempre entero en la GPU** (`device_map="cuda:0"`, no `"auto"`). Con `"auto"`, si falta
  VRAM, manda capas a la CPU sin avisar y cada inferencia se vuelve lentísima. Mejor que falle
  con un error claro.
- **Precargar el modelo** antes de abrir la app, para no esperar a mitad de la automatización.

---

## 3. Optimización de las tools: meter lo determinista dentro

### Antes

El agente encadenaba pasos sueltos: localizar → clic → escribir → comprobar… Cada paso era
una llamada al LLM (muchos tokens) y una ocasión más de equivocarse (por ejemplo, escribir
sin haber hecho clic en el campo).

### Ahora: tools "empaquetadas"

Cada tool hace **por dentro, siempre igual**, toda la secuencia física. El LLM solo dice
**qué** elemento y **dónde** está; el **cómo** es código.

| Tool | Qué hace por dentro |
|---|---|
| `pulsar(descripcion)` | localizar → clic |
| `rellenar_campo(descripcion, texto)` | localizar → clic → `End` → pegar el texto |
| `borrar_campo(descripcion)` | localizar → clic → `End` → 50 × `Backspace` |
| `seleccionar_en_desplegable(desplegable, opcion)` | localizar el desplegable → clic (abre la lista) → captura nueva → localizar la opción "en la lista abierta" → clic |
| `verificar_alta_cliente(...)`, `verificar_pedido(...)` | leer campo a campo con UI-TARS y comparar en Python (ver §4) |

Cada tool de acción devuelve un JSON con `resultado` (texto para el agente) y `acciones` (lo
que hizo físicamente, con coordenadas). **De ahí sale después el RPA.**

### Trucos aprendidos a base de fallos

- **Pegar en vez de teclear.** `pyautogui.typewrite` se salta en silencio los caracteres que no
  conoce (tildes, ñ…). Se copia al portapapeles (`pyperclip`) y se pega con `Ctrl+V`.
- **Borrar con `End` + `Backspace`, no con `Shift+Home`.** En Windows, `pyautogui` manda `Home`
  como tecla del teclado numérico y, con Bloq Num activado, Windows suelta el `Shift` y no
  selecciona nada.
- **El desplegable es una sola tool.** Solo la tool sabe que la lista acaba de abrirse, así que
  ella misma busca la opción "dentro de la lista desplegable que está abierta". El agente no
  tiene que coordinar dos pasos.
- **Sin umbrales numéricos puestos a ojo.** Hubo una comprobación de "la opción tiene que estar
  a menos de N píxeles del desplegable" y se quitó. Un número elegido a dedo funciona en una
  pantalla y falla en otra.
- **Los docstrings son el manual del LLM.** Es lo que lee para decidir qué tool usar y cuándo,
  así que tienen que ser claros y cortos.

---

## 4. Verificación determinista: UI-TARS lee, Python decide

Antes de pulsar "Añadir cliente" o "Crear pedido", el agente llama a la tool de verificar con
los valores que le pidió el usuario:

1. Para **cada campo**, UI-TARS recibe la captura de la ventana y una frase que completa con lo
   que hay escrito.
2. **Python** normaliza la respuesta (espacios, comillas, la etiqueta si la copia, "VACIO") y la
   **compara** con lo pedido, sin distinguir mayúsculas.
3. La tool devuelve `SI` o `NO` y, por campo, `BIEN` o `MAL`. Si está mal, dice qué hay escrito
   y **cómo corregirlo**: en un campo de texto, `borrar_campo` y luego `rellenar_campo`; en un
   desplegable, `seleccionar_en_desplegable` otra vez.
4. El system prompt obliga: **nunca enviar un formulario sin un `SI` justo antes**. Si sale `NO`,
   se corrige solo lo marcado y se vuelve a verificar.

Por qué así:

- **A UI-TARS no se le da el valor esperado.** Si le preguntas "¿pone 12345?", tiende a darte la
  razón. Solo lee; la comparación es código, y el código no se deja convencer.
- **Cada respuesta original de UI-TARS se imprime** (`[UI-TARS] … -> '12345'`). Cuando algo falla,
  lo primero es ver qué leyó de verdad, no solo el resultado ya limpio.

---

## 5. La importancia de los prompts

Hay **tres** prompts distintos, y cada uno tiene sus reglas.

### 5.1 Preguntas a UI-TARS: cortas, sin suponer lugares

Esta fue **la lección más importante** de la verificación. La versión antigua para leer un
campo era:

```
En la parte de abajo de la ventana está el formulario 'Alta de cliente'. Mira el hueco blanco
de texto que está justo a la derecha de la etiqueta 'NIF:' de ese formulario (no la tabla de
clientes de arriba). ¿Qué texto hay escrito literalmente ahí? ...
```

Con ella, UI-TARS leía el **NIF como vacío** aunque el agente lo había escrito bien (lo
comprobamos por las coordenadas y a ojo). El agente borraba, volvía a escribir y la
verificación seguía diciendo `MAL`. Era un bucle sin salida. Los motivos:

- **"Hueco blanco"** le hace buscar un espacio *vacío*. Pero el campo ya está relleno, así que
  busca otro hueco: en la tabla de arriba hay espacio en blanco entre columnas, y la columna NIF
  está más separada de Email.
- **"Justo a la derecha de la etiqueta…"** sobra. UI-TARS ya localiza bien los campos por su
  nombre; las indicaciones de posición solo le añaden cosas que interpretar.
- **"(no la tabla de clientes de arriba)"** le nombra justo lo que no debe mirar.

La versión que funciona:

```
Responde solo con el texto que hay escrito, sin comillas ni explicaciones. Si no hay nada escrito, responde VACIO.
En la parte de abajo, en "Alta de cliente", el campo "NIF" es:
```

Reglas que salen de aquí:

1. **Zona + nombre del campo, y nada más.** Sin "hueco", sin "a la derecha de", sin negaciones.
2. **Frase para completar** ("el campo X es:") en vez de pregunta abierta.
3. **No suponer el estado.** No decir "hueco blanco" si a lo mejor ya hay texto.
4. **No darle la respuesta esperada.**
5. **Desconfiar y comprobar el texto literal.** Ante una duda, ejecutar el código real e imprimir
   exactamente lo que recibe UI-TARS.

### 5.2 Descripciones para localizar (las escribe el LLM)

El modelo de visión no conoce la app ni el objetivo: solo ve la captura. Por eso, en
`descripcion` el agente pone **tipo de elemento + nombre o etiqueta + zona**, sacados del user
prompt. Por ejemplo: `campo NIF en el formulario Alta de cliente` o
`pestaña Pedidos en la barra superior`. Nombrar la zona evita que lo confunda con el mismo texto
en otro sitio, como una cabecera de tabla.

### 5.3 User prompt: el orden importa

El user prompt lo escribe el usuario (`experiments/prompts/`) y es lo que cambia de una app a
otra. Una ejecución falló porque el agente **pulsó "Entrar" antes de escribir la contraseña**:
la frase "Escribe admin en Contraseña y pulsa Entrar" no dejaba el orden lo bastante claro. Con
**"Primero escribe… y luego pulsa…"** lo hizo bien.

Lección: los pasos tienen que estar **en orden explícito**. El agente no ve la pantalla entre
acciones; si se equivoca de orden, no se entera.

### 5.4 System prompt: el método, genérico y corto

- Explica el **método** (cómo describir elementos, qué tool para qué, cuándo verificar y cómo
  corregir), no los pasos concretos de una app.
- **"Actúa solo con tools":** nunca escribir en texto una acción ni inventarse su resultado.
- **Corto**, porque se reenvía en *cada* paso del agente y los tokens cuentan para el límite
  diario de Groq.

---

## 6. El bucle del agente

- **LangChain v1 `create_agent`** (LangGraph por debajo) con `ChatGroq`
  (`openai/gpt-oss-120b`, `temperature=0`, `reasoning_effort="low"` para gastar menos tokens).
- **`agent.stream`** en vez de `invoke`, para ver cada tool y su resultado en cuanto ocurre.
- **Reanudaciones.** Si el agente para sin escribir su `RESUMEN FINAL`, o si Groq rechaza una
  respuesta mal formada, se le dice "continúa con el siguiente paso pendiente" con todo el
  historial (hasta 5 veces).
- **Límite de Groq:** unos 200 000 tokens/día por modelo. Una ejecución completa con
  verificaciones gasta una parte importante.

---

## 7. De la grabación del agente al RPA determinista

La lista de mensajes del agente es una **grabación** de toda la ejecución. De ella se extrae un
flujo fijo (celda "Del agente al RPA determinista"):

1. Se recorren las tools de acción y se toman sus `acciones` con coordenadas. Las verificaciones
   no pasan al flujo, porque el RPA no tiene visión.
2. Las coordenadas se guardan **relativas a la ventana** (no a la pantalla), junto con el tamaño
   de la ventana.
3. **Limpieza:**
   - cada escritura se reproduce como "borrar + escribir", así que los `borrar_campo` del agente
     sobran;
   - si un campo se escribió varias veces (una corrección tras verificar), **solo vale la última**;
   - dos clics idénticos seguidos cuentan como uno.
4. Cada grabación se guarda en su propio `experiments/flujos/flujo_AAAAMMDD_HHMMSS.json`, con la
   instrucción original. Nunca se sobrescriben.

Ejemplo de paso:

```json
{ "accion": "escribir", "elemento": "campo NIF en el formulario Alta de cliente",
  "x": 535, "y": 1358, "texto": "12345" }
```

**Reproducción:** se cierra la app (sin tocar la base de datos), se abre en la mitad derecha
**con el mismo tamaño de ventana** y se ejecutan los pasos con `pyautogui`, con una pausa tras
cada clic para que la UI reaccione. No usa el agente ni UI-TARS, así que va mucho más rápido.

---

## 8. Límites conocidos y siguientes pasos

- **El RPA depende del tamaño y la posición relativa de la ventana.** Si la app cambia de
  diseño, hay que volver a grabar (o, más adelante, que el RPA pida ayuda a la visión cuando un
  paso falle: fase 4 de `PROJECT.md`).
- **Las tools de verificar son específicas de GestCorp** (nombres de formularios y campos fijos).
  Pendiente: una verificación genérica a la que el agente le pase formulario, campo y valor.
- **La sección TERMINAR del system prompt** todavía nombra "Crear pedido". Hay que dejarla
  genérica.
- **Ahorro de tokens:** sacar las coordenadas del resultado que ve el agente
  (`registro_acciones`), porque al LLM no le sirven y se reenvían en cada paso.
- **El agente sin "ojos" entre acciones:** las tools de acción no dicen si la pantalla cambió.
  Una idea es comparar la captura de antes y la de después del clic (iguales o distintas, sin
  umbral).
- **Conectar el agente a la plataforma web** (`plataforma/`). Hoy la web ejecuta los robots
  grabados y el agente vive en el notebook.
