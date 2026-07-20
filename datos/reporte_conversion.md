# Reporte de Conversión — Bancos Markdown → JSON

Fecha de conversión inicial: 14 de julio de 2026
Última actualización: 19 de julio de 2026
Conversión técnica: no se revisaron PDF, no se cambiaron respuestas académicas y no se modificó ningún banco Markdown.

## Archivos leídos

1. `Procesado/DER 101 - Introducción al Derecho/banco_preguntas.md`
2. `Procesado/DER 102 - Lógica y Dialéctica Jurídica/banco_preguntas.md`
3. `Procesado/DER 104 - Teoría General del Estado y Sociología Jurídica/banco_preguntas.md`
4. `Procesado/DER 105 - Expresión Oral y Redacción Jurídica/banco_preguntas.md`
5. `Procesado/DER 106 - Historia y Filosofía del Derecho/banco_preguntas.md`
6. `Procesado/C10 - Investigación/banco_preguntas.md`

Nota: la entrada manual DER101-M001 fue validada e integrada como `DER101-P029`.

## Archivos generados

- `scripts/convert_banks.py` (conversor reproducible, solo biblioteca estándar, rutas relativas)
- `scripts/validate_questions.py` (validador)
- `datos/question.schema.json` (esquema JSON, draft-07)
- `datos/questions.json` (consolidado)
- `datos/subjects/DER101.json`, `DER102.json`, `DER104.json`, `DER105.json`, `DER106.json`, `C10.json`
- `datos/reporte_conversion.md` (este archivo)

## Total convertido

- **347 preguntas** (coincide con el total esperado)

## Conteo por asignatura

| Asignatura | Esperado | Convertido |
|---|---|---|
| DER101 — Introducción al Derecho | 29 | 29 |
| DER102 — Lógica y Dialéctica Jurídica | 20 | 20 |
| DER104 — Teoría General del Estado y Sociología Jurídica | 30 | 30 |
| DER105 — Expresión Oral y Redacción Jurídica | 95 | 95 |
| DER106 — Historia y Filosofía del Derecho | 33 | 33 |
| C10 — Investigación | 140 | 140 |

## Conteo por tipo de pregunta

| Tipo | Cantidad |
|---|---|
| single_choice | 307 |
| fill_blank | 21 |
| matching | 11 |
| multiple_choice | 4 |
| ordering | 3 |
| unknown | 0 |
| true_false | 1 |

## Preguntas activas e inactivas

- Activas (`active: true`, status `reviewed`): **345**
- Inactivas (`active: false`, status `pending_review`): **2** — `DER105-P033` y `DER105-P087` (casos conocidos; se conservó su respuesta original en `answer.raw` sin normalizar y no se intentó resolverlas).

## Preguntas de ordenamiento

Tres preguntas se clasificaron como `ordering` y su secuencia correcta quedó normalizada en `answer.ordered_items`:

- `C10-P045` — Pasos del método científico (ordenar 1–4)
- `C10-P068` — Orden de la estrategia de búsqueda (ordenar 1–6)
- `C10-P134` — Orden del proceso de investigación (ordenar 1–5)

En las tres también se conserva la solución completa original en `answer.raw`.

## Preguntas con tipo `unknown`

- Ninguna.

## Respuestas que no pudieron normalizarse

- Las 2 pendientes de revisión (`DER105-P033`, `DER105-P087`): `option_ids` vacío por diseño, ya que la fuente no confirma la respuesta.
- Todo lo demás quedó normalizado: 307 single_choice y 1 true_false con su letra en `option_ids`; 4 multiple_choice con todas sus letras; 21 fill_blank con `accepted_text` (extraído de los marcadores `[...]` de la solución; cuando además existía alternativa con letra, se añadió también `option_ids`); 11 matching con `pairs` completos (las referencias numeradas "(1)…" se resolvieron con los enunciados del propio prompt); y 3 ordering con `ordered_items`.

## Errores o advertencias

- Advertencias del conversor: 0. Sin errores.
- Campo adicional `options_note` (documentado en el esquema): presente en 29 preguntas de tipo fill_blank/matching cuya sección "Alternativas" no usa letras (bancos de palabras, elementos a emparejar). Preserva ese texto literal sin inventar letras de opción.
- Fidelidad a la fuente: se conservaron tal cual las particularidades académicas de los bancos (p. ej., alternativas A y C idénticas en DER102-P018, erratas citadas de los originales). No se alteró contenido académico para pasar validaciones.

## Resultado de las validaciones

Ejecución de `python scripts/validate_questions.py`: **RESULTADO: OK — todas las validaciones pasaron** (0 errores; 0 avisos).

Comprobaciones realizadas: total exacto de 347; conteos por asignatura; identificadores únicos y con formato válido; numeración consecutiva por asignatura (P001…PNNN sin saltos); campos obligatorios no vacíos; tipos, dificultades y estados dentro de los valores permitidos; `active=false` exactamente en las 2 pendientes conocidas; opciones sin letras duplicadas y con texto; `option_ids` presentes entre las opciones; single/true_false revisadas con exactamente 1 letra y multiple_choice con 2+; consistencia total entre `questions.json` y los 6 archivos por asignatura (incluido el campo `total`); codificación UTF-8 estricta de todos los JSON; ausencia de registros duplicados.

Determinismo verificado: dos ejecuciones consecutivas del conversor producen archivos byte a byte idénticos (mismo hash MD5).

## Comandos para reejecutar

Desde la raíz del proyecto (`…\Educativo\simulador`):

```
python scripts/convert_banks.py
python scripts/validate_questions.py
```

El conversor sobrescribe íntegramente las salidas en `datos/`, por lo que puede ejecutarse cuantas veces se desee sin duplicar preguntas.
