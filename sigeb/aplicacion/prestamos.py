"""Casos de uso de préstamo y devolución (RF-08 a RF-14).

Semana 1: el plazo es fijo. En la semana 7 lo resuelve una política Strategy.
"""

from datetime import date, timedelta

from sigeb.dominio.errores import (
    DatosInvalidos,
    LibroNoEncontrado,
    PrestamoNoEncontrado,
    PrestamoYaDevuelto,
    SinDisponibilidad,
    UsuarioInactivo,
    UsuarioNoEncontrado,
)
from sigeb.dominio.prestamo import Prestamo
from sigeb.infraestructura.repositorio_libros import RepositorioLibros
from sigeb.infraestructura.repositorio_prestamos import RepositorioPrestamos
from sigeb.infraestructura.repositorio_usuarios import RepositorioUsuarios

PLAZO_DIAS = 7
ESTADOS = ("activo", "devuelto", "vencido")


class ServicioPrestamos:
    def __init__(
        self,
        prestamos: RepositorioPrestamos,
        libros: RepositorioLibros,
        usuarios: RepositorioUsuarios,
    ) -> None:
        self._prestamos = prestamos
        self._libros = libros
        self._usuarios = usuarios

    def prestar(self, isbn: str, id_usuario: str, hoy: date) -> Prestamo:
        """Valida, guarda el préstamo y después descuenta un ejemplar.

        Si descontar falla, el préstamo guardado se elimina. Así el inventario
        y el historial no quedan a medias (RN-12). `hoy` llega desde afuera:
        este servicio no consulta el reloj (RN-11).
        """
        fecha = _fecha(hoy)
        libro = self._libro(isbn)
        usuario = self._usuario(id_usuario)
        if not usuario.activo:
            raise UsuarioInactivo(usuario.id_usuario)
        if libro.ejemplares_disponibles <= 0:
            raise SinDisponibilidad(libro.isbn)

        prestamo = Prestamo(
            id_prestamo=self._prestamos.siguiente_id(),
            isbn_libro=libro.isbn,
            id_usuario=usuario.id_usuario,
            fecha_inicio=fecha,
            fecha_limite=fecha + timedelta(days=PLAZO_DIAS),
        )
        self._prestamos.guardar(prestamo)
        try:
            libro.descontar()
        except Exception:
            self._prestamos.eliminar(prestamo.id_prestamo)
            raise
        return prestamo

    def devolver(self, id_prestamo: str, hoy: date) -> Prestamo:
        """Marca la devolución y repone un ejemplar.

        Una segunda devolución falla antes de tocar el inventario (RN-06, RN-07).
        """
        fecha = _fecha(hoy)
        prestamo = self._prestamo(id_prestamo)
        if prestamo.esta_devuelto():
            raise PrestamoYaDevuelto(prestamo.id_prestamo)
        libro = self._libro(prestamo.isbn_libro)
        prestamo.marcar_devuelto(fecha)
        try:
            libro.reponer()
        except Exception:
            prestamo.fecha_devolucion = None
            raise
        return prestamo

    def historial(self, id_usuario: str) -> list[Prestamo]:
        """Préstamos de un usuario, devueltos y no devueltos."""
        usuario = self._usuario(id_usuario)
        return [
            prestamo
            for prestamo in self._prestamos.listar()
            if prestamo.id_usuario == usuario.id_usuario
        ]

    def consultar(self, estado: str, hoy: date) -> list[Prestamo]:
        """Tres vistas disjuntas.

        - activo: sin devolver y aún dentro del plazo
        - vencido: sin devolver y hoy posterior a la fecha límite
        - devuelto: con fecha de devolución
        """
        if not isinstance(estado, str):
            raise DatosInvalidos("El estado debe ser activo, devuelto o vencido.")
        estado_limpio = estado.strip().lower()
        if estado_limpio not in ESTADOS:
            raise DatosInvalidos("El estado debe ser activo, devuelto o vencido.")
        fecha = _fecha(hoy)

        resultado: list[Prestamo] = []
        for prestamo in self._prestamos.listar():
            vencido = prestamo.esta_vencido(fecha)
            if estado_limpio == "devuelto" and prestamo.esta_devuelto():
                resultado.append(prestamo)
            elif estado_limpio == "vencido" and vencido:
                resultado.append(prestamo)
            elif estado_limpio == "activo" and prestamo.esta_activo() and not vencido:
                resultado.append(prestamo)
        return resultado

    def _libro(self, isbn: str):
        if not isinstance(isbn, str) or not isbn.strip():
            raise DatosInvalidos("El ISBN no puede estar vacío.")
        libro = self._libros.obtener(isbn.strip())
        if libro is None:
            raise LibroNoEncontrado(isbn.strip())
        return libro

    def _usuario(self, id_usuario: str):
        if not isinstance(id_usuario, str) or not id_usuario.strip():
            raise DatosInvalidos("El id de usuario no puede estar vacío.")
        usuario = self._usuarios.obtener(id_usuario.strip())
        if usuario is None:
            raise UsuarioNoEncontrado(id_usuario.strip())
        return usuario

    def _prestamo(self, id_prestamo: str) -> Prestamo:
        if not isinstance(id_prestamo, str) or not id_prestamo.strip():
            raise DatosInvalidos("El id de préstamo no puede estar vacío.")
        prestamo = self._prestamos.obtener(id_prestamo.strip())
        if prestamo is None:
            raise PrestamoNoEncontrado(id_prestamo.strip())
        return prestamo


def _fecha(valor: date) -> date:
    if type(valor) is not date:
        raise DatosInvalidos("La fecha debe ser un día de calendario.")
    return valor
