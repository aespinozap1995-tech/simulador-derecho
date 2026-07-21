# Reporte de conversión — Bancos Markdown → JSON

**Conversión inicial:** 14 de julio de 2026
**Última actualización:** 20 de julio de 2026

## Fuentes convertidas

Cada asignatura se construye a partir de dos bancos independientes:

1. `banco_preguntas.md`: preguntas recuperadas de los simuladores del aula virtual.
2. `preguntas_compendios.md`: primera tanda generada desde los compendios de clase.

La procedencia se conserva en JSON mediante:

- `original_simulator`: pregunta proveniente del aula virtual.
- `generated_from_compendium`: pregunta formulada a partir de los compendios.

## Inventario resultante

- **865 preguntas registradas**.
- **863 preguntas activas**.
- **2 preguntas inactivas:** `DER105-P033` y `DER105-P087`.
- **347 preguntas del banco original**.
- **518 preguntas generadas desde compendios**.

| Asignatura | Total | Activas | Generadas desde compendios |
|---|---:|---:|---:|
| DER101 — Introducción al Derecho | 125 | 125 | 96 |
| DER102 — Lógica y Dialéctica Jurídica | 105 | 105 | 85 |
| DER104 — Teoría General del Estado y Sociología Jurídica | 125 | 125 | 95 |
| DER105 — Expresión Oral y Redacción Jurídica | 142 | 140 | 47 |
| DER106 — Historia y Filosofía del Derecho | 153 | 153 | 120 |
| C10 — Investigación | 215 | 215 | 75 |
| **Total** | **865** | **863** | **518** |

## Distribución por tipo

| Tipo | Cantidad |
|---|---:|
| `single_choice` | 674 |
| `multiple_choice` | 47 |
| `ordering` | 44 |
| `matching` | 78 |
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
python scripts/convert_banks.py
python scripts/validate_questions.py
node scripts/build_standalone.mjs
```

Los procesos son deterministas y sobrescriben sus salidas completas, por lo que pueden ejecutarse nuevamente sin duplicar preguntas.
