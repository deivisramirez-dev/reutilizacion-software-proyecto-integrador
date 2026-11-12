# Etapa 3 — Adapter del proveedor SMS

Registro de SIGEB antes de integrar el proveedor externo simulado, y de cómo quedó implementado el Adapter.

Observer, Facade y Strategy no se ejecutaron en esta etapa y no están en el código. El `RESUMEN.md` asigna la etapa 3 al RF-16: integrar un proveedor externo simulado. El patrón de esa integración es el Adapter. Facade está previsto para la semana 4. Observer y Strategy están previstos para la semana 7. Describirlos como si ya se hubieran aplicado no correspondería al proyecto.

## Estado del proyecto antes de la etapa 3

El corte es el de responsabilidades, no un commit distinto. La etapa 2 y la etapa 3 se escribieron en la misma intervención, encima del commit `24d1473`. Antes de la traducción al proveedor, el sistema ya tenía el núcleo de la versión 1 y los dos patrones de la etapa 2.

### Lo que ya estaba

- Catálogo, usuarios y préstamos en memoria, con las reglas de la versión 1 y el plazo fijo de siete días.
- Menú de las opciones 1 a 11, más la pausa hasta pulsar Enter.
- Factory Method en `sigeb/notificaciones/fabrica.py`, con `FabricaConsola`, `FabricaCorreo` y `FabricaSMS`.
- Productos `NotificacionConsola` y `NotificacionCorreo`, y el contrato `Notificacion.enviar(mensaje)`.
- `ServicioNotificaciones.enviar`, que pide `crear()` y `enviar()` sin inspeccionar la clase concreta.
- Builder en `ConstructorReporte`, producto `Reporte` y `ServicioReportes`.
- Opciones de menú **12. Enviar notificación** y **13. Generar reporte**.
- Pruebas de aceptación 1 a 7 y 12.

### Lo que la etapa 3 tenía que resolver

El canal SMS no puede llamar al proveedor con `enviar(mensaje)`. El diseño exige un proveedor simulado cuya API sea distinta, y un Adapter que traduzca el contrato de SIGEB a esa API. Esa traducción no debe mezclarse con la fábrica ni con el servicio de préstamos.

Tampoco debía aparecer todavía:

- `BibliotecaFacade` ni `aplicacion/fachada_biblioteca.py`
- `CentroEventos`, `Observador` ni `notificaciones/eventos.py`
- `PoliticaPrestamo` ni `dominio/politicas.py`
- Aviso automático al prestar o devolver (RF-17)
- Plazos 7/15/10 ni cupos 3/5/3 (RF-19 y RF-20)

`MenuConsola` seguía recibiendo `ServicioCatalogo`, `ServicioUsuarios` y `ServicioPrestamos` por separado. El menú ya conocía esos servicios. Ocultarlos detrás de una fachada es trabajo de la semana 4, no de esta etapa.

## Cómo se implementó el Adapter

El Adapter implementa el contrato que SIGEB ya usa y esconde la API del proveedor.

### El proveedor simulado

`sigeb/infraestructura/proveedor_sms_simulado.py` representa la API externa. No tiene un método `enviar(mensaje)`.

Su operación es:

```text
despachar(numero_destino, cuerpo) -> referencia
```

Cada envío aceptado se guarda en `enviados` como un diccionario con `numero_destino`, `cuerpo` y `referencia` (`SMS-0001`, `SMS-0002`, …). Si falta el destino o el cuerpo, lanza `ErrorProveedorSMS`, una excepción del proveedor y no de `ErrorDominio`.

No hay red, número real ni servicio de telecomunicaciones. La lista `enviados` es la evidencia de que la llamada ocurrió.

### La traducción

`sigeb/notificaciones/adaptador_sms.py` define `AdaptadorSMS`, que hereda de `Notificacion`.

- Guarda el proveedor y normaliza el número: admite un `+` inicial, quita espacios y exige al menos siete dígitos.
- `enviar(mensaje)` valida el texto y llama a `proveedor.despachar(self._destino, mensaje)`.
- Si el proveedor lanza `ErrorProveedorSMS`, el Adapter la convierte en `ErrorNotificacion`. El menú ya captura `ErrorDominio`, así que muestra el fallo sin conocer `despachar`.

Quien posee una `Notificacion` sigue escribiendo `enviar(mensaje)`. Solo el Adapter conoce `despachar`, el número y la referencia.

### Relación con Factory Method

