# Propuesta UX: preguntas y retroalimentación

**Fecha:** 19 de julio de 2026
**Alcance:** solo evaluación y propuesta. No se modificó código ni bancos de preguntas.
**Archivos revisados:** `prototipo/app/page.tsx`, `prototipo/app/globals.css`, `prototipo/public/questions.json`, `datos/subjects/DER101.json`, `DER 101 - Introducción al Derecho/Preguntas.md`.

**Datos verificados:** el banco de la aplicación contiene 346 preguntas, de las cuales 344 están activas (304 selección única, 21 completar, 11 emparejamiento, 4 selección múltiple, 3 ordenamiento, 1 verdadero/falso). DER101 tiene 28 activas. La pregunta manual DER101-M001 ("¿Qué es el sujeto del Derecho?") está pendiente de integración; al incorporarla, DER101 pasará a 29. Nota: el arreglo `subjects` en `page.tsx` tiene el total de DER101 escrito a mano (28), por lo que la integración exigirá actualizar ese número o, mejor, calcularlo desde el JSON.

---

## 1. Diagnóstico de la interfaz actual

La base es sólida: panel de pregunta con tarjeta, navegador lateral, barra de progreso, temporizador, tres tamaños de letra, tema claro y azul oscuro, y estados visuales para seleccionada/correcta/incorrecta con etiquetas de texto ("Correcta", "Tu respuesta") que no dependen solo del color. El flujo Comprobar → Siguiente es correcto y la respuesta correcta nunca se revela antes de comprobar.

Sin embargo, la retroalimentación —el corazón educativo del simulador— es el elemento más débil de la pantalla:

- Es un bloque plano con un solo párrafo (`feedback_correct` o `feedback_incorrect`), sin estructura: no reitera la alternativa correcta, no muestra lo que el estudiante marcó, no ofrece frase para recordar ni distinción de conceptos confundibles.
- Es el texto más pequeño de la pantalla (0.7em ≈ 11 px), cuando debería ser el contenido con mayor jerarquía tras responder.
- Aparece al final del panel, debajo de todas las alternativas, lo que obliga a desplazarse cuando el enunciado o las opciones son largas (hay enunciados de hasta 725 caracteres y opciones de hasta 258).
- El consejo desaparece al comprobar (`tipsEnabled && !isSubmitted`), impidiendo contrastar la pista con la explicación.

Otros hallazgos relevantes del código:

- **Ordenamiento:** el orden inicial es el orden correcto invertido (`[...ordered_items].reverse()`), un patrón predecible que un estudiante puede explotar. Debe barajarse aleatoriamente.
- **Selección múltiple:** se ve idéntica a la selección única (mismos botones, misma letra en recuadro). Nada indica que se puede marcar más de una opción.
- **Emparejamiento:** no hay forma de deshacer una asignación, y tras comprobar no se marca qué pares quedaron bien o mal; solo aparece el bloque genérico de retroalimentación.
- **Completar (fill_blank):** se renderiza como selección única con opciones; funciona, pero el tipo declarado no coincide con lo que ve el estudiante.
- **Accesibilidad:** las alternativas son botones sin semántica de grupo (`radiogroup`/`aria-checked`), la retroalimentación no se anuncia (`aria-live`) ni recibe foco, y no hay atajos de teclado (flechas, letras A–D, Enter para comprobar).
- **Móvil:** bajo 560 px se ocultan los conmutadores de Consejos/Retroalimentación, los botones de tamaño de letra y el enlace "Salir del intento", perdiendo funciones en el dispositivo donde más se usará.
- **Longitud de línea:** el panel permite ~840 px de ancho de texto (~95–100 caracteres por línea), por encima del rango cómodo de lectura (60–80).

## 2. Problemas principales, por importancia

1. **Retroalimentación pobre y sin estructura** (impacto educativo directo): un párrafo genérico, letra minúscula, sin alternativa correcta explícita, sin respuesta del estudiante, sin frase memorable.
2. **Jerarquía tipográfica invertida tras responder:** lo más importante (la explicación) es lo más pequeño; el enunciado en 1.65em domina incluso después de contestar.
3. **Orden inicial predecible en preguntas de ordenamiento** (compromete la validez de ese tipo de pregunta).
4. **Selección múltiple indistinguible de selección única.**
5. **Desplazamiento excesivo para leer la retroalimentación** en preguntas largas.
6. **El consejo desaparece al comprobar**, rompiendo el ciclo pista → intento → explicación.
7. **Accesibilidad incompleta:** sin roles ARIA, sin `aria-live`, sin navegación por teclado más allá de Tab.
8. **Pérdida de funciones en móvil** (toggles, tamaños de letra, salir del intento).
9. **Emparejamiento sin corrección visual por par ni forma de deshacer.**
10. **Líneas de texto demasiado largas en escritorio.**
11. **Totales de materias escritos a mano en `page.tsx`**, propensos a desincronizarse del banco (relevante al pasar DER101 a 29).

