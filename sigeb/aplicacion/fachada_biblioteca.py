"""Puerta única del subsistema. El menú no conoce repositorios ni servicios internos."""

from datetime import date

from sigeb.aplicacion.catalogo import ServicioCatalogo
from sigeb.aplicacion.notificaciones import ServicioNotificaciones
from sigeb.aplicacion.prestamos import ServicioPrestamos
from sigeb.aplicacion.reportes import ServicioReportes
from sigeb.aplicacion.usuarios import ServicioUsuarios
from sigeb.dominio.libro import Libro
from sigeb.dominio.prestamo import Prestamo
from sigeb.dominio.usuario import TIPOS_USUARIO, Usuario
from sigeb.reportes.reporte import Reporte


class BibliotecaFacade:
    def __init__(
        self,
        catalogo: ServicioCatalogo,
        usuarios: ServicioUsuarios,
        prestamos: ServicioPrestamos,
        notificaciones: ServicioNotificaciones,
        reportes: ServicioReportes,
    ) -> None:
        self._catalogo = catalogo
        self._usuarios = usuarios
        self._prestamos = prestamos
        self._notificaciones = notificaciones
        self._reportes = reportes

    @property
    def tipos_usuario(self) -> tuple[str, ...]:
        return TIPOS_USUARIO

    @property
    def canales(self) -> tuple[str, ...]:
        return self._notificaciones.canales

    def registrar_libro(
        self,
        isbn: str,
        titulo: str,
        autor: str,
        categoria: str,
        ejemplares: int,
    ) -> Libro:
        return self._catalogo.registrar_libro(isbn, titulo, autor, categoria, ejemplares)

    def listar_libros(self) -> list[Libro]:
        return self._catalogo.listar()

    def buscar_libro(
        self,
        *,
        isbn: str | None = None,
        titulo: str | None = None,
        autor: str | None = None,
    ) -> list[Libro]:
        return self._catalogo.buscar(isbn=isbn, titulo=titulo, autor=autor)

    def consultar_disponibilidad(self, isbn: str) -> Libro:
        return self._catalogo.consultar_disponibilidad(isbn)

    def agregar_ejemplares(self, isbn: str, cantidad: int) -> Libro:
        return self._catalogo.agregar_ejemplares(isbn, cantidad)

    def registrar_usuario(
        self,
        id_usuario: str,
        nombre: str,
        tipo: str,
        activo: bool = True,
    ) -> Usuario:
        return self._usuarios.registrar_usuario(id_usuario, nombre, tipo, activo)

    def listar_usuarios(self) -> list[Usuario]:
        return self._usuarios.listar()

    def historial(self, id_usuario: str) -> list[Prestamo]:
        return self._prestamos.historial(id_usuario)

    def prestar(self, isbn: str, id_usuario: str, hoy: date) -> Prestamo:
        return self._prestamos.prestar(isbn, id_usuario, hoy)

    def devolver(self, id_prestamo: str, hoy: date) -> Prestamo:
        return self._prestamos.devolver(id_prestamo, hoy)

    def consultar_prestamos(self, estado: str, hoy: date) -> list[Prestamo]:
        return self._prestamos.consultar(estado, hoy)

    def enviar_notificacion(
        self,
        canal: str,
        mensaje: str,
        destino: str | None = None,
    ) -> str:
        return self._notificaciones.enviar(canal, mensaje, destino)

    def generar_reporte(
        self,
        titulo: str,
        incluir_resumen: bool,
        incluir_detalle: bool,
        incluir_pie: bool,
        hoy: date,
    ) -> Reporte:
        return self._reportes.generar(
            titulo,
            incluir_resumen,
            incluir_detalle,
            incluir_pie,
            hoy,
        )
