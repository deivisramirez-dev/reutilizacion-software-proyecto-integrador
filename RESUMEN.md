# Resumen del proyecto SIGEB

El repositorio todavía no tiene código: solo existe el documento de diseño `README.md`  sin historial de Git ni módulos. El proyecto está definido por completo en ese diseño y aún no se ha empezado a implementar.

## Qué es

**SIGEB** es el proyecto integrador del curso de Reutilización de Software (Ingeniería Informática). Es una aplicación de consola en Python 3 que simula una biblioteca: catálogo de libros, usuarios y préstamos. Los datos viven solo en memoria, no hay dependencias externas obligatorias y no hay persistencia entre ejecuciones.



La idea pedagógica es enseñar cada patrón con este ciclo: problema inicial, UML, implementación guiada, refactorización, prueba y justificación. Solo se implementa un patrón si un requisito lo justifica.

## Estado actual

| Qué hay | Qué falta |
|---|---|
| Diseño, requisitos, reglas, arquitectura, contratos, plan de 7 semanas y criterios de aceptación | Código, pruebas, diagramas PlantUML y repositorio Git |

La estructura final prevista (aún no creada) separa presentación, dominio, aplicación, infraestructura, notificaciones y reportes:

```text
sigeb/
├── main.py
├── sigeb/
│   ├── presentacion/menu.py
│   ├── dominio/          libro, usuario, prestamo, errores, politicas
│   ├── aplicacion/       catalogo, usuarios, prestamos, fachada
│   ├── infraestructura/  repositorios en memoria, proveedor SMS
│   ├── notificaciones/   fabrica, canales, adaptador SMS, eventos
│   └── reportes/         reporte, constructor
├── pruebas/
├── diagramas/            3 archivos PlantUML
└── laboratorios/         creacionales, estructurales, comportamiento
```

Al inicio del curso solo deben existir los módulos de la versión inicial. El resto se agrega cuando se estudia cada patrón.

## Dominio y reglas

Tres entidades:

- **Libro:** ISBN único, título, autor, categoría, ejemplares totales y disponibles.
- **Usuario:** id, nombre, tipo (`estudiante`, `docente`, `administrativo`) y si está activo.
- **Préstamo:** id, ISBN, usuario, fecha de inicio, fecha límite y fecha de devolución opcional.

Fuera de alcance: multas, reservas, autenticación y persistencia (RN-10).

Las reglas que más condicionan el diseño:

- Un préstamo descuenta un ejemplar; con cero disponibles no se presta y no se muta nada (RN-02, RN-03).
- Solo usuarios registrados y activos pueden prestar (RN-04).
- No se puede devolver dos veces el mismo préstamo; al devolver se restituye un ejemplar (RN-06, RN-07).
- Vencido significa activo y que hoy es posterior a la fecha límite (RN-08).
- La fecha límite se calcula a partir del `hoy` que recibe el método. Las pruebas no usan el reloj del sistema (RN-11).
- Las validaciones ocurren antes de mutar el inventario. Guardar el préstamo y descontar disponibilidad es una operación indivisible; si falla un almacenamiento simulado, se revierte (RN-12).
- Si falla el envío de una notificación, el préstamo ya confirmado no se revierte: se registra el fallo y se conserva el resultado de la operación principal (RN-13).

Política de plazos (RN-09):

| Momento | Plazo | Cupo |
|---|---|---|
| Antes de Strategy (semanas 1–6) | 7 días para todos | Sin cupo por tipo |
| Estudiante | 7 días | máximo 3 activos |
| Docente | 15 días | máximo 5 activos |
| Administrativo | 10 días | máximo 3 activos |

## Requisitos funcionales

Veinte requisitos, agrupados por etapa:

- **Etapa 1 (núcleo):** registrar y listar libros, buscar por ISBN, título o autor, consultar disponibilidad, agregar ejemplares, registrar y listar usuarios, historial, prestar, devolver, actualizar disponibilidad y consultar préstamos activos, devueltos y vencidos (RF-01 a RF-14).
- **Etapa 2:** notificaciones por canal y reportes configurables (RF-15, RF-18).
- **Etapa 3:** proveedor externo simulado de SMS (RF-16).
- **Etapa 7:** aviso automático al prestar o devolver, política por tipo de usuario y extensión de políticas sin tocar el servicio central (RF-17, RF-19, RF-20). RF-10 y RF-11 se refinan en la semana 7 (cupo y fecha límite según política).

## Arquitectura

Cuatro capas, con responsabilidades explícitas:

1. **Presentación.** `MenuConsola` traduce entradas y muestra respuestas. No decide reglas de préstamo.
2. **Aplicación.** `ServicioCatalogo`, `ServicioUsuarios` y `ServicioPrestamos` orquestan. Desde la semana 4, `BibliotecaFacade` es la única puerta pública de las operaciones compuestas.
3. **Dominio.** Entidades, errores y, en la semana 7, políticas (`PoliticaPrestamo`: `dias_permitidos()` y `maximo_activos()`).
4. **Infraestructura.** Repositorios en memoria y proveedor SMS simulado. Más adelante las dependencias hacia repositorios pueden convertirse en protocolos.

Contratos que el diseño ya fija y que conviene respetar al implementar:

