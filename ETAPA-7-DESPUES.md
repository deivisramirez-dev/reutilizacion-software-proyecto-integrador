# Etapa 7 — Estado posterior

SIGEB después de incorporar Observer y Strategy. La versión del paquete pasa a `"5"`. Las quince pruebas pasan, incluidas las aceptaciones 10 y 11. Factory Method, Builder, Adapter y Facade siguen como estaban.

El estado anterior a este cambio está en `ETAPA-7-ANTES.md`.

## Strategy

El plazo y el cupo ya no están escritos dentro de `ServicioPrestamos`. Los resuelve `PoliticaPrestamo`, en `sigeb/dominio/politicas.py`.

| Política | Días | Préstamos activos |
|---|---|---|
| `PoliticaEstudiante` | 7 | 3 |
| `PoliticaDocente` | 15 | 5 |
| `PoliticaAdministrativo` | 10 | 3 |

El contrato es `dias_permitidos()` y `maximo_activos()`. `politica_para(tipo)` devuelve la política del usuario. `prestar` solo llama a esos dos métodos: no pregunta si el usuario es estudiante, docente o administrativo.

El cupo cuenta los préstamos sin devolver, vencidos incluidos. Si el usuario ya llegó al máximo, se lanza `CupoAgotado` antes de guardar el préstamo y sin descontar ejemplares.

Una política nueva es una clase más y una entrada en el mapa `_POLITICAS`. El cuerpo de `prestar` no se reescribe (RF-20).

En el menú, un docente que presta el 25 de noviembre de 2026 recibe límite el 10 de diciembre de 2026, quince días después.

## Observer

`sigeb/notificaciones/eventos.py` define `Evento`, `Observador`, `CentroEventos` y `ObservadorNotificacion`.

`CentroEventos.publicar(evento)` llama a `actualizar(evento)` solo en los observadores suscritos con `suscribir`. Quien no fue suscrito no recibe el aviso.

`ServicioPrestamos` publica después de que la operación ya quedó confirmada:

- `prestamo`, al guardar el préstamo y descontar el ejemplar.
- `devolucion`, al marcar la devolución y reponer el ejemplar.

Si el descuento o la reposición fallan, no hay evento. Una segunda devolución falla antes de publicar.

`ObservadorNotificacion` convierte el evento en una notificación: llama al `enviar(mensaje)` que recibió al construirse. Si ese envío lanza `ErrorDominio`, guarda el texto en `fallos` y no lo propaga. El préstamo ya confirmado permanece (RN-13).

`main.py` suscribe un `ObservadorNotificacion` al canal consola. Por eso, al prestar, la pantalla muestra primero el aviso automático y después la línea del préstamo. La opción 12 sigue existiendo para un envío manual por consola, correo o SMS. Factory Method crea el canal y el Adapter traduce el SMS; el Observer no hace ninguna de esas dos cosas.

`ServicioPrestamos` puede recibir el `CentroEventos`. Si no se le pasa, usa uno vacío: las pruebas antiguas no avisan a nadie y no cambian de resultado. El estudiante de esas pruebas sigue teniendo siete días de plazo.

## Diagramas

- `diagramas/02_arquitectura_objetivo.puml` reúne los seis patrones y sus colaboraciones.
- `diagramas/03_prestamo_secuencia.puml` recorre el préstamo: menú, fachada, política, repositorio, descuento, publicación y observador.

`diagramas/01_modelo_inicial.puml` y `diagramas/04_fachada.puml` no se reescribieron.

## Pruebas nuevas

`pruebas/test_politicas.py` comprueba los tres pares 7/3, 15/5 y 10/3, y que un préstamo por encima del cupo no modifica el inventario.

`pruebas/test_eventos.py` comprueba que el suscriptor recibe `prestamo` y `devolucion`, que el observador no suscrito sigue con la lista vacía, y que un envío fallido no devuelve el ejemplar ni borra el préstamo.

## Qué queda fuera

Siguen fuera del alcance las multas, las reservas, la autenticación y la persistencia. Los laboratorios de Chain of Responsibility, Command, Interpreter e Iterator no entran en SIGEB: el diseño los deja como ejercicios independientes.
