# SIGEB — Diseño del proyecto integrador

**Curso:** Reutilización de Software, Ingeniería Informática.  
**Proyecto Experimental de Aula:** SIGEB es el proyecto integrador del curso de Reutilización de Software (Ingeniería Informática). Es una aplicación de consola en Python 3 que simula una biblioteca: catálogo de libros, usuarios y préstamos. Los datos viven solo en memoria, no hay dependencias externas obligatorias y no hay persistencia entre ejecuciones.

## Principios de diseño

- Aplicación CLI en Python 3 con datos en memoria. Sin dependencias externas obligatorias.
- Se enseña cada patrón con: problema inicial → UML → implementación guiada → refactorización → prueba → justificación.
- Se implementan **seis patrones** en el proyecto: Factory Method, Builder, Adapter, Facade, Observer y Strategy.
- Los otros patrones del programa se estudian en ejercicios breves o laboratorios independientes.
- No implementar un patrón si no existe un requisito que lo justifique.

## Alcance y requisitos funcionales

| ID | Funcionalidad | Etapa |
|---|---|---|
| RF-01 | Registrar libro (ISBN único, título, autor, categoría) | 1 |
| RF-02 | Listar libros | 1 |
| RF-03 | Buscar libro por ISBN, título o autor | 1 |
| RF-04 | Consultar disponibilidad | 1 |
| RF-05 | Agregar ejemplares de título existente | 1 |
| RF-06 | Registrar usuario (ID, nombre, tipo, activo) | 1 |
| RF-07 | Listar usuarios | 1 |
| RF-08 | Consultar historial de préstamos | 1 |
| RF-09 | Prestar ejemplar | 1 |
| RF-10 | Validar usuario, cupo y disponibilidad | 1/7 |
| RF-11 | Establecer fecha de inicio y límite | 1/7 |
| RF-12 | Devolver préstamo | 1 |
| RF-13 | Actualizar disponibilidad al prestar/devolver | 1 |
| RF-14 | Consultar préstamos activos, devueltos y vencidos | 1 |
| RF-15 | Crear notificaciones por canal | 2 |
| RF-16 | Integrar proveedor externo simulado | 3 |
| RF-17 | Avisar automáticamente de préstamo/devolución | 7 |
| RF-18 | Generar reportes configurables | 2 |
| RF-19 | Política por tipo de usuario | 7 |
| RF-20 | Extender políticas sin alterar el servicio central | 7 |

## Reglas de negocio

- RN-01: ISBN único identifica un título. Cada título posee `ejemplares_totales` y `ejemplares_disponibles`.
- RN-02: Cada préstamo retira una unidad de ejemplares disponibles.
- RN-03: No se presta si los ejemplares disponibles son cero.
- RN-04: Solo usuarios registrados y activos pueden prestar.
- RN-05: Préstamos con ID único, fecha de inicio y fecha límite.
- RN-06: No se permite devolver dos veces el mismo préstamo.
- RN-07: Al devolver se restituye una unidad disponible.
- RN-08: Vencido = activo y hoy > fecha límite.
- RN-09: Antes de Strategy, plazo uniforme de siete días; después: estudiantes 7 días y máximo 3, docentes 15 días y máximo 5, administrativos 10 días y máximo 3.
- RN-10: Sin multas, reservas, autenticación ni persistencia entre ejecuciones en el alcance básico.
- RN-11: La fecha límite se calcula a partir de `hoy` recibido por el método; no se usa reloj global en las pruebas.
- RN-12: Las validaciones preceden a la mutación del inventario. El guardado del préstamo y descuento de disponibilidad deben considerarse una operación indivisible desde la lógica de aplicación; en memoria se ejecuta en una secuencia controlada, revertida ante error de almacenamiento simulado.
- RN-13: El envío externo de una notificación no revierte una operación de préstamo ya confirmada; registrar fallos de envío sin ocultar el resultado de la operación principal.

## Arquitectura

**Presentación:** `MenuConsola` transforma entradas en llamadas y muestra respuestas. No decide reglas de préstamo.

**Aplicación:** `ServicioCatalogo`, `ServicioUsuarios`, `ServicioPrestamos` orquestan operaciones; `BibliotecaFacade` simplifica el uso público de operaciones compuestas (semana 4).

**Dominio:** `Libro`, `Usuario`, `Prestamo`, reglas y políticas (Strategy en semana 7).

**Infraestructura:** repositorios en memoria y proveedor simulado de SMS. Las dependencias hacia repositorios se pueden convertir a protocolos al introducir la refactorización.

**Notificaciones:** Factory Method crea objetos del canal seleccionado; Adapter traduce la interfaz `enviar(mensaje)` a la API diferente del proveedor SMS; Observer suscribe una clase que transforma eventos de dominio en notificaciones. Estas responsabilidades permanecen separadas.

**Reportes:** Builder compone un reporte opcionalmente con encabezado, resumen, detalle y pie.

## Contratos básicos

- `Libro(isbn, titulo, autor, categoria, ejemplares_totales, ejemplares_disponibles)`.
- `Usuario(id_usuario, nombre, tipo, activo)`.
- `Prestamo(id_prestamo, isbn_libro, id_usuario, fecha_inicio, fecha_limite, fecha_devolucion=None)`.
- `ServicioPrestamos.prestar(isbn: str, id_usuario: str, hoy: date) -> Prestamo`.
- `ServicioPrestamos.devolver(id_prestamo: str, hoy: date) -> Prestamo`.
- `PoliticaPrestamo.dias_permitidos() -> int` y `maximo_activos() -> int`.
- `CentroEventos.publicar(evento)` y `Observador.actualizar(evento)`.
- `Notificacion.enviar(mensaje: str)`.
- `ConstructorReporte.con_titulo(...).con_resumen(...).con_detalle(...).construir()`.

