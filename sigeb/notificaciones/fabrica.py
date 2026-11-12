"""Factory Method. El consumidor pide `crear()` y no elige la clase concreta."""

from abc import ABC, abstractmethod
from collections.abc import Callable

from sigeb.dominio.errores import DatosInvalidos
from sigeb.infraestructura.proveedor_sms_simulado import ProveedorSMSSimulado
from sigeb.notificaciones.adaptador_sms import AdaptadorSMS
from sigeb.notificaciones.canales import Notificacion, NotificacionConsola, NotificacionCorreo

CANALES = ("consola", "correo", "sms")


class FabricaNotificacion(ABC):
    @abstractmethod
    def crear(self) -> Notificacion:
        """Devuelve el canal concreto de esta fábrica."""


class FabricaConsola(FabricaNotificacion):
    def __init__(self, salida: Callable[[str], None]) -> None:
        self._salida = salida

    def crear(self) -> Notificacion:
        return NotificacionConsola(self._salida)


class FabricaCorreo(FabricaNotificacion):
    def __init__(self, destinatario: str, buzon: list[tuple[str, str]]) -> None:
        self._destinatario = destinatario
        self._buzon = buzon

    def crear(self) -> Notificacion:
        return NotificacionCorreo(self._destinatario, self._buzon)


class FabricaSMS(FabricaNotificacion):
    def __init__(self, proveedor: ProveedorSMSSimulado, destino: str) -> None:
        self._proveedor = proveedor
        self._destino = destino

    def crear(self) -> Notificacion:
        return AdaptadorSMS(self._proveedor, self._destino)


def fabrica_para(
    canal: str,
    *,
    salida: Callable[[str], None],
    buzon: list[tuple[str, str]],
    proveedor: ProveedorSMSSimulado,
    destino: str | None,
) -> FabricaNotificacion:
    """Único lugar que asocia el nombre del canal con su fábrica."""
    nombre = nombre_canal(canal)
    if nombre == "consola":
        return FabricaConsola(salida)
    if nombre == "correo":
        return FabricaCorreo(destino or "", buzon)
    return FabricaSMS(proveedor, destino or "")


def nombre_canal(canal: str) -> str:
    if not isinstance(canal, str):
        raise DatosInvalidos("El canal debe ser consola, correo o sms.")
    nombre = canal.strip().lower()
    if nombre not in CANALES:
        raise DatosInvalidos("El canal debe ser consola, correo o sms.")
    return nombre