- `ServicioPrestamos.prestar(isbn, id_usuario, hoy) -> Prestamo`
- `ServicioPrestamos.devolver(id_prestamo, hoy) -> Prestamo`
- `CentroEventos.publicar(evento)` y `Observador.actualizar(evento)`
- `Notificacion.enviar(mensaje)`
- `ConstructorReporte.con_titulo(...).con_resumen(...).con_detalle(...).construir()`

## Los seis patrones del proyecto

| Patrón | Semana | Dónde vive | Problema que resuelve |
|---|---|---|---|
| Factory Method | 2 | `notificaciones/fabrica.py` | Crear el canal pedido (consola, correo, SMS) sin condicionales de tipo en los consumidores |
| Builder | 2 | `reportes/constructor_reporte.py` | Armar reportes con encabezado, resumen, detalle y pie opcionales |
| Adapter | 3 | `notificaciones/adaptador_sms.py` | Traducir `enviar(mensaje)` a la API distinta del proveedor SMS simulado |
| Facade | 4 | `aplicacion/fachada_biblioteca.py` | El menú registra un préstamo sin conocer repositorios ni servicios internos |
| Observer | 7 | `notificaciones/eventos.py` | Avisar a suscriptores al prestar o devolver; quien no está suscrito no recibe nada |
| Strategy | 7 | `dominio/politicas.py` | Plazo y cupo según tipo de usuario, sin modificar el servicio central |

Factory Method, Adapter y Observer se mantienen separados: uno crea el canal, otro traduce la API externa y el tercero reacciona a eventos de dominio.

Los demás patrones del temario no entran al sistema. Se cubren en laboratorios independientes: Abstract Factory, Singleton, Bridge, Composite, Decorator, Proxy, Chain of Responsibility, Command, Interpreter e Iterator. También entran MVC, frameworks y J2EE como temas de comprensión, sin exigir una aplicación web.

## Plan de versiones

| Semana | Versión | Qué se entrega |
|---|---|---|
| 1 | V1 | Entidades, servicios, CLI, pruebas, plazo fijo de 7 días, UML inicial |
| 2 | V2 | Factory Method y Builder, más pruebas creacionales |
| 3 | V3 | Adapter del SMS y su prueba |
| 4 | V4 | Facade y diagrama actualizado |
| 5 | — | Consolidar casos de uso y pruebas (laboratorio A: Chain of Responsibility y Command) |
| 6 | — | Corregir y refactorizar pruebas (laboratorio B: Interpreter e Iterator) |
| 7 | V5 | Observer, Strategy, explicación de MVC y frameworks |

Tres diagramas PlantUML previstos y aún no creados: modelo inicial, arquitectura objetivo y secuencia del préstamo (incluyendo la publicación del evento).

## Criterios de aceptación

Doce pruebas prioritarias, alineadas con las reglas:

1. Registrar un libro con dos ejemplares deja un solo ISBN y `ejemplares_totales = 2`.
2. Prestar con cero disponibles falla y no toca los repositorios.
3. Prestar descuenta una unidad y crea el préstamo con el límite correcto.
4. Una segunda devolución falla y no incrementa el inventario.
5. Un usuario inactivo no puede prestar.
6. Un préstamo activo con fecha límite anterior a hoy se marca vencido.
7. Factory Method devuelve el canal pedido.
8. Adapter convierte `enviar(mensaje)` en una llamada válida al proveedor simulado.
9. Facade permite prestar sin que el menú conozca los repositorios.
10. Observer avisa solo a los suscriptores.
11. Strategy asigna 7/15/10 días y cupos 3/5/3.
12. Builder arma reportes con secciones opcionales.

## Observaciones sobre el diseño

El diseño está cerrado en lo esencial: capas, contratos, reglas de invariantes y el momento en que entra cada patrón. Hay algunos puntos que conviene decidir antes de escribir la V1, porque el README no los fija:

- **Búsqueda (RF-03).** No dice si título y autor se comparan en forma exacta, parcial o sin distinguir mayúsculas.
- **Agregar ejemplares (RF-05).** No dice si suma a totales y disponibles a la vez, ni qué pasa si se pide agregar a un ISBN que no existe.
- **Historial (RF-08).** No aclara si es por usuario, por libro o global.
- **Errores.** Existe `dominio/errores.py` en el árbol, pero no hay un catálogo de excepciones ni de mensajes.
- **Identificadores.** ISBN y id de usuario los aporta quien registra. El id de préstamo no dice si lo genera el servicio o quien llama.
- **Categoría del libro.** Se guarda, pero ninguna regla ni reporte la usa.
- **Canales de notificación.** El Factory Method debe devolver “el canal pedido”, pero no se nombran los canales concretos (consola, correo y SMS son la lectura natural, no un contrato).
- **Eventos.** `publicar` y `actualizar` no definen los tipos de evento ni el contenido del mensaje.
- **Reporte.** El Builder tiene secciones, pero no el formato de salida ni qué datos incluye el resumen o el detalle.
- **Evaluación.** El propio documento advierte que la actividad de patrones de creación (2 de noviembre de 2026) y el laboratorio de comportamiento (30 de noviembre de 2026) dependen de enunciados oficiales que todavía no se asumen alineados con estas versiones.

La secuencia de construcción es coherente: primero el núcleo sin patrones (V1), luego creacionales, el adaptador, la fachada y, al final, Observer y Strategy, cuando ya existen eventos de préstamo y la política uniforme de siete días que esas dos piezas van a reemplazar.
