# Estimación de nuevas preguntas desde compendios

**Fecha de revisión:** 20 de julio de 2026  
**Alcance:** archivos Markdown incorporados directamente en `Procesado/`.

## Criterio de estimación

La cifra indicada es un **máximo razonable de preguntas nuevas y distintas**, no el número de frases que podría convertir mecánicamente en preguntas. Para estimarla se excluyeron:

- páginas y bloques repetidos por la extracción de PDF;
- bibliografías, objetivos introductorios y material administrativo;
- reformulaciones que evaluarían exactamente el mismo dato;
- contenidos ya cubiertos de forma equivalente por el banco actual;
- secuencias o parejas que no tienen un orden o correspondencia inequívocos.

La categoría **selección con alternativas** incluye preguntas de una respuesta correcta y, cuando el contenido lo permite, de varias respuestas correctas. Las preguntas genuinamente multirrespuesta no deberían superar aproximadamente el 10–15 % de esa categoría.

## Resultado por asignatura

| Asignatura | Activas actuales | Selección con alternativas | Ordenamiento | Emparejamiento | Máximo nuevo razonable | Total proyectado |
|---|---:|---:|---:|---:|---:|---:|
| Introducción al Derecho | 29 | 180 | 12 | 24 | **216** | 245 |
| Lógica y Dialéctica Jurídica | 20 | 150 | 10 | 22 | **182** | 202 |
| Teoría General del Estado y Sociología Jurídica | 30 | 160 | 18 | 26 | **204** | 234 |
| Expresión Oral y Redacción Jurídica | 93 | 75 | 8 | 18 | **101** | 194 |
| Historia y Filosofía del Derecho | 33 | 210 | 24 | 32 | **266** | 299 |
| Investigación | 140 | 120 | 18 | 28 | **166** | 306 |
| **Total** | **345** | **895** | **90** | **150** | **1.135** | **1.480** |

## Primera tanda recomendada

No conviene producir inmediatamente las 1.135 preguntas. Una primera tanda de **518 preguntas** permite revisar dificultad, ambigüedad y repetición antes de agotar todos los conceptos disponibles.

| Asignatura | Selección | Ordenamiento | Emparejamiento | Primera tanda |
|---|---:|---:|---:|---:|
| Introducción al Derecho | 80 | 6 | 10 | **96** |
| Lógica y Dialéctica Jurídica | 70 | 5 | 10 | **85** |
| Teoría General del Estado y Sociología Jurídica | 75 | 8 | 12 | **95** |
| Expresión Oral y Redacción Jurídica | 35 | 4 | 8 | **47** |
| Historia y Filosofía del Derecho | 95 | 10 | 15 | **120** |
| Investigación | 55 | 8 | 12 | **75** |
| **Total** | **410** | **41** | **67** | **518** |

## Observaciones por fuente

### Introducción al Derecho

- `texto_extraido_derecho_unemi.md` es una versión ordenada y útil de las unidades sobre negocios jurídicos, relaciones jurídicas, sistemas jurídicos, orden jurídico, fuentes y normatividad.
- `introduccion_al_derecho_texto_completo.md` no pertenece íntegramente a esta materia: las páginas 1–504 contienen Introducción al Derecho y desde la página 505 aparecen materiales de Expresión Oral y Redacción Jurídica.
- Antes de generar preguntas debe separarse el archivo por asignatura y deduplicarse frente a `texto_extraido_derecho_unemi.md`.

### Lógica y Dialéctica Jurídica

- El compendio presenta cuatro unidades, ocho temas y aproximadamente treinta y dos subtemas bien delimitados.
- Es especialmente apropiado para emparejar principios, falacias, autores y conceptos; y para ordenar el silogismo, la justificación y el juicio de proporcionalidad.

### Teoría General del Estado y Sociología Jurídica

- El archivo contiene alrededor de 200 páginas extraídas, pero solo unas 88 páginas son textualmente únicas.
- Hay unidades repetidas dos y hasta tres veces. Debe trabajarse sobre una copia deduplicada.
- El material ofrece buenas secuencias históricas y administrativas, además de relaciones entre actores, teorías, órganos y competencias.

### Expresión Oral y Redacción Jurídica

- `contenido_texto_juridico.md` es la fuente más limpia para comenzar.
- Las páginas 505–860 de `introduccion_al_derecho_texto_completo.md` contienen material adicional de esta asignatura, pero con mucha repetición.
- Como el banco actual ya tiene 93 preguntas activas y cubre gran parte de los mismos temas, el margen nuevo es menor que en las demás materias.

### Historia y Filosofía del Derecho

- Es el compendio con mayor expansión respecto del banco actual: desarrolla ocho unidades y numerosos procesos, escuelas, autores, tratados, fechas y evoluciones constitucionales.
- Es la materia con más potencial para ordenamiento cronológico y emparejamiento.
- Las fechas deben preguntarse solo cuando sean relevantes para comprender el proceso, evitando convertir el banco en memorización aislada.

### Investigación

- El compendio es amplio, ordenado y casi sin duplicación textual.
- Sin embargo, el banco actual ya contiene 140 preguntas y cubre 36 temas relacionados; por eso la estimación descuenta una superposición considerable.
- Los mejores contenidos nuevos son preguntas de aplicación: elegir técnica o instrumento, ordenar fases y relacionar métodos, variables, niveles de medición y tipos de muestreo.

## Reglas para la generación

1. Mantener el estilo de los simuladores conocidos: enunciado directo, distractores plausibles y una única interpretación defendible.
2. No crear una pregunta de ordenamiento si el compendio no establece expresamente una secuencia.
3. En emparejamiento, usar entre 3 y 5 parejas y evitar pistas gramaticales evidentes.
4. En selección multirrespuesta, indicar siempre cuántas respuestas deben elegirse o usar una instrucción inequívoca.
5. Incorporar explicación, clave para recordar, confusión común y justificación de los distractores.
6. Registrar unidad, tema, subtema y fragmento fuente para poder auditar cada respuesta.
7. Comparar semánticamente cada nueva pregunta con el banco existente antes de activarla.

## Prioridad sugerida

1. Historia y Filosofía del Derecho.
2. Teoría General del Estado y Sociología Jurídica.
3. Lógica y Dialéctica Jurídica.
4. Introducción al Derecho, después de separar el archivo mixto.
5. Investigación.
6. Expresión Oral y Redacción Jurídica.

La prioridad considera cuánto contenido nuevo aporta cada compendio frente al banco que ya está activo, no solo el tamaño del archivo.
