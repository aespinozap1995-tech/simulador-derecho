# Reporte de conversión — Bancos Markdown → JSON

**Conversión inicial:** 14 de julio de 2026
**Última actualización:** 23 de julio de 2026

## Fuentes convertidas

Cada asignatura se construye a partir de bancos independientes:

1. `banco_preguntas.md`: preguntas recuperadas de los simuladores del aula virtual.
2. `preguntas_compendios.md`: primera tanda generada desde los compendios de clase.
3. Para DER101, `preguntas_examenes_anteriores.md`: preguntas reconstruidas desde
   temas atribuidos a exámenes anteriores y verificadas contra el compendio.

La procedencia se conserva en JSON mediante:

- `original_simulator`: pregunta proveniente del aula virtual.
- `generated_from_compendium`: pregunta formulada a partir de los compendios.

## Inventario resultante

- **900 preguntas registradas**.
- **898 preguntas activas**.
- **2 preguntas inactivas:** `DER105-P033` y `DER105-P087`.
- **347 preguntas del banco original**.
- **553 preguntas generadas y verificadas desde compendios**.

| Asignatura | Total | Activas | Generadas desde compendios |
|---|---:|---:|---:|
| DER101 — Introducción al Derecho | 160 | 160 | 131 |
| DER102 — Lógica y Dialéctica Jurídica | 105 | 105 | 85 |
| DER104 — Teoría General del Estado y Sociología Jurídica | 125 | 125 | 95 |
| DER105 — Expresión Oral y Redacción Jurídica | 142 | 140 | 47 |
| DER106 — Historia y Filosofía del Derecho | 153 | 153 | 120 |
| C10 — Investigación | 215 | 215 | 75 |
| **Total** | **900** | **898** | **553** |

## Distribución por tipo

| Tipo | Cantidad |
|---|---:|
| `single_choice` | 698 |
| `multiple_choice` | 50 |
| `ordering` | 46 |
| `matching` | 84 |
| `fill_blank` | 21 |
| `true_false` | 1 |

## Controles aplicados a las preguntas generadas

- Identificadores únicos y consecutivos por asignatura.
- Fuente Markdown y apartado identificables.
- Opciones, parejas y elementos de ordenamiento sin duplicados internos.
- Respuestas normalizadas para todos los tipos.
- Explicación, clave para recordar y confusión común obligatorias.
- Descarte de bibliografías, material administrativo, preguntas de comprensión, referencias a imágenes no reproducidas y bloques repetidos.
- Comparación textual contra las preguntas originales: no se encontraron coincidencias cercanas por encima del umbral de revisión.
- Mezcla de `introduccion_al_derecho_texto_completo.md` controlada: únicamente las páginas 1–504 se usan como apoyo para DER101.
- Para la tanda de exámenes anteriores de DER101 se revisaron además los apartados
  específicos sobre fuentes del Derecho, ley, costumbre, jurisprudencia, doctrina,
  jerarquía normativa y fines del Derecho. Los errores de OCR fueron descartados y las
  alternativas se reconstruyeron desde el contenido académico.

## Resultado técnico

La ejecución de `scripts/validate_questions.py` finalizó con **0 errores y 0 advertencias**.

El conversor genera:

- `datos/questions.json`;
- `datos/subjects/DER101.json`;
- `datos/subjects/DER102.json`;
- `datos/subjects/DER104.json`;
- `datos/subjects/DER105.json`;
- `datos/subjects/DER106.json`;
- `datos/subjects/C10.json`.

## Reejecución

Desde la raíz del proyecto:

```powershell
python scripts/generate_compendium_questions.py
python scripts/generate_der101_exam_reconstructions.py
python scripts/convert_banks.py
python scripts/validate_questions.py
node scripts/build_standalone.mjs
```

Los procesos son deterministas y sobrescriben sus salidas completas, por lo que pueden ejecutarse nuevamente sin duplicar preguntas.
