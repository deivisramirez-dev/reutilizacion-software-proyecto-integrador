# Etapa 2 — Factory Method y Builder

Registro de SIGEB antes de incorporar las notificaciones por canal y los reportes configurables, y de cómo quedaron implementados Factory Method y Builder.

Las etapas 2 y 3 se escribieron en la misma intervención, sobre el commit `24d1473` de `main`. No existe un commit intermedio que contenga solo la etapa 2. El corte que sigue es el de responsabilidades definido en `RESUMEN.md`: la etapa 2 cubre RF-15 y RF-18; la etapa 3 cubre RF-16.

## Estado del proyecto antes de la etapa 2

SIGEB era la versión 1 del proyecto integrador: una biblioteca en consola, en Python 3, sin dependencias externas y sin ningún patrón GoF.

### Qué hacía el programa

El menú ofrecía las operaciones del núcleo:

1. Registrar libro
2. Listar libros
3. Buscar libro
4. Consultar disponibilidad
5. Agregar ejemplares
6. Registrar usuario
7. Listar usuarios
8. Historial de préstamos
9. Prestar ejemplar
10. Devolver préstamo
11. Consultar préstamos
0. Salir

Había un ajuste local, todavía no publicado, para que el resultado de cada opción permaneciera en pantalla hasta pulsar Enter. El menú de Cursor es bajo y, sin esa pausa, el listado quedaba fuera de la vista.

### Capas y piezas existentes

| Capa | Piezas |
|---|---|
| Presentación | `MenuConsola` |
| Aplicación | `ServicioCatalogo`, `ServicioUsuarios`, `ServicioPrestamos` |
| Dominio | `Libro`, `Usuario`, `Prestamo` y la jerarquía `ErrorDominio` |
| Infraestructura | `RepositorioLibros`, `RepositorioUsuarios`, `RepositorioPrestamos` |

`main.py` creaba los tres repositorios en memoria y los entregaba a los servicios. El menú no decidía reglas de préstamo: traducía la entrada y mostraba la respuesta.

### Reglas ya vigentes

- El ISBN identifica un título. Registrar con N ejemplares deja `ejemplares_totales` y `ejemplares_disponibles` en N.
- Agregar ejemplares suma la misma cantidad a totales y a disponibles.
- La búsqueda usa ISBN exacto. Título y autor coinciden por fragmento, sin distinguir mayúsculas.
- El historial es por usuario.
- El identificador del préstamo lo genera el repositorio: `P-0001`, `P-0002`, y así sucesivamente.
- El plazo es fijo: `PLAZO_DIAS = 7` para estudiante, docente y administrativo. No hay cupo por tipo.
- La fecha límite se calcula con el `hoy` que recibe el servicio. Las pruebas no usan el reloj del sistema.
- Prestar valida libro, usuario activo y disponibilidad antes de mutar. Guarda el préstamo y después descuenta. Si el descuento falla, elimina el préstamo.
- Una segunda devolución falla antes de tocar el inventario.
- Vencido significa sin devolver y con fecha límite anterior a hoy. Las consultas `activo`, `vencido` y `devuelto` no se solapan.
- No hay multas, reservas, autenticación ni persistencia. Al salir, los diccionarios desaparecen.

### Pruebas y diagrama

Pasaban las aceptaciones 1 a 6: un ISBN con dos ejemplares, préstamo sin disponibilidad, descuento y límite de siete días, segunda devolución, usuario inactivo y préstamo vencido.

El único diagrama era `diagramas/01_modelo_inicial.puml`, el modelo previo a los patrones.

### Lo que todavía no existía

No había paquete `notificaciones` ni `reportes`. No había fábrica, canal, reporte ni constructor. El menú no podía enviar un aviso ni generar un documento con secciones opcionales. Un canal nuevo habría exigido condicionales repartidos entre el menú y los servicios. Un reporte con encabezado, resumen, detalle y pie opcionales habría exigido un constructor con todas las combinaciones de argumentos, o una cadena de `if` que armara el texto a mano.

## Problema que resuelve cada patrón

