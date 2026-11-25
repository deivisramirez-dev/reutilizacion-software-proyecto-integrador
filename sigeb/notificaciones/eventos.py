"""Observer. Publicar un evento no entrega el aviso: lo hacen los suscriptores."""

from abc import ABC, abstractmethod
from collections.abc import Callable

from sigeb.dominio.errores import ErrorDominio


class Evento:
    def __init__(
        self,
        tipo: str,
        id_prestamo: str,
        isbn_libro: str,
        id_usuario: str,
        mensaje: str,
    ) -> None:
        self.tipo = tipo
        self.id_prestamo = id_prestamo
        self.isbn_libro = isbn_libro
        self.id_usuario = id_usuario
        self.mensaje = mensaje


class Observador(ABC):
    @abstractmethod
    def actualizar(self, evento: Evento) -> None:
        """Reacciona a un evento ya publicado."""


class CentroEventos:
    def __init__(self) -> None:
        self._observadores: list[Observador] = []

    def suscribir(self, observador: Observador) -> None:
        if observador not in self._observadores:
            self._observadores.append(observador)

    def publicar(self, evento: Evento) -> None:
        for observador in list(self._observadores):
            observador.actualizar(evento)


class ObservadorNotificacion(Observador):
    """Convierte el evento en una notificación. Un fallo de envío queda registrado."""

    def __init__(self, enviar: Callable[[str], None]) -> None:
        self._enviar = enviar
        self.recibidos: list[Evento] = []
        self.fallos: list[str] = []

    def actualizar(self, evento: Evento) -> None:
        self.recibidos.append(evento)
        try:
            self._enviar(evento.mensaje)
        except ErrorDominio as exc:
            self.fallos.append(str(exc))
