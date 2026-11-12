"""Envío por canal. No inspecciona la clase concreta: pide `crear()` y `enviar()`."""

from collections.abc import Callable

from sigeb.dominio.errores import DatosInvalidos
from sigeb.infraestructura.proveedor_sms_simulado import ProveedorSMSSimulado
from sigeb.notificaciones.fabrica import CANALES, fabrica_para, nombre_canal


class ServicioNotificaciones:
    canales = CANALES

    def __init__(
        self,
        proveedor: ProveedorSMSSimulado,
        salida: Callable[[str], None] = print,
    ) -> None:
        self._proveedor = proveedor
        self._salida = salida
        self._buzon: list[tuple[str, str]] = []

    @property
    def buzon(self) -> list[tuple[str, str]]:
        return list(self._buzon)

    def enviar(self, canal: str, mensaje: str, destino: str | None = None) -> str:
        if not isinstance(mensaje, str) or not mensaje.strip():
            raise DatosInvalidos("El mensaje no puede estar vacío.")
        nombre = nombre_canal(canal)
        destino_limpio = destino.strip() if isinstance(destino, str) else None
        fabrica = fabrica_para(
            nombre,
            salida=self._salida,
            buzon=self._buzon,
            proveedor=self._proveedor,
            destino=destino_limpio or None,
        )
        fabrica.crear().enviar(mensaje.strip())
        return nombre
