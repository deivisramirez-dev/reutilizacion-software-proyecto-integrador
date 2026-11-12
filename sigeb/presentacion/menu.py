"""Menú de consola. Traduce entradas en llamadas y muestra respuestas."""

import sys
from collections.abc import Callable
from datetime import date

from sigeb.aplicacion.catalogo import ServicioCatalogo
from sigeb.aplicacion.notificaciones import ServicioNotificaciones
from sigeb.aplicacion.prestamos import ServicioPrestamos
from sigeb.aplicacion.reportes import ServicioReportes
from sigeb.aplicacion.usuarios import ServicioUsuarios
from sigeb.dominio.errores import DatosInvalidos, ErrorDominio
from sigeb.dominio.libro import Libro
from sigeb.dominio.prestamo import Prestamo
from sigeb.dominio.usuario import TIPOS_USUARIO, Usuario


class MenuConsola:
    def __init__(
        self,
        catalogo: ServicioCatalogo,
        usuarios: ServicioUsuarios,
        prestamos: ServicioPrestamos,
        notificaciones: ServicioNotificaciones,
        reportes: ServicioReportes,
        entrada: Callable[[str], str] = input,
        salida: Callable[[str], None] = print,
        hoy: Callable[[], date] | None = None,
    ) -> None:
        self._catalogo = catalogo
        self._usuarios = usuarios
        self._prestamos = prestamos
        self._notificaciones = notificaciones
        self._reportes = reportes
        self._entrada = entrada
        self._salida = salida
        self._hoy = hoy or date.today
        self._seguir = True

    def ejecutar(self) -> None:
        self._escribir("SIGEB — biblioteca")
        while self._seguir:
            self._escribir("")
            self._escribir("1. Registrar libro")
            self._escribir("2. Listar libros")
            self._escribir("3. Buscar libro")
            self._escribir("4. Consultar disponibilidad")
            self._escribir("5. Agregar ejemplares")
            self._escribir("6. Registrar usuario")
            self._escribir("7. Listar usuarios")
            self._escribir("8. Historial de préstamos")
            self._escribir("9. Prestar ejemplar")
            self._escribir("10. Devolver préstamo")
            self._escribir("11. Consultar préstamos")
            self._escribir("12. Enviar notificación")
            self._escribir("13. Generar reporte")
            self._escribir("0. Salir")
            try:
                opcion = self._leer("Opción: ")
            except EOFError:
                self._escribir("")
                return
            accion = {
                "1": self._registrar_libro,
                "2": self._listar_libros,
                "3": self._buscar_libro,
                "4": self._consultar_disponibilidad,
                "5": self._agregar_ejemplares,
                "6": self._registrar_usuario,
                "7": self._listar_usuarios,
                "8": self._historial,
                "9": self._prestar,
                "10": self._devolver,
                "11": self._consultar_prestamos,
                "12": self._enviar_notificacion,
                "13": self._generar_reporte,
                "0": self._salir,
            }.get(opcion)
            if accion is None:
                self._escribir("Opción no válida.")
                continue
            try:
                accion()
            except ErrorDominio as exc:
                self._escribir(f"Error: {exc}")
            except EOFError:
                self._escribir("")
                return
            if opcion != "0":
                try:
                    self._pausar()
                except EOFError:
                    self._escribir("")
                    return

    def _registrar_libro(self) -> None:
        isbn = self._leer("ISBN: ")
        titulo = self._leer("Título: ")
        autor = self._leer("Autor: ")
        categoria = self._leer("Categoría: ")
        ejemplares = self._leer_entero("Ejemplares: ")
        if ejemplares is None:
            return
        libro = self._catalogo.registrar_libro(isbn, titulo, autor, categoria, ejemplares)
        self._escribir(f"Libro registrado. {self._formato_libro(libro)}")

    def _listar_libros(self) -> None:
        libros = self._catalogo.listar()
        if not libros:
            self._escribir("No hay libros para mostrar.")
            return
        self._escribir(f"Libros registrados: {len(libros)}")
        self._escribir_libros(libros)

    def _buscar_libro(self) -> None:
        self._escribir("Buscar por: 1) ISBN  2) título  3) autor")
        criterio = self._leer("Criterio: ")
        if criterio == "1":
            libros = self._catalogo.buscar(isbn=self._leer("ISBN: "))
        elif criterio == "2":
            libros = self._catalogo.buscar(titulo=self._leer("Título: "))
        elif criterio == "3":
            libros = self._catalogo.buscar(autor=self._leer("Autor: "))
        else:
            raise DatosInvalidos("El criterio debe ser 1, 2 o 3.")
        self._escribir_libros(libros)

    def _consultar_disponibilidad(self) -> None:
        libro = self._catalogo.consultar_disponibilidad(self._leer("ISBN: "))
        self._escribir(self._formato_libro(libro))

    def _agregar_ejemplares(self) -> None:
        isbn = self._leer("ISBN: ")
        cantidad = self._leer_entero("Cantidad: ")
        if cantidad is None:
            return
        libro = self._catalogo.agregar_ejemplares(isbn, cantidad)
        self._escribir(f"Ejemplares actualizados. {self._formato_libro(libro)}")

    def _registrar_usuario(self) -> None:
        id_usuario = self._leer("Id: ")
        nombre = self._leer("Nombre: ")
        self._escribir(f"Tipo ({', '.join(TIPOS_USUARIO)})")
        tipo = self._leer("Tipo: ")
        activo = self._leer_si_no("¿Activo? (s/n) [s]: ")
        if activo is None:
            return
        usuario = self._usuarios.registrar_usuario(id_usuario, nombre, tipo, activo)
        self._escribir(f"Usuario registrado. {self._formato_usuario(usuario)}")

    def _listar_usuarios(self) -> None:
        usuarios = self._usuarios.listar()
        if not usuarios:
            self._escribir("No hay usuarios registrados.")
            return
        self._escribir(f"Usuarios registrados: {len(usuarios)}")
        for usuario in usuarios:
            self._escribir(self._formato_usuario(usuario))

    def _historial(self) -> None:
        prestamos = self._prestamos.historial(self._leer("Id de usuario: "))
        self._escribir_prestamos(prestamos)

    def _prestar(self) -> None:
        prestamo = self._prestamos.prestar(
            self._leer("ISBN: "),
            self._leer("Id de usuario: "),
            self._fecha(),
        )
        self._escribir(f"Préstamo registrado. {self._formato_prestamo(prestamo)}")

    def _devolver(self) -> None:
        prestamo = self._prestamos.devolver(self._leer("Id de préstamo: "), self._fecha())
        self._escribir(f"Devolución registrada. {self._formato_prestamo(prestamo)}")

    def _consultar_prestamos(self) -> None:
        self._escribir("Estado: activo, devuelto o vencido")
        prestamos = self._prestamos.consultar(self._leer("Estado: "), self._fecha())
        self._escribir_prestamos(prestamos)

    def _enviar_notificacion(self) -> None:
        canales = ", ".join(self._notificaciones.canales)
        self._escribir(f"Canal ({canales})")
        canal = self._leer("Canal: ")
        destino = self._leer("Destino (vacío si el canal es consola): ")
        mensaje = self._leer("Mensaje: ")
        enviado = self._notificaciones.enviar(canal, mensaje, destino or None)
        self._escribir(f"Notificación enviada por {enviado}.")

    def _generar_reporte(self) -> None:
        titulo = self._leer("Título: ")
        resumen = self._leer_si_no("¿Incluir resumen? (s/n) [s]: ")
        if resumen is None:
            return
        detalle = self._leer_si_no("¿Incluir detalle? (s/n) [s]: ")
        if detalle is None:
            return
        pie = self._leer_si_no("¿Incluir pie? (s/n) [s]: ")
        if pie is None:
            return
        reporte = self._reportes.generar(titulo, resumen, detalle, pie, self._fecha())
        self._escribir(reporte.texto())

    def _salir(self) -> None:
        self._seguir = False
        self._escribir("Hasta luego.")

    def _fecha(self) -> date:
        return self._hoy()

    def _leer(self, etiqueta: str) -> str:
        return self._entrada(etiqueta).strip()

    def _pausar(self) -> None:
        self._leer("Presione Enter para continuar...")

    def _leer_entero(self, etiqueta: str) -> int | None:
        texto = self._leer(etiqueta)
        try:
            return int(texto)
        except ValueError:
            self._escribir("Ingrese un número entero.")
            return None

    def _leer_si_no(self, etiqueta: str) -> bool | None:
        texto = self._leer(etiqueta).lower() or "s"
        if texto in {"s", "si", "sí"}:
            return True
        if texto in {"n", "no"}:
            return False
        self._escribir("Responda s o n.")
        return None

    def _escribir(self, mensaje: str) -> None:
        self._salida(mensaje)
        if self._salida is print:
            sys.stdout.flush()

    def _escribir_libros(self, libros: list[Libro]) -> None:
        if not libros:
            self._escribir("No hay libros para mostrar.")
            return
        for libro in libros:
            self._escribir(self._formato_libro(libro))

    def _escribir_prestamos(self, prestamos: list[Prestamo]) -> None:
        if not prestamos:
            self._escribir("No hay préstamos para mostrar.")
            return
        for prestamo in prestamos:
            self._escribir(self._formato_prestamo(prestamo))

    @staticmethod
    def _formato_libro(libro: Libro) -> str:
        return (
            f"{libro.isbn} | {libro.titulo} | {libro.autor} | {libro.categoria} | "
            f"disponibles {libro.ejemplares_disponibles} de {libro.ejemplares_totales}"
        )

    @staticmethod
    def _formato_usuario(usuario: Usuario) -> str:
        estado = "activo" if usuario.activo else "inactivo"
        return f"{usuario.id_usuario} | {usuario.nombre} | {usuario.tipo} | {estado}"

    @staticmethod
    def _formato_prestamo(prestamo: Prestamo) -> str:
        if prestamo.fecha_devolucion is None:
            devolucion = "sin devolver"
        else:
            devolucion = prestamo.fecha_devolucion.isoformat()
        return (
            f"{prestamo.id_prestamo} | ISBN {prestamo.isbn_libro} | "
            f"usuario {prestamo.id_usuario} | "
            f"{prestamo.fecha_inicio.isoformat()} a {prestamo.fecha_limite.isoformat()} | "
            f"{devolucion}"
        )