## 3. Propuesta visual: bloque de pregunta y alternativas

**Jerarquía descendente clara:**

- Fila superior de metadatos en una sola línea discreta: `TEMA · Pregunta 4 de 10` (10–11 px, mayúsculas, color primario apagado). El tema a la izquierda, el contador a la derecha, como ahora, pero unificando color para no competir con el enunciado.
- Enunciado como único elemento grande: serif 1.35–1.5em (reducir del 1.65em actual), interlineado 1.45, ancho máximo de texto **68–72 caracteres** (`max-width: 68ch`) centrado en el panel. En enunciados de más de ~400 caracteres, reducir automáticamente a 1.2em (clase condicional por longitud).
- Un chip pequeño junto a los metadatos que indique el tipo de pregunta cuando no sea selección única: "Selecciona todas las que correspondan", "Verdadero o falso", "Ordena los elementos", "Empareja los conceptos". Elimina la ambigüedad del punto 4 del diagnóstico.

**Alternativas:**

- Mantener la tarjeta-botón actual (funciona bien) con ajustes: separación vertical de 10 a 12 px, altura mínima 56 px, radio 12 px.
- Letra A/B/C/D en recuadro de 32 px, alineada arriba (no centrada verticalmente) cuando el texto ocupe más de una línea, para que en opciones largas la letra quede junto a la primera línea.
- Texto de la opción a 0.95em (subir del 0.82em actual): las alternativas son contenido primario, no secundario.
- En selección múltiple, sustituir el recuadro de letra por una casilla cuadrada con marca de verificación; en única, mantener recuadro (o círculo tipo radio). La forma comunica el modo sin leer instrucciones.
- Estados: normal (borde neutro), hover (borde primario, sin trasladar el botón: el `translateX(2px)` actual mueve el objetivo del puntero), seleccionada (borde primario 2 px + fondo primario 8 %), correcta (borde verde + fondo verde 10 % + etiqueta "Correcta"), incorrecta seleccionada (borde rojo + fondo rojo 8 % + etiqueta "Tu respuesta"). Tras comprobar, atenuar las opciones no relevantes (opacidad 0.55) para que el ojo vaya a la correcta y a la marcada.
- Verde y rojo solo tras comprobar, y siempre acompañados de texto e icono (✓/✗ en el recuadro de la letra), nunca color solo.

**Teclado:** teclas A–D (o 1–9) seleccionan opción, flechas ↑/↓ mueven el foco, Enter comprueba si hay respuesta completa, → pasa a la siguiente tras comprobar. Roles `radiogroup`/`group` con `aria-checked` en las opciones.

## 4. Propuesta: respuesta correcta

Tarjeta de retroalimentación estructurada (ver sección 9 para su posición), con borde y franja superior verdes, icono ✓ y este contenido en orden:

1. **Confirmación breve:** "¡Correcto!" en 1em, seminegrita, verde oscuro accesible (no el verde del borde).
2. **Alternativa correcta reiterada:** "A. Toda persona o entidad con derechos y obligaciones." en una línea propia, seminegrita.
3. **Explicación** (2–3 oraciones, 0.95em, interlineado 1.6): por qué es correcta, con la idea complementaria integrada.
4. **Frase para recordar**, visualmente diferenciada (fondo neutro suave, icono 💡 o etiqueta "Para recordar:"): una sola oración.
5. **Distinción de conceptos confundibles**, solo cuando exista en los datos: "No confundir con: …" en una línea.

Todo el texto de la tarjeta a 0.9–0.95em como mínimo: la explicación nunca más pequeña que las alternativas.

## 5. Propuesta: respuesta incorrecta

Misma tarjeta con franja roja moderada (el rojo actual `#c94d5b` es adecuado; evitar rojos saturados) e icono neutro (✗ fino, no alarmante):