**Factory Method (RF-15).** SIGEB debe crear una notificación del canal pedido: consola, correo o SMS. Quien envía el mensaje solo necesita `enviar(mensaje)`. No debe conocer `NotificacionConsola`, `NotificacionCorreo` ni la clase del SMS, ni ramificar con `isinstance`.

**Builder (RF-18).** Un reporte puede llevar título, resumen, detalle y pie, en cualquier subconjunto. El cliente no debe pasar `None` por las secciones que no quiere, ni existir una clase distinta por cada combinación.

## Cómo se implementó Factory Method

El patrón separa el contrato del canal, las fábricas que deciden la clase concreta y el servicio que solo pide `crear()` y `enviar()`.

### Contrato y productos

`sigeb/notificaciones/canales.py` define la interfaz y dos productos que SIGEB conoce de forma directa:

- `Notificacion.enviar(mensaje)` es el contrato fijado en el diseño.
- `NotificacionConsola` escribe el mensaje en una salida inyectada (`print` en la aplicación, una lista en las pruebas).
- `NotificacionCorreo` valida que el destinatario contenga `@` y guarda la pareja `(destinatario, mensaje)` en un buzón en memoria. No abre una conexión SMTP.

El mensaje vacío se rechaza con `DatosInvalidos` antes de entregarlo.

### Fábricas

`sigeb/notificaciones/fabrica.py` define el creador abstracto y un creador por canal. El método de fábrica es `crear() -> Notificacion`.

| Fábrica | Producto que devuelve `crear()` |
|---|---|
| `FabricaConsola` | `NotificacionConsola` |
| `FabricaCorreo` | `NotificacionCorreo` |
| `FabricaSMS` | `AdaptadorSMS` |

`FabricaSMS` aparece aquí porque el canal SMS también se obtiene por el método de fábrica. La traducción a la API del proveedor no vive en la fábrica: vive en el Adapter, y corresponde a la etapa 3. La fábrica solo decide qué objeto construir.

`fabrica_para(canal, ...)` es el único lugar que asocia el nombre escrito por el usuario (`consola`, `correo`, `sms`) con una fábrica. `nombre_canal` normaliza el texto y rechaza cualquier otro valor. Los canales válidos están en la tupla `CANALES`.

### Consumidor

`ServicioNotificaciones.enviar(canal, mensaje, destino)` hace siempre lo mismo:

1. Rechaza el mensaje vacío.
2. Normaliza el nombre del canal.
3. Pide la fábrica a `fabrica_para`.
4. Ejecuta `fabrica.crear().enviar(mensaje)`.
5. Devuelve el nombre del canal, sin inspeccionar la clase del objeto creado.

No hay `isinstance` ni una rama por cada clase concreta dentro de `enviar`. La prueba `consumir(fabrica, mensaje)` de `pruebas/test_notificaciones.py` es ese consumidor reducido: sirve igual para los tres canales y comprueba el efecto distinto de cada producto (texto en la salida, pareja en el buzón, llamada registrada en el proveedor).

### Uso desde el menú

La opción **12. Enviar notificación** pregunta el canal, el destino y el mensaje. Si el canal es consola, el destino se deja vacío. El menú no instancia `NotificacionConsola` ni `NotificacionCorreo`. Llama a `ServicioNotificaciones.enviar` y muestra `Notificación enviada por {canal}`.

`main.py` construye un solo `ServicioNotificaciones` con un `ProveedorSMSSimulado` y lo entrega al menú junto con el resto de servicios.

## Cómo se implementó Builder

El patrón separa el armado paso a paso del reporte ya cerrado.

### Producto

`sigeb/reportes/reporte.py` define `Reporte` con cuatro secciones, todas opcionales: `titulo`, `resumen`, `detalle` y `pie`. La que no se pidió queda en `None`. `detalle` es una tupla de líneas.

`texto()` concatena solo los bloques presentes. Si no hay resumen, el texto no contiene el encabezado `Resumen`. Lo mismo ocurre con `Detalle` y `Pie`. Un reporte vacío, construido sin llamar a ningún `con_*`, produce la cadena vacía.