## Organización propuesta

```text
sigeb/
├── README.md
├── main.py
├── sigeb/
│   ├── __init__.py
│   ├── presentacion/
│   │   ├── __init__.py
│   │   └── menu.py
│   ├── dominio/
│   │   ├── __init__.py
│   │   ├── libro.py
│   │   ├── usuario.py
│   │   ├── prestamo.py
│   │   ├── errores.py
│   │   └── politicas.py                 # Semana 7
│   ├── aplicacion/
│   │   ├── __init__.py
│   │   ├── catalogo.py
│   │   ├── usuarios.py
│   │   ├── prestamos.py
│   │   └── fachada_biblioteca.py       # Semana 4
│   ├── infraestructura/
│   │   ├── __init__.py
│   │   ├── repositorio_libros.py
│   │   ├── repositorio_usuarios.py
│   │   ├── repositorio_prestamos.py
│   │   └── proveedor_sms_simulado.py   # Semana 3
│   ├── notificaciones/
│   │   ├── __init__.py
│   │   ├── fabrica.py                   # Semana 2: Factory Method
│   │   ├── canales.py
│   │   ├── adaptador_sms.py             # Semana 3: Adapter
│   │   └── eventos.py                  # Semana 7: Observer
│   └── reportes/
│       ├── __init__.py
│       ├── reporte.py
│       └── constructor_reporte.py      # Semana 2: Builder
├── pruebas/
│   ├── test_catalogo.py
│   ├── test_prestamos.py
│   ├── test_notificaciones.py
│   ├── test_reportes.py
│   └── test_politicas.py
├── diagramas/
│   ├── 01_modelo_inicial.puml
│   ├── 02_arquitectura_objetivo.puml
│   └── 03_prestamo_secuencia.puml
└── laboratorios/
    ├── creacionales_complementarios/
    ├── estructurales_complementarios/
    └── comportamiento_complementarios/
```

**Nota:** el árbol describe la estructura final; al iniciar el curso solo existen los módulos de la versión inicial. Los demás se incorporan cuando se estudia cada patrón.

## Evolución (en lo posible despúes de la explicación del patrón)

| Semana | Temas oficiales | Teoría / práctica | Cambio en proyecto | Laboratorio independiente | Entregable |
|---|---|---|---|---|---|
| 1 | 1 y 2 | 75 / 45 min | Entidades, servicios, CLI, pruebas iniciales; plazo fijo | Nivelación POO, catálogo GoF | V1 + UML inicial |
| 2 | 3 y 4 | 60 / 60 min | Factory Method para canales; Builder para reportes | Abstract Factory, Singleton; comparación Factory Method/Abstract Factory, Builder/Abstract Factory | V2 + test creacionales |
| 3 | 5 y 6 | 60 / 60 min | Adapter para proveedor SMS simulado | Bridge, Composite, Decorator | V3 + prueba adaptador |
| 4 | 7 | 45 / 75 min | Facade para flujo de préstamos | Proxy | V4 + diagrama actualizado |
| 5 | 8 | 60 / 60 min | Consolidar casos de uso y pruebas | Chain of Responsibility y Command | Laboratorio A |
| 6 | 9 | 60 / 60 min | Corrección/refactorización de pruebas | Interpreter e Iterator | Laboratorio B |
| 7 | 10 y 11 | 75 / 45 min | Observer para eventos y Strategy para políticas; explicación de MVC y frameworks (no exigir web) | Discusión comparativa MVC y frameworks | V5 final + explicación técnica |
| 8 | 12 | 120 / 0 min | No se modifica el proyecto | Clase independiente J2EE (terminología contemporánea: Jakarta EE) | Actividad de comprensión |
| 9 | Repaso y exámenes | Sin clase | Sin cambios | Sin clase | Según cronograma oficial |

## Pruebas de aceptación prioritarias

1. Registrar un libro y dos ejemplares permite consultar un único ISBN con `ejemplares_totales=2`.
2. Prestar con cero disponibilidad devuelve error y no modifica los repositorios.
3. Prestar un ejemplar descuenta una unidad y crea préstamo con límite correcto.
4. Una segunda devolución del mismo préstamo falla sin incrementar inventario.
5. Un usuario inactivo no puede tomar prestado.
6. Un préstamo activo con fecha límite anterior a hoy se identifica como vencido.
7. El Factory Method devuelve el canal pedido, sin condicionales de tipo repartidos entre consumidores.
8. El Adapter convierte un `enviar(mensaje)` en llamada válida a la API simulada del proveedor.
9. Facade permite registrar un préstamo sin que el menú conozca los repositorios.
10. Observer notifica a suscriptores por eventos; una suscripción ausente no recibe avisos.
11. Strategy asigna 7/15/10 días según tipo de usuario y aplica cupos 3/5/3.
12. Builder genera reportes con secciones opcionales sin necesitar todos los argumentos en el constructor.

## Archivos PlantUML

- `01_modelo_inicial.puml`: clases y dependencias antes de introducir patrones GoF.
- `02_arquitectura_objetivo.puml`: clases, patrones y sus colaboraciones tras la evolución del proyecto.
- `03_prestamo_secuencia.puml`: flujo de préstamo y publicación de evento.

Para generar una imagen con PlantUML instalado: `plantuml -tpng diagramas/*.puml`.


