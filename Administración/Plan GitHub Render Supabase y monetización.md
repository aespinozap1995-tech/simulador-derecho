# Plan de GitHub, Render, Supabase y monetización

## Decisiones recomendadas

- Mantener el repositorio de GitHub **privado** mientras contenga bancos de preguntas, claves correctas o material académico.
- Convertir el prototipo actual en una aplicación de producción con **Next.js y TypeScript**.
- Confirmar el servicio exacto de **PocketBase/PocketHost ya pagado** y aprovecharlo en la arquitectura sin duplicar funciones con Supabase.
- Mantener **GitHub y Supabase en sus planes gratuitos** durante la validación inicial.
- Conservar Render como alternativa de despliegue hasta comprobar qué incluye el servicio ya pagado.
- Usar **Supabase Auth y Postgres** para usuarios, intentos y vigencia premium.
- No enviar nunca al navegador la respuesta correcta junto con la pregunta. La calificación debe hacerse en el servidor.
- Lanzar primero el pago como activación de **30 días**, no como acceso vitalicio por USD 1.
- Empezar únicamente con **transferencia bancaria y aprobación manual**; incorporar una pasarela solo cuando el volumen lo justifique.

## Infraestructura ya disponible

- GitHub: plan gratuito.
- Supabase: plan gratuito.
- PocketBase/PocketHost: servicio pagado, pendiente de confirmar proveedor, plan, URL y prestaciones incluidas.
- No se asignará todavía a PocketBase la autenticación o la base de datos: primero se comprobará si es alojamiento, servicio administrado o una instalación propia. Mantener dos fuentes de usuarios o intentos sería innecesario y aumentaría los errores.

## Planes de acceso

| Función | Visitante sin cuenta | Registrado gratuito | Premium |
|---|---:|---:|---:|
| Realizar simulacros | Sí | Sí | Sí |
| Ver resultado al terminar | Temporal | Sí | Sí |
| Historial guardado | No | Últimos 3 intentos | Historial ampliado |
| Retroalimentación | No | Sí | Sí, ampliada |
| Navegación, temporizador, tema y tamaño de letra | Sí | Sí | Sí |
| Cantidad de preguntas | Básica | Básica | Todas las opciones |
| Reintentar preguntas falladas | No | No | Sí |
| Estadísticas por asignatura y tema | No | Básicas | Detalladas |
| Simulacros enfocados en debilidades | No | No | Sí |
| Nuevas preguntas de compendios | Muestra limitada | Selección | Acceso completo |

La accesibilidad, el temporizador y la navegación no deben convertirse en beneficios de pago. Premium debe aportar práctica y análisis adicionales, no empeorar deliberadamente el examen básico.

## Reglas por nivel

### Visitante

- El intento vive únicamente en memoria o en la sesión del navegador.
- Al cerrar o recargar, el resultado no se conserva.
- Solo recibe puntaje, porcentaje y número de aciertos al finalizar.
- No recibe respuesta correcta ni explicación.
- Aplicar un límite razonable de intentos por dispositivo o dirección IP para evitar abuso.

### Registrado gratuito

- Registro con correo verificado y contraseña mediante Supabase Auth.
- Puede consultar sus tres resultados más recientes.
- Al guardar el cuarto resultado, se elimina el más antiguo.
- Recibe retroalimentación sencilla después de responder si activó esa opción.
- El historial conserva solo el resumen del intento, no necesariamente todas las respuestas individuales.

### Premium

- Vigencia recomendada inicial: 30 días desde la activación.
- Más tamaños de simulacro y uso razonablemente ilimitado.
- Historial ampliado, evolución por asignatura y detección de temas débiles.
- Modo «practicar mis errores» y simulacros dirigidos.
- Acceso completo a los futuros bancos generados desde compendios revisados.
- La vigencia se controla en el servidor; nunca mediante una variable manipulable en el navegador.

## Arquitectura

```text
Navegador
   │
   ▼
Next.js en Render
   ├── entrega preguntas sin clave correcta
   ├── califica respuestas en el servidor
   ├── comprueba el nivel de acceso
   └── administra solicitudes de activación por transferencia
             │
             ▼
Supabase
   ├── Auth: cuentas y sesiones
   ├── Postgres: preguntas, intentos y accesos
   └── RLS: cada usuario ve solamente sus datos
```

El archivo actual `questions.json` puede continuar como fuente de importación, pero no debe publicarse dentro de los archivos estáticos si contiene las claves correctas.

Esta arquitectura es provisional hasta identificar el producto de PocketBase ya contratado. Si ese servicio aloja la aplicación, puede sustituir a Render; si ofrece base de datos y autenticación, se elegirá entre PocketBase y Supabase en lugar de mantener ambos para la misma función.

## Modelo de datos mínimo

### `profiles`

- `id`: coincide con el usuario de Supabase Auth.
- `display_name`.
- `created_at`.
- No usar campos editables por el usuario para decidir si es premium.

