# Definición del producto

## Objetivo

Crear un simulador de exámenes por asignatura con temporizador, acceso mediante usuario y contraseña y retroalimentación sencilla.

## Funciones previstas

- Cronómetro ascendente para medir el tiempo empleado, sin límite ni finalización automática.
- Pausa, reanudación y persistencia local del intento para continuarlo posteriormente.
- Acciones independientes para guardar y salir, terminar con resultado o cerrar y descartar el intento.
- Consejos y retroalimentación inmediata activables o desactivables.
- Preguntas y alternativas en orden aleatorio.
- Registro de aciertos, errores, calificación y tiempo empleado.
- Gestión de usuarios y vigencia del acceso.
- Panel administrativo para preguntas, simulacros y resultados.
- Despliegue mediante GitHub y Render.

## Etapas del proyecto

### Etapa 1 — Banco inicial

- Recopilar y revisar las preguntas existentes en los simuladores del aula virtual.
- Utilizar este banco como base para desarrollar y probar el sistema.
- Banco consolidado: 900 preguntas, 898 activas, distribuidas entre seis asignaturas. Incluye 347 preguntas del banco original y 553 preguntas reconstruidas o generadas con respaldo en los compendios.

### Etapa 2 — Sistema funcional

- Convertir las preguntas a un formato estructurado para la aplicación.
- Crear un prototipo visual navegable antes de implementar toda la lógica.
- Validar en el prototipo la selección de asignatura, configuración del simulacro, temporizador, consejos, retroalimentación y pantalla de resultados.
- Ajustar el diseño a partir de la revisión del prototipo antes de conectarlo a la base de datos.
- Construir el simulador con temporizador, consejos configurables y retroalimentación inmediata.
- Incorporar resultados, usuarios, contraseñas y administración de accesos.
- Probar el sistema y desplegarlo mediante GitHub y Render.

### Etapa 3 — Ampliación mediante compendios

- Incorporar los compendios de clase después de completar y validar el sistema.
- Generar nuevas preguntas basadas en el contenido académico de los compendios.
- Mantener el estilo, estructura y dificultad observados en los simuladores originales.
- Someter las preguntas generadas a revisión académica antes de publicarlas.
- Evitar mezclar preguntas generadas con preguntas originales sin identificar su procedencia.

## Modelo inicial de acceso

- Visitante: intentos sin registro, resultado temporal, sin historial y sin retroalimentación.
- Registrado gratuito: retroalimentación y conservación de sus últimos tres resultados.
- Premium: historial ampliado, práctica dirigida y beneficios adicionales.
- Precio recomendado para validar el producto: USD 1 por 30 días, no acceso vitalicio.
- Pago inicial únicamente mediante transferencia bancaria y aprobación manual del administrador.
- Evaluar una pasarela y su automatización solamente cuando el volumen lo justifique.
- Detalle técnico y comercial: [[Plan GitHub Render Supabase y monetización]].
