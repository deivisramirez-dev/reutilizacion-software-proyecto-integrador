"""Contrato `enviar(mensaje)` y los canales que SIGEB conoce directamente."""

from abc import ABC, abstractmethod
from collections.abc import Callable

from sigeb.dominio.errores import DatosInvalidos


class Notificacion(ABC):
    @abstractmethod
    def enviar(self, mensaje: str) -> None:
        """Entrega el mensaje por este canal."""


class NotificacionConsola(Notificacion):
    def __init__(self, salida: Callable[[str], None]) -> None:
        self._salida = salida

    def enviar(self, mensaje: str) -> None:
        self._salida(_mensaje(mensaje))


class NotificacionCorreo(Notificacion):
    def __init__(self, destinatario: str, buzon: list[tuple[str, str]]) -> None:
        self._destinatario = _correo(destinatario)
        self._buzon = buzon

    def enviar(self, mensaje: str) -> None:
        self._buzon.append((self._destinatario, _mensaje(mensaje)))


def _mensaje(mensaje: str) -> str:
    if not isinstance(mensaje, str) or not mensaje.strip():
        raise DatosInvalidos("El mensaje no puede estar vacío.")
    return mensaje.strip()


def _correo(valor: str) -> str:
    if not isinstance(valor, str):
        raise DatosInvalidos("El destinatario debe ser un correo.")
    correo = valor.strip()
    if "@" not in correo or correo.startswith("@") or correo.endswith("@"):
        raise DatosInvalidos("El destinatario debe ser un correo.")
    return correo
