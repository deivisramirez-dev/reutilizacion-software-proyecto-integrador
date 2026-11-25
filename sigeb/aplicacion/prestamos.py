"""Casos de uso de préstamo y devolución (RF-08 a RF-14, RF-17, RF-19 y RF-20).

El plazo y el cupo los resuelve una política Strategy. Al confirmar la
operación se publica un evento; quien no está suscrito no se entera.
"""

from datetime import date, timedelta

from sigeb.dominio.errores import (
    CupoAgotado,
    DatosInvalidos,
    ErrorDominio,
    LibroNoEncontrado,
    PrestamoNoEncontrado,
    PrestamoYaDevuelto,
    SinDisponibilidad,
    UsuarioInactivo,
    UsuarioNoEncontrado,
)
from sigeb.dominio.politicas import politica_para
from sigeb.dominio.prestamo import Prestamo
from sigeb.infraestructura.repositorio_libros import RepositorioLibros
from sigeb.infraestructura.repositorio_prestamos import RepositorioPrestamos
from sigeb.infraestructura.repositorio_usuarios import RepositorioUsuarios
from sigeb.notificaciones.eventos import CentroEventos, Evento

ESTADOS = ("activo", "devuelto", "vencido")


class ServicioPrestamos:
    def __init__(
        self,
        prestamos: RepositorioPrestamos,
        libros: RepositorioLibros,
        usuarios: RepositorioUsuarios,
        eventos: CentroEventos | None = None,
    ) -> None:
        self._prestamos = prestamos
        self._libros = libros
        self._usuarios = usuarios
        self._eventos = eventos if eventos is not None else CentroEventos()

    def prestar(self, isbn: str, id_usuario: str, hoy: date) -> Prestamo:
        """Valida, guarda el préstamo, descuenta un ejemplar y publica el evento.

        Si descontar falla, el préstamo guardado se elimina (RN-12). Un fallo
        al avisar no deshace el préstamo (RN-13). `hoy` llega desde afuera (RN-11).
        """
        fecha = _fecha(hoy)
        libro = self._libro(isbn)
        usuario = self._usuario(id_usuario)
        if not usuario.activo:
            raise UsuarioInactivo(usuario.id_usuario)
        politica = politica_para(usuario.tipo)
        if self._activos(usuario.id_usuario) >= politica.maximo_activos():
            raise CupoAgotado(usuario.id_usuario, politica.maximo_activos())
        if libro.ejemplares_disponibles <= 0:
            raise SinDisponibilidad(libro.isbn)

        prestamo = Prestamo(
            id_prestamo=self._prestamos.siguiente_id(),
            isbn_libro=libro.isbn,
            id_usuario=usuario.id_usuario,
            fecha_inicio=fecha,
            fecha_limite=fecha + timedelta(days=politica.dias_permitidos()),
        )
        self._prestamos.guardar(prestamo)
        try:
            libro.descontar()
        except Exception:
            self._prestamos.eliminar(prestamo.id_prestamo)
            raise
        self._publicar("prestamo", prestamo)
        return prestamo

    def devolver(self, id_prestamo: str, hoy: date) -> Prestamo:
        """Marca la devolución, repone un ejemplar y publica el evento.

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
        self._publicar("devolucion", prestamo)
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

    def _activos(self, id_usuario: str) -> int:
        return sum(
            1
            for prestamo in self._prestamos.listar()
            if prestamo.id_usuario == id_usuario and prestamo.esta_activo()
        )

    def _publicar(self, tipo: str, prestamo: Prestamo) -> None:
        if tipo == "prestamo":
            mensaje = (
                f"Préstamo {prestamo.id_prestamo}: ISBN {prestamo.isbn_libro} "
                f"para {prestamo.id_usuario}, hasta {prestamo.fecha_limite.isoformat()}."
            )
        else:
            mensaje = (
                f"Devolución {prestamo.id_prestamo}: ISBN {prestamo.isbn_libro} "
                f"del usuario {prestamo.id_usuario}."
            )
        try:
            self._eventos.publicar(
                Evento(
                    tipo,
                    prestamo.id_prestamo,
                    prestamo.isbn_libro,
                    prestamo.id_usuario,
                    mensaje,
                )
            )
        except ErrorDominio:
            return


def _fecha(valor: date) -> date:
    if type(valor) is not date:
        raise DatosInvalidos("La fecha debe ser un día de calendario.")
    return valor
