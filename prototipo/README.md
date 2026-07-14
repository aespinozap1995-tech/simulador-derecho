# Simulador de examen final — Carrera de Derecho

Beta funcional de un simulador de exámenes para seis asignaturas de la carrera de Derecho.

## Funciones de la beta

- Selección de asignatura y cantidad de preguntas.
- Examen de una hora con navegación entre preguntas.
- Tema claro o crepuscular y tamaño de letra ajustable.
- Consejos y retroalimentación configurables.
- Preguntas de selección, asociación y ordenamiento.
- Resultado al terminar e historial local en el navegador.

Esta versión no usa cuentas ni una base de datos externa. El historial se almacena únicamente en el navegador del usuario.

## Desarrollo

```bash
npm ci
npm run dev
```

## Producción

```bash
npm ci
npm run build
npm start
```

## Despliegue en Render

- Build Command: `npm ci && npm run build`
- Start Command: `npm start`
- Node: `22.13.0` o posterior

La aplicación utiliza el servidor oficial de Next.js para asegurar compatibilidad con Render.

Como la aplicación vive dentro del proyecto académico, el campo Root Directory de Render debe ser `prototipo`.

## Estado de seguridad

Esta versión es una beta de prueba. El banco de preguntas se descarga en el navegador. Antes de incorporar usuarios, pagos o venta de accesos, la calificación y las respuestas correctas deberán trasladarse a un servicio de servidor.
