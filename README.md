# Simulador de examen final — Carrera de Derecho

Proyecto académico y aplicación beta de un simulador de exámenes para seis asignaturas de la carrera de Derecho.

La aplicación desplegable se encuentra en `prototipo/`. Consulta su README para ejecutar y desplegar el simulador.

## Versión individual sin instalación

El archivo `simulador-examen-final.html` contiene la interfaz y el banco de preguntas completo. Puede copiarse a otra computadora y abrirse con doble clic, sin servidor ni conexión a internet.

Para reconstruirlo después de actualizar el banco:

```bash
node scripts/build_standalone.mjs
```

## Render

- Root Directory: `prototipo`
- Build Command: `npm ci && npm run build`
- Start Command: `npm start`
- Node: `22.13.0` o posterior

Los PDF y las fuentes originales se mantienen fuera del repositorio.