`FabricaSMS.crear()` devuelve un `AdaptadorSMS`. La fábrica elige la clase. El Adapter hace la traducción. `ServicioNotificaciones` no llama a `despachar` ni captura `ErrorProveedorSMS`.

Esa separación es la que pide el diseño: Factory Method crea el canal, el Adapter traduce la API, y más adelante el Observer reaccionará a eventos. Cada responsabilidad queda en su módulo.

### Regla RN-13

Un fallo de envío no deshace un préstamo ya confirmado. El envío no está dentro de `ServicioPrestamos.prestar`: la opción 12 es independiente de la opción 9. La prueba `test_fallo_de_sms_no_revierte_un_prestamo_confirmado` presta un ejemplar, fuerza un proveedor que lanza `ErrorProveedorSMS("sin señal")` y comprueba tres cosas: se lanza `ErrorNotificacion`, los ejemplares disponibles no cambian y el préstamo sigue sin fecha de devolución.

## Beneficios obtenidos con el Adapter

- SIGEB habla con el proveedor sin adoptar su firma. El contrato interno sigue siendo `enviar(mensaje)`. Cambiar `despachar` por otro nombre o por otros parámetros obliga a tocar el Adapter, no el menú ni `ServicioNotificaciones`.
- `ErrorProveedorSMS` no se filtra a la presentación. El Adapter lo traduce a `ErrorNotificacion`, que el menú ya sabe mostrar.
- El proveedor se puede sustituir en las pruebas por un objeto con `despachar`. La prueba de fallo no necesita un teléfono ni una red.
- La aceptación 8 fija la traducción: `enviar("Préstamo registrado")` sobre el destino `3001112233` deja en el proveedor un envío con ese número, ese cuerpo y la referencia `SMS-0001`.
- El préstamo confirmado permanece aunque el SMS falle. La operación principal y el aviso externo no comparten una misma transacción.

## Observer, Facade y Strategy

Estos tres patrones se pidieron como contenido de este registro. No fueron ejecutados. No hay clases, menú, pruebas ni beneficios obtenidos que documentar como trabajo hecho. Lo que sigue es el lugar que el diseño les reserva, para no confundirlos con el Adapter.

### Facade

Previsto en la semana 4, en `sigeb/aplicacion/fachada_biblioteca.py`.

Hoy el menú construye un préstamo llamando a `ServicioPrestamos` y, para un reporte, a `ServicioReportes`, que a su vez conoce catálogo, usuarios y préstamos. La fachada debería ofrecer una puerta única para las operaciones compuestas, de modo que el menú no conozca los repositorios ni coordine los servicios. La aceptación 9 todavía no tiene prueba: «Facade permite prestar sin que el menú conozca los repositorios».

Como no está implementada, el menú sigue dependiendo de los servicios concretos y no hay un beneficio realizado de simplificación.

### Observer

Previsto en la semana 7, en `sigeb/notificaciones/eventos.py`.

El contrato previsto es `CentroEventos.publicar(evento)` y `Observador.actualizar(evento)`. Al prestar o devolver, el dominio publicaría un evento y solo los observadores suscritos lo recibirían (RF-17). Quien no está suscrito no recibe el aviso. La aceptación 10 no está escrita como prueba del proyecto.

Hoy el aviso solo sale si la persona usa la opción 12 y escribe el mensaje. Prestar y devolver no publican nada. No hay suscriptores que contar ni un beneficio realizado de desacoplar el aviso del servicio de préstamos.

### Strategy

Previsto en la semana 7, en `sigeb/dominio/politicas.py`.

El contrato previsto es `PoliticaPrestamo.dias_permitidos()` y `maximo_activos()`. Estudiante: 7 días y 3 préstamos. Docente: 15 días y 5. Administrativo: 10 días y 3. El servicio central de préstamos no debería modificarse para agregar otra política (RF-19 y RF-20).

Hoy `PLAZO_DIAS = 7` sigue fijo en `ServicioPrestamos` para todos los tipos. No se consulta el cupo. La aceptación 11 no está cubierta. No hay un beneficio realizado de intercambiar la política sin tocar el servicio.

## Qué sí cubre la etapa 3 en las pruebas

`pruebas/test_notificaciones.py` incluye:

- Aceptación 8: `AdaptadorSMS.enviar` produce la llamada `despachar` esperada en `ProveedorSMSSimulado`.
- El fallo del proveedor se convierte en `ErrorNotificacion` y no altera un préstamo ya guardado ni el inventario.

Las aceptaciones 9, 10 y 11, que corresponderían a Facade, Observer y Strategy, siguen sin implementarse.