### Constructor

`sigeb/reportes/constructor_reporte.py` define `ConstructorReporte`. El `__init__` no recibe las secciones. Cada una se agrega con un método que devuelve `self`, de modo que se pueden encadenar:

```text
ConstructorReporte().con_titulo(...).con_resumen(...).con_detalle(...).con_pie(...).construir()
```

El contrato del diseño exige `con_titulo`, `con_resumen`, `con_detalle` y `construir`. `con_pie` completa la sección de pie descrita en la arquitectura. Omitir cualquiera de esos métodos es válido: `construir()` copia al `Reporte` solo lo que se haya fijado.

Cada texto se valida: no se acepta una sección en blanco. `con_detalle` exige una lista con al menos una línea. Llamar dos veces al mismo `con_*` sustituye el valor anterior.

### Servicio que usa el Builder

`ServicioReportes.generar(titulo, incluir_resumen, incluir_detalle, incluir_pie, hoy)` crea un `ConstructorReporte`, siempre añade el título y solo entonces encadena las secciones cuyas marcas vienen en `True`.

- El resumen cuenta libros, usuarios, préstamos activos y préstamos vencidos en la fecha `hoy`.
- El detalle lista cada libro (ISBN, título, autor, categoría y disponibles/totales) y cada usuario (id, nombre, tipo y estado). Si no hay registros, la única línea es `Sin libros ni usuarios registrados.`
- El pie escribe `Generado el {fecha}. SIGEB.`

La categoría del libro, que en la versión 1 se guardaba sin usarse, aparece en el detalle.

### Uso desde el menú

La opción **13. Generar reporte** pide el título y tres respuestas `s/n`: resumen, detalle y pie. La respuesta vacía vale como sí. El menú imprime `reporte.texto()` y espera Enter antes de redibujar las opciones.

## Beneficios obtenidos

### Factory Method

- Un canal nuevo se agrega con una clase de notificación y una fábrica. `ServicioNotificaciones.enviar` y la opción 12 no cambian su forma de entrega: siguen en `crear()` y `enviar()`.
- La elección de la clase concreta quedó concentrada en `fabrica_para`. No se repartieron condicionales de tipo entre el menú, el préstamo y las pruebas.
- Consola, correo y SMS comparten el contrato `enviar(mensaje)`. Las pruebas pueden usar el mismo consumidor y distinguir los canales por el efecto, no por el nombre de la clase en cada llamada.
- El buzón de correo y la salida de consola se inyectan. Las pruebas no envían correo real ni dependen de lo que se vea en la terminal.

### Builder

- No hace falta un constructor con título, resumen, detalle y pie obligatorios, ni una sobrecarga por cada subconjunto. El reporte de solo título se arma con `con_titulo` y `construir`.
- Las secciones ausentes no aparecen como huecos ni como el texto `None`. `texto()` omite el bloque y su encabezado.
- `ServicioReportes` decide el contenido de negocio (conteos, líneas del catálogo, fecha). `ConstructorReporte` solo sabe componer secciones. Cambiar el texto del resumen no obliga a cambiar la forma de construir el reporte.
- La prueba de aceptación 12 fija el comportamiento: un `ConstructorReporte()` vacío es válido, un reporte de solo título no contiene `Resumen`, `Detalle` ni `Pie`, y la cadena completa conserva las cuatro secciones.

## Pruebas que cubren esta etapa

En `pruebas/test_notificaciones.py`:

- Aceptación 7: cada fábrica devuelve el tipo pedido y el mismo `consumir` produce el efecto de consola, correo y SMS.

En `pruebas/test_reportes.py`:

- Aceptación 12: secciones opcionales, reporte vacío y reporte completo.
- El servicio genera un reporte de catálogo con detalle y sin resumen ni pie, e incluye la línea del libro registrado.

Las aceptaciones 1 a 6 siguen pasando. El plazo fijo de siete días, los repositorios en memoria y la ausencia de Facade, Observer y Strategy no se modificaron en esta etapa.