### `subjects`

- `id`, `slug`, `name`, `active`.

### `questions`

- Enunciado, tipo, alternativas, solución, explicación, asignatura, origen y estado.
- Las columnas con soluciones no se exponen mediante consultas públicas.

### `attempts`

- Usuario, asignatura, cantidad de preguntas, aciertos, porcentaje, duración, nivel al momento del intento y fecha.
- Para visitantes no se crea ningún registro.

### `attempt_answers`

- Se incorpora cuando se implemente «practicar mis errores» y análisis premium.
- Debe tener una política de conservación definida para no guardar datos innecesarios.

### `entitlements`

- Usuario, plan, estado, inicio, vencimiento y origen de activación.
- Es la fuente de verdad para autorizar Premium.

### `payments`

- Método, banco de destino, referencia de transferencia, usuario, monto, moneda, estado, revisor y fechas.
- No almacenar números de tarjeta ni información financiera sensible.
- La referencia de transferencia debe ser única para impedir que un mismo pago active dos veces el acceso.

## Seguridad obligatoria

- Activar Row Level Security en todas las tablas expuestas por Supabase.
- Cada usuario solo puede leer sus propios intentos, perfil y acceso.
- Las preguntas se solicitan a una ruta de servidor que elimina solución y explicación antes de responder.
- La entrega de retroalimentación y la calificación comprueban la sesión y el nivel de acceso en el servidor.
- La clave `service_role` de Supabase solo existe en Render y jamás lleva el prefijo `NEXT_PUBLIC_`.
- Proteger los endpoints de examen y autenticación con límites de solicitudes.
- Toda aprobación o rechazo debe quedar registrado con administrador, fecha y observación.
- Añadir política de privacidad, términos de uso, política de reembolsos y aviso de que el simulador es una herramienta de estudio.

## GitHub

### Preparación

1. Inicializar el repositorio privado y revisar el `.gitignore`.
2. Excluir `.env*`, archivos temporales, resultados de extracción y material que no deba distribuirse.
3. Confirmar si los PDF y compendios pueden almacenarse legalmente; por defecto, mantenerlos fuera del repositorio.
4. Conservar migraciones SQL, código, pruebas y documentación dentro del repositorio.
5. Usar `main` para producción y ramas breves para cada cambio.

### Integración continua

En cada cambio se debe ejecutar:

- validación del banco de preguntas;
- pruebas unitarias de calificación y niveles de acceso;
- comprobación de tipos;
- compilación de producción;
- análisis para impedir que secretos se incluyan en el repositorio.

El servicio de despliegue elegido desplegará únicamente una versión que haya superado estas comprobaciones.

## Supabase

1. Crear proyectos separados para pruebas y producción cuando empiece el cobro.
2. Configurar autenticación por correo y contraseña con verificación de correo.
3. Conectar un SMTP propio antes del lanzamiento; el servicio de correo predeterminado es solo para pruebas y tiene límites muy bajos.
4. Crear el esquema mediante migraciones versionadas.
5. Crear y probar las políticas RLS con usuario anónimo, gratuito, premium y administrador.
6. Importar las 345 preguntas activas; mantener `DER105-P033` y `DER105-P087` inactivas hasta resolverlas.
7. Crear una función transaccional que guarde el intento gratuito y conserve solamente los tres últimos.
8. Preparar copias de seguridad y un procedimiento de restauración antes de aceptar pagos.

## Render

1. Conectar el servicio web al repositorio privado de GitHub.
2. Configurar variables de entorno de Supabase y pagos desde el panel de Render.
3. Añadir una ruta `/api/health` y registros sin datos personales ni respuestas de examen.
4. Activar despliegues automáticos desde `main` después de las pruebas.
5. Utilizar el nivel gratuito durante las pruebas de hoy y la beta cerrada.
6. Pasar a una instancia pagada antes de vender el servicio: el nivel gratuito puede suspenderse tras inactividad y tardar en reactivarse.
7. Configurar dominio propio, HTTPS, alertas y comprobación posterior al despliegue.

Esta sección se mantiene como alternativa. Antes de contratar Render se verificará si el servicio de PocketBase/PocketHost ya pagado puede alojar de forma fiable la aplicación.

## Pagos

### Primera fase: transferencia y aprobación manual

- Precio inicial recomendado: USD 1 por 30 días de Premium.
- La persona debe crear primero su cuenta para obtener un identificador de pedido.
- Mostrar las instrucciones de transferencia y pedir que el identificador conste en el concepto cuando el banco lo permita.
- El usuario registra la referencia, fecha, monto y banco de origen. El comprobante será opcional si la verificación se realiza directamente en la cuenta bancaria.
- La solicitud queda en estado `pending`; nunca activa Premium automáticamente.
- El administrador compara la solicitud con los movimientos bancarios y la aprueba o rechaza.
- Al aprobar, el sistema activa 30 días y registra quién tomó la decisión.
- Una referencia de transferencia ya utilizada no puede asociarse a otra activación.
- Si un usuario renueva antes de vencer, los 30 días se suman al vencimiento vigente.