1. **Indicación respetuosa:** "Esta vez no es correcto." — sin mayúsculas gritadas ni "¡Incorrecto!".
2. **Tu respuesta:** "B. Solo las personas naturales." (la marcada por el estudiante, en gris/rojo suave).
3. **Respuesta correcta:** "A. Toda persona o entidad con derechos y obligaciones." destacada en verde/seminegrita.
4. **Por qué es correcta** (2–3 oraciones).
5. **Por qué tu opción no corresponde** (1–2 oraciones específicas de la opción elegida cuando exista `why_options_are_wrong`; genérica si no).
6. **Frase para recordar**, con el mismo tratamiento visual que en la respuesta correcta.

La tarjeta se limita a ~120 palabras en total; si los datos traen más texto, se prioriza explicación + frase y se colapsa el resto bajo "Ver más".

## 6. Propuesta: consejos opcionales

- Mantener la caja dorada actual antes de comprobar, pero **colapsada por defecto**: una línea "💡 Consejo disponible" que se expande al tocarla. Reduce ruido y evita que el consejo condicione la lectura del enunciado.
- **No ocultarlo tras comprobar:** conservarlo visible (colapsado) para poder contrastar pista y explicación.
- Diferenciación clara con la retroalimentación: el consejo es **antes** de responder, dorado, discreto, opcional; la retroalimentación es **después**, verde/roja, protagonista. Nunca deben verse iguales ni ocupar la misma zona con el mismo estilo.
- El conmutador "Consejos" del lateral se conserva; quien lo desactiva no ve ni la línea colapsada.

## 7. Comportamiento recomendado en escritorio y móvil

**Escritorio (≥ 840 px):**

- Conservar la estructura de dos columnas (navegador + panel). Limitar el texto a 68–72 caracteres por línea dentro del panel.
- Al comprobar, la tarjeta de retroalimentación aparece **sin desplazar la pantalla completa**: se inserta con una transición suave y el panel hace scroll automático mínimo (`scrollIntoView({block:"nearest"})`) solo si la tarjeta queda fuera de vista; el foco se mueve a la tarjeta (`tabindex="-1"` + `focus()`), lo que además la anuncia con `aria-live="polite"`.
- Botonera fija en la parte baja del panel (posición `sticky`): "Anterior" a la izquierda; "Comprobar" (primario) que se transforma en "Siguiente" tras comprobar. Mostrar "Siguiente" inmediatamente después de responder es lo recomendado, pero **sin avanzar automáticamente**: el estudiante decide cuándo terminó de leer la explicación. Con retroalimentación desactivada (modo examen), se mantiene el comportamiento actual: solo navegación, sin comprobar por pregunta.
- Cuando "Comprobar" está deshabilitado, un microtexto al lado lo explica ("Selecciona una opción para comprobar" / "Completa todos los pares…").

**Móvil (< 840 px):**

- Restaurar en pantallas pequeñas lo que hoy se oculta: tamaños de letra y toggles pueden vivir en un menú de tres puntos en la barra superior; "Salir del intento" siempre accesible desde ese mismo menú.
- La tarjeta de retroalimentación aparece como **hoja inferior (bottom sheet)** deslizante anclada al fondo, con la botonera integrada ("Siguiente" dentro de la hoja). Evita perder el contexto de la pregunta y el desplazamiento largo.
- Alternativas a ancho completo, altura mínima táctil 48 px, separación 10 px.
- En emparejamiento, mantener el modo tocar-origen → tocar-destino (ya existe) y añadir botón para deshacer cada par.
- Botonera `sticky` al fondo con fondo del panel para que "Comprobar" siempre esté visible sin buscarlo.

## 8. Ejemplo completo: "¿Qué es el sujeto del Derecho?"

**Antes de responder:**

> SUJETO DEL DERECHO · PREGUNTA 5 DE 10
>
> **¿Qué es el sujeto del Derecho?**
>
> 💡 Consejo disponible *(colapsado; al expandir: "Piensa en quién puede ser titular de un derecho o estar obligado a cumplir un deber jurídico.")*
>
> - [A] Toda persona o entidad con derechos y obligaciones.
> - [B] Solo las personas naturales.
> - [C] Los abogados.
> - [D] El Estado exclusivamente.
>
> `Anterior` · `Comprobar` (deshabilitado hasta seleccionar)

**Si responde A (correcto):**

> ✓ **¡Correcto!**
>
> **A. Toda persona o entidad con derechos y obligaciones.**
>
> El sujeto del Derecho es toda persona o entidad reconocida por el ordenamiento jurídico como titular de derechos y obligaciones. Esto comprende tanto a las personas naturales como a las personas jurídicas.
>
> 💡 **Para recordar:** si puede tener un derecho o asumir una obligación, puede ser sujeto del Derecho.
>
> **No confundir con:** el *objeto* del Derecho, que es aquello sobre lo que recaen los derechos y obligaciones.
>
> `Anterior` · `Siguiente`

