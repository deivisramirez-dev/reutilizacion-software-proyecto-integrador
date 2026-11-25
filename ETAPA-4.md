# Etapa 4 — Facade

Registro de SIGEB antes de unificar el subsistema detrás de una sola puerta, y de cómo quedó implementado el patrón Facade.

## Estado del proyecto antes de la etapa 4

La versión publicada en `68b9c68` ya cubría las etapas 1 a 3.

### Lo que ya funcionaba

- Catálogo, usuarios y préstamos en memoria, con plazo fijo de 7 días y las reglas RN-01 a RN-13 que aplican sin Observer ni Strategy.
- Factory Method para los canales `consola`, `correo` y `sms`.
- Builder para reportes con título, resumen, detalle y pie opcionales.
- Adapter: `enviar(mensaje)` se traduce a `despachar(numero, cuerpo)` del proveedor simulado. Un fallo de SMS no deshace un préstamo confirmado.
- Menú de las opciones 1 a 13, con pausa hasta pulsar Enter.
- Pruebas de aceptación 1 a 8 y 12.

### Cómo estaba armado el menú

`MenuConsola` recibía cinco colaboradores:

- `ServicioCatalogo`
- `ServicioUsuarios`
- `ServicioPrestamos`
- `ServicioNotificaciones`
- `ServicioReportes`

`main.py` creaba los repositorios, construía esos servicios y se los pasaba al menú uno por uno. El menú no importaba los repositorios, pero sí conocía cada servicio y decidía a cuál llamar en cada opción. Para prestar usaba `ServicioPrestamos` directamente. Para un reporte, `ServicioReportes`, que a su vez conoce catálogo, usuarios y préstamos.

Esa superficie obliga a la presentación a saber cómo está partido el subsistema. Agregar un paso al préstamo, o cambiar qué servicio lo ejecuta, obliga a tocar el menú.

### Lo que esta etapa no cambia

Siguen fuera Observer, Strategy, el aviso automático al prestar o devolver, y los plazos y cupos por tipo de usuario. El plazo continúa en `PLAZO_DIAS = 7`. Los datos siguen solo en memoria.

## Cómo se implementó Facade

El patrón introduce `BibliotecaFacade` como única puerta pública del subsistema. El menú deja de nombrar los servicios.

### La fachada

`sigeb/aplicacion/fachada_biblioteca.py` recibe los cinco servicios y delega. No valida inventario, no calcula fechas y no elige el canal de notificación. Esas reglas permanecen donde ya estaban.

| Método de la fachada | Servicio que lo resuelve |
|---|---|
| `registrar_libro`, `listar_libros`, `buscar_libro`, `consultar_disponibilidad`, `agregar_ejemplares` | `ServicioCatalogo` |
| `registrar_usuario`, `listar_usuarios` | `ServicioUsuarios` |
| `historial`, `prestar`, `devolver`, `consultar_prestamos` | `ServicioPrestamos` |
| `enviar_notificacion` | `ServicioNotificaciones` |
| `generar_reporte` | `ServicioReportes` |

También expone `tipos_usuario` y `canales`, para que el menú arme los textos de ayuda sin importar `usuario.py` ni el paquete de notificaciones.

`prestar(isbn, id_usuario, hoy)` y `devolver(id_prestamo, hoy)` conservan las firmas del diseño. La fachada las reenvía a `ServicioPrestamos`.

### El menú

`MenuConsola` ahora se construye con un solo argumento de dominio de aplicación: `BibliotecaFacade`. Cada opción llama a un método de esa fachada. La opción 9 queda así:

```text
prestamo = self._biblioteca.prestar(isbn, id_usuario, hoy)
```

El módulo `sigeb/presentacion/menu.py` no importa `infraestructura`, ni ningún repositorio, ni `ServicioCatalogo`, `ServicioUsuarios`, `ServicioPrestamos`, `ServicioNotificaciones` o `ServicioReportes`. Sigue conociendo `Libro`, `Usuario` y `Prestamo` solo para mostrar sus datos, y `ErrorDominio` para imprimir el fallo.

### El punto de entrada

`main.py` sigue siendo quien crea los repositorios y los servicios. Después los envuelve en `BibliotecaFacade` y entrega solo esa fachada a `MenuConsola`. Los repositorios no salen de `main`.

### Diagrama

`diagramas/04_fachada.puml` muestra la colaboración: el menú apunta únicamente a `BibliotecaFacade`, y la fachada apunta a los cinco servicios. Los repositorios quedan detrás de catálogo, usuarios y préstamos. `diagramas/01_modelo_inicial.puml` no se modifica: sigue siendo el modelo de la semana 1, anterior a los patrones.

La versión del paquete pasa de `"3"` a `"4"`.

## Beneficios obtenidos

- El menú registra un préstamo sin conocer los repositorios ni el servicio que descuenta el ejemplar. La aceptación 9 lo fija: la fuente del menú no menciona repositorios ni `ServicioPrestamos`, y la opción 9 deja un préstamo con límite de siete días y descuenta una unidad.
- La presentación depende de una sola clase. Cambiar la coordinación interna del préstamo, del reporte o de la notificación no obliga a cambiar la firma de `MenuConsola`.
- Los servicios no se funden. Catálogo, usuarios, préstamos, notificaciones y reportes conservan sus reglas. La fachada solo ofrece una interfaz más simple.
- Factory Method, Builder y Adapter siguen en sus módulos. La fachada llama a `enviar_notificacion` y a `generar_reporte`; no crea canales ni arma secciones.

## Prueba de esta etapa

`pruebas/test_fachada.py` cubre la aceptación 9:

- Lee el código de `menu.py` y comprueba que no aparecen repositorios, infraestructura ni los servicios de catálogo y de préstamos.
- Arma la fachada en la prueba, como hace `main.py`, registra un libro y un usuario, y ejecuta el menú solo con la opción 9.
- El ejemplar disponible pasa de 1 a 0 y el préstamo queda con inicio el 18 de noviembre de 2026 y límite el 25 de noviembre de 2026.

Las aceptaciones 1 a 8 y la 12 siguen pasando. Observer y Strategy quedan para la semana 7.
