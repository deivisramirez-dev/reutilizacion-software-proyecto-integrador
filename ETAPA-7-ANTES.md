# Etapa 7 — Estado previo

Fotografía de SIGEB el 25 de noviembre de 2026, antes de implementar Observer y Strategy. Esta etapa agrupa los dos patrones que el diseño deja para la semana 7: el aviso automático al prestar o devolver (RF-17) y la política por tipo de usuario (RF-19 y RF-20).

## Dónde está el código

La aplicación es de consola, en Python 3, sin dependencias externas. Los datos viven en memoria.

En GitHub, `main` está en el commit `68b9c68` (etapas 2 y 3). En el disco, sin confirmar, ya está la etapa 4:

- `sigeb/aplicacion/fachada_biblioteca.py`
- `sigeb/presentacion/menu.py` recibe solo `BibliotecaFacade`
- `main.py` arma los repositorios, los servicios y la fachada
- `pruebas/test_fachada.py`
- `diagramas/04_fachada.puml`
- `ETAPA-4.md`
- `__version__ = "4"`

También hay tres PDF locales (`README.pdf`, `RESUMEN.pdf`, `ETAPA-4.pdf`) que no forman parte del código.

Las doce pruebas actuales pasan: aceptaciones 1 a 9 y 12.

## Qué ya hace el programa

El menú ofrece las opciones 1 a 13. `MenuConsola` no importa repositorios ni servicios. Prestar es `biblioteca.prestar(isbn, id_usuario, hoy)`.

| Patrón | Módulo | Situación |
|---|---|---|
| Factory Method | `notificaciones/fabrica.py` | Canales `consola`, `correo` y `sms`. El envío es manual, opción 12. |
| Builder | `reportes/constructor_reporte.py` | Reporte con título, resumen, detalle y pie opcionales. Opción 13. |
| Adapter | `notificaciones/adaptador_sms.py` | `enviar(mensaje)` llama a `despachar(numero, cuerpo)`. |
| Facade | `aplicacion/fachada_biblioteca.py` | Única puerta del menú hacia el subsistema. |

El plazo está fijo en `ServicioPrestamos`:

```text
PLAZO_DIAS = 7
fecha_limite = hoy + 7 días
```

Ese valor vale para estudiante, docente y administrativo. No se cuenta cuántos préstamos activos tiene el usuario. Un usuario activo con ejemplares disponibles puede prestar sin tope.

`prestar` y `devolver` no publican eventos. No existen `CentroEventos`, `Observador` ni `PoliticaPrestamo`. No hay `notificaciones/eventos.py` ni `dominio/politicas.py`.

El aviso de un préstamo solo aparece si alguien usa la opción 12 y escribe el mensaje. Quien no hace esa operación no recibe nada, porque no hay suscriptores: no hay evento que suscribir.

## Reglas que siguen vigentes y que esta etapa debe respetar

- Validar antes de mutar el inventario. Guardar el préstamo y descontar es una sola operación: si el descuento falla, el préstamo se elimina.
- Una segunda devolución no incrementa el inventario.
- Vencido = sin devolver y hoy posterior a la fecha límite.
- La fecha `hoy` entra como argumento. Las pruebas no usan el reloj.
- Un fallo al enviar una notificación no deshace un préstamo ya confirmado (RN-13).
- Las aceptaciones 1 a 9 y 12 deben seguir pasando. El usuario de esas pruebas es estudiante, así que su plazo nuevo seguirá siendo 7 días.

## Lo que falta implementar

- Observer: al prestar y al devolver, publicar un evento. Solo los observadores suscritos lo reciben. Uno que no fue suscrito no se entera (aceptación 10).
- Strategy: `dias_permitidos()` y `maximo_activos()`. Estudiante 7 días y 3 activos, docente 15 y 5, administrativo 10 y 3 (aceptación 11). Una política nueva se agrega sin reescribir el cuerpo de `prestar`.
- Los diagramas que el diseño aún no tiene: arquitectura con los seis patrones y la secuencia del préstamo con la publicación del evento.