**Si responde B (incorrecto):**

> ✗ **Esta vez no es correcto.**
>
> Tu respuesta: B. Solo las personas naturales.
> Respuesta correcta: **A. Toda persona o entidad con derechos y obligaciones.**
>
> El sujeto del Derecho no se limita a las personas naturales: también incluye personas jurídicas y otras entidades reconocidas por la ley. La opción B es incompleta porque excluye a las personas jurídicas.
>
> 💡 **Para recordar:** sujeto del Derecho es quien puede tener derechos y obligaciones.
>
> `Anterior` · `Siguiente`

*Nota: los textos de explicación y distinción de este ejemplo siguen la retroalimentación ya registrada en `Preguntas.md`; la frase sobre el "objeto del Derecho" es una recomendación de contenido pendiente de validación académica antes de integrarse al banco.*

## 9. Wireframe textual de la pantalla propuesta (escritorio)

```
┌──────────────────────────────────────────────────────────────────┐
│ Simulador de examen final   DER 101 · Introducción   [A A A][🌓][⏱ 58:12] │
├──────────────────────────────────────────────────────────────────┤
│ ██████████████░░░░░░░░░░  (progreso)                             │
├──────────────┬───────────────────────────────────────────────────┤
│ PREGUNTAS 5/10│  SUJETO DEL DERECHO          PREGUNTA 5 DE 10    │
│ [1][2][3][4] │                                                   │
│ [5][6][7][8] │  ¿Qué es el sujeto del Derecho?      (≤68ch)      │
│ [9][10]      │                                                   │
│              │  ▸ 💡 Consejo disponible                          │
│ ☑ Consejos   │                                                   │
│ ☑ Retroalim. │  [A] Toda persona o entidad con derechos…  ✓ Correcta │
│              │  [B] Solo las personas naturales.       ✗ Tu respuesta │
│ Salir del    │  [C] Los abogados.                    (atenuada)  │
│ intento      │  [D] El Estado exclusivamente.        (atenuada)  │
│              │  ┌─────────────────────────────────────────────┐  │
│              │  │ ✗ Esta vez no es correcto.                  │  │
│              │  │ Tu respuesta: B · Correcta: A               │  │
│              │  │ Explicación (2–3 oraciones)…                │  │
│              │  │ 💡 Para recordar: …                          │  │
│              │  └─────────────────────────────────────────────┘  │
│              │ ─────────────────────────────────────────────────│
│              │  [ Anterior ]                      [ Siguiente ]  │ ← sticky
└──────────────┴───────────────────────────────────────────────────┘
```

En móvil, la columna izquierda pasa arriba como tira horizontal de números, y la tarjeta de retroalimentación se presenta como hoja inferior con "Siguiente" integrado.

## 10. Cambios técnicos posteriores

**`page.tsx`:**

- Extraer la tarjeta de retroalimentación a un componente `FeedbackCard` que reciba la pregunta, la respuesta del estudiante y el resultado, y renderice los campos estructurados con degradación a `feedback_correct`/`feedback_incorrect` cuando no existan.
- Corregir `orderingItems`: inicializar con barajado aleatorio estable por intento (guardar el orden barajado en el estado al montar la pregunta), nunca `reverse()` del orden correcto.
- Añadir chip de tipo de pregunta y casillas cuadradas para selección múltiple.
- Mantener el consejo visible (colapsado) tras comprobar; convertirlo en `<details>` o estado colapsable.
- Foco y `aria-live` en la tarjeta de retroalimentación; roles `radiogroup`/`aria-checked` en alternativas; atajos de teclado (A–D, flechas, Enter).
- Marcado por par en emparejamiento tras comprobar (verde/rojo por fila) y botón de deshacer par.
- Botonera `sticky`; microtexto junto a "Comprobar" deshabilitado.
- Menú móvil con tamaños de letra, toggles y "Salir del intento".
- Calcular los totales de materias desde `questions.json` en lugar del arreglo manual (evita desincronización al pasar DER101 a 29).

**`globals.css`:**

- Nueva escala tipográfica del panel: enunciado 1.35–1.5em (1.2em si es extenso), opciones 0.95em, retroalimentación ≥ 0.9em, metadatos 0.65em.
- `max-width: 68ch` para enunciado, opciones y retroalimentación.
- Estilos de `FeedbackCard` (franja superior de color, secciones internas, bloque "Para recordar"), estados atenuados post-comprobación, casilla de selección múltiple, hoja inferior móvil (`@media (max-width: 840px)`), botonera sticky.
- Eliminar `translateX` en hover de alternativas.
- Revisar contraste del tema oscuro para los nuevos verdes/rojos de la tarjeta (usar variantes con contraste ≥ 4.5:1 sobre el fondo `--panel-solid`).

