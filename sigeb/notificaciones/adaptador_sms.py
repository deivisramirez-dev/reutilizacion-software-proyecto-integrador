"""Adapter: `enviar(mensaje)` se convierte en `despachar(numero, cuerpo)`."""

from sigeb.dominio.errores import DatosInvalidos, ErrorNotificacion
from sigeb.infraestructura.proveedor_sms_simulado import ErrorProveedorSMS, ProveedorSMSSimulado
from sigeb.notificaciones.canales import Notificacion


class AdaptadorSMS(Notificacion):
    def __init__(self, proveedor: ProveedorSMSSimulado, destino: str) -> None:
        self._proveedor = proveedor
        self._destino = _numero(destino)

    def enviar(self, mensaje: str) -> None:
        if not isinstance(mensaje, str) or not mensaje.strip():
            raise DatosInvalidos("El mensaje no puede estar vacío.")
        try:
            self._proveedor.despachar(self._destino, mensaje.strip())
        except ErrorProveedorSMS as exc:
            raise ErrorNotificacion(str(exc)) from exc


def _numero(valor: str) -> str:
    if not isinstance(valor, str):
        raise DatosInvalidos("El número de destino debe ser texto.")
    limpio = valor.strip().replace(" ", "")
    digitos = limpio[1:] if limpio.startswith("+") else limpio
    if not digitos.isdigit() or len(digitos) < 7:
        raise DatosInvalidos("El número de destino no es válido.")
    return limpio
