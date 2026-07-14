# Flujo de procesamiento de fuentes

## Principio

No se considerará completo un PDF únicamente porque permita extraer texto. Cada página también debe revisarse visualmente para detectar preguntas, alternativas, fórmulas o indicaciones que estén dentro de capturas e imágenes.

## Proceso por archivo

1. Conservar intacto el PDF o Markdown en `Material original`.
2. Extraer la capa de texto del PDF.
3. Renderizar todas las páginas como imágenes temporales.
4. Revisar visualmente las páginas y aplicar OCR al contenido gráfico que tenga texto.
5. Combinar el texto extraído con el texto recuperado de imágenes.
6. Identificar enunciado, alternativas, respuesta correcta y retroalimentación original.
7. Eliminar encabezados, menús y datos del aula virtual que no pertenezcan a la pregunta.
8. Detectar preguntas repetidas entre intentos sin eliminar variantes reales.
9. Verificar manualmente la respuesta correcta y registrar cualquier duda.
10. Convertir cada pregunta al formato normalizado del banco.

## Tratamiento de Markdown

Los archivos Markdown se leerán directamente, pero sus preguntas pasarán por la misma normalización, deduplicación y verificación académica que las extraídas de PDF.

## Formato de salida por pregunta

- Identificador único.
- Asignatura.
- Tema o unidad, cuando pueda determinarse.
- Enunciado.
- Alternativas.
- Respuesta correcta.
- Explicación sencilla para acierto y error.
- Consejo opcional.
- Fuente original.
- Estado de revisión.

## Control de calidad

- Mantener tildes, signos y terminología jurídica.
- No asumir que la alternativa resaltada por color fue extraída correctamente.
- Marcar como `pendiente de revisión` toda respuesta ambigua o sin evidencia suficiente.
- No inventar información que no aparezca en la fuente o en material académico verificable.
- Mantener los archivos temporales de renderizado fuera de la bóveda final.