Este proceso evita comisiones de pasarela y permite validar la demanda. También exige conciliar pagos con disciplina y limitar el acceso administrativo.

### Segunda fase: agilizar la conciliación

- Añadir filtros de solicitudes pendientes, búsqueda por referencia y registro de observaciones.
- Permitir aprobación y rechazo desde un panel administrativo protegido.
- Enviar confirmación por correo después de la aprobación.
- Exportar un reporte de activaciones para la conciliación contable.

### Tercera fase: pasarela opcional

- Evaluar PayPhone u otra alternativa solamente cuando las aprobaciones manuales consuman demasiado tiempo.
- Validar cualquier confirmación de pago en el servidor.
- Mantener idempotencia para que una notificación repetida no duplique la vigencia.

## Economía inicial

Con transferencia directa no existe una comisión de pasarela por cada venta, salvo los cargos que pueda aplicar el banco. Si la meta es **100 clientes premium activos**:

- Ingreso bruto: USD 100 por período.
- Ingreso recibido: aproximadamente USD 100 antes de cargos bancarios e impuestos.
- De allí todavía se descuentan el servicio ya pagado, dominio, correo transaccional y cualquier ampliación futura de infraestructura.

No conviene vender acceso vitalicio por USD 1. Un período de 30 días o un paquete de USD 3 por 90 días mantiene el precio accesible y permite sostener el contenido y la infraestructura.

## Fases de ejecución

### Fase 1 — Cerrar el prototipo

- Realizar las pruebas visuales y funcionales actuales.
- Registrar los ajustes sin ampliar todavía el banco mediante compendios.
- Congelar una versión de referencia de la interfaz.

### Fase 2 — Base de producción

- Crear el repositorio privado.
- Migrar o consolidar la aplicación en Next.js con TypeScript.
- Separar interfaz, rutas de servidor y banco de respuestas.
- Añadir pruebas y validación continua.

### Fase 3 — Supabase

- Implementar esquema, migraciones, Auth y RLS.
- Importar el banco validado.
- Implementar visitantes, usuarios gratuitos y conservación de tres intentos.

### Fase 4 — Premium y pagos

- Crear `entitlements`, solicitudes de transferencia, panel de aprobación y vencimiento.
- Habilitar instrucciones de transferencia y activación manual auditada.
- Añadir beneficios premium empezando por historial y práctica de errores.

### Fase 5 — Render y beta

- Desplegar una instancia de pruebas.
- Probar con 10 a 20 personas.
- Corregir errores, medir finalización y observar solicitudes de soporte.
- Pasar a instancia de producción pagada y abrir gradualmente a 50 y luego 100 clientes.

### Fase 6 — Ampliación académica

- Después de estabilizar el sistema, procesar los compendios.
- Generar preguntas nuevas identificando siempre origen y estado de revisión.
- Publicarlas únicamente después de una revisión académica.

## Pruebas de aceptación antes de cobrar

- Un visitante no deja historial ni obtiene retroalimentación.
- Un usuario gratuito nunca puede consultar intentos ajenos y conserva exactamente tres resultados.
- Un premium activo recibe sus beneficios y los pierde correctamente al vencer.
- Cambiar datos en el navegador no concede Premium.
- Ninguna respuesta correcta aparece en el código descargado ni en la respuesta inicial de la API.
- El temporizador, navegación, ordenamiento, asociación y selección funcionan en escritorio y móvil.
- Una referencia de transferencia repetida no produce activaciones duplicadas.
- La aplicación se recupera de una recarga, caída de red o despliegue sin corromper intentos.

## Métricas para decidir los siguientes beneficios

- Porcentaje de visitantes que crea una cuenta.
- Porcentaje de registrados que compra Premium.
- Simulacros iniciados y terminados.
- Retención a 7 y 30 días.
- Asignaturas más utilizadas.
- Uso de retroalimentación y «practicar mis errores».
- Solicitudes de soporte por cada 100 usuarios.

## Fuentes operativas

- [Planes y límites de Supabase](https://supabase.com/pricing)
- [Autenticación con contraseña en Supabase](https://supabase.com/docs/guides/auth/passwords)
- [Row Level Security en Supabase](https://supabase.com/docs/guides/database/postgres/row-level-security)
- [Servicios gratuitos de Render](https://render.com/docs/free)
- [Despliegues en Render](https://render.com/docs/deploys)
- [Facturación de GitHub Actions](https://docs.github.com/en/billing/concepts/product-billing/github-actions)
- [Costos de PayPhone, para una evaluación futura](https://help.payphone.app/hc/es/articles/31532700571931--Cu%C3%A1nto-cuesta-Payphone)