**`questions.json` / `datos/subjects/*.json`:**

- Añadir campos opcionales estructurados (sección 11) sin romper el esquema actual; conservar `feedback_correct`/`feedback_incorrect` como respaldo.

## 11. Campos de datos: ¿bastan los actuales?

`feedback_correct`, `feedback_incorrect` y `tip` no son suficientes para la retroalimentación estructurada propuesta: obligan a redactar párrafos monolíticos, no permiten reaccionar a la opción concreta que marcó el estudiante y mezclan explicación, refuerzo y mnemotecnia en un solo texto.

Recomendación — añadir campos **opcionales**:

- `explanation`: por qué la alternativa correcta es correcta (2–3 oraciones). Se usa en ambos resultados.
- `memory_key`: frase corta para recordar. Se muestra en el bloque "Para recordar".
- `common_confusion`: distinción frente a conceptos que suelen confundirse. Se muestra solo si existe.
- `why_options_are_wrong`: objeto `{ "B": "…", "C": "…", "D": "…" }` con la razón específica de cada distractor. Permite que la tarjeta de respuesta incorrecta explique exactamente la opción marcada.

Reglas de compatibilidad: si `explanation` existe, la tarjeta usa los campos nuevos y trata `feedback_correct`/`feedback_incorrect` como respaldo; si no, muestra el texto legado como hasta ahora. Así se pueden migrar las 344 preguntas gradualmente, empezando por DER101. `tip` se conserva tal cual. La redacción del contenido de estos campos para las preguntas existentes es trabajo académico pendiente de validación; no debe generarse automáticamente sin revisión.

## 12. Plan de implementación en pasos pequeños y verificables

Cada paso es independiente, se puede probar en el navegador antes de continuar y no requiere el siguiente.

1. **Tipografía y medidas** (`globals.css`): nueva escala, `68ch`, quitar `translateX`. Verificar: legibilidad en los 3 tamaños de letra y ambos temas, sin desbordes.
2. **Barajado del ordenamiento** (`page.tsx`): orden inicial aleatorio persistente por intento. Verificar: dos intentos muestran órdenes distintos y nunca el correcto ni su inverso; comprobar sigue calificando bien.
3. **Distinción de selección múltiple**: casillas + chip de tipo. Verificar: las 4 preguntas de selección múltiple activas se distinguen a simple vista; la calificación no cambia.
4. **Componente `FeedbackCard` con campos legados**: misma información de hoy, nueva presentación (título, alternativa correcta, tu respuesta, explicación). Verificar: respuestas correctas e incorrectas en los 5 tipos de pregunta, ambos temas.
5. **Esquema de datos**: añadir los 4 campos opcionales al esquema y a `FeedbackCard` con degradación. Verificar: preguntas sin campos nuevos se ven igual que en el paso 4.
6. **Piloto DER101**: redactar los campos nuevos para las 28 preguntas (validación académica del docente/autor antes de cargar) e integrar DER101-M001 con la estructura completa, actualizando ambos bancos y el total (28 → 29, y 344 → 345 en la app). Verificar: conteos, y que la nueva pregunta aparece y califica bien.
7. **Consejo persistente y colapsable**. Verificar: colapsado por defecto, visible tras comprobar, desaparece con el toggle apagado.
8. **Accesibilidad**: roles, `aria-live`, foco a la tarjeta, atajos de teclado. Verificar: recorrido completo de un intento solo con teclado; lector de pantalla anuncia el resultado.
9. **Botonera sticky + microtexto de "Comprobar"**. Verificar: visible sin scroll en preguntas largas, escritorio y móvil.
10. **Hoja inferior móvil + menú de opciones móvil**. Verificar en 360–560 px: tamaños de letra, toggles y salida accesibles; retroalimentación legible sin perder la pregunta.
11. **Emparejamiento**: corrección por par y deshacer. Verificar con las 11 preguntas de emparejamiento activas.
12. **Totales dinámicos por materia** desde `questions.json`. Verificar: las tarjetas del catálogo muestran 29 para DER101 sin tocar código.

---

*Ninguna afirmación jurídica nueva de este documento (p. ej., la distinción sujeto/objeto del Derecho) debe incorporarse al banco sin validación académica previa.*
