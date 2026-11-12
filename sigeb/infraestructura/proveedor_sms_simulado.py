"""API externa simulada. No usa `enviar(mensaje)`: esa traducción es del Adapter."""


class ErrorProveedorSMS(Exception):
    """Fallo propio del proveedor, distinto de los errores de SIGEB."""


class ProveedorSMSSimulado:
    def __init__(self) -> None:
        self.enviados: list[dict[str, str]] = []

    def despachar(self, numero_destino: str, cuerpo: str) -> str:
        if not isinstance(numero_destino, str) or not numero_destino.strip():
            raise ErrorProveedorSMS("El proveedor rechazó el destino.")
        if not isinstance(cuerpo, str) or not cuerpo.strip():
            raise ErrorProveedorSMS("El proveedor rechazó el cuerpo del mensaje.")
        referencia = f"SMS-{len(self.enviados) + 1:04d}"
        self.enviados.append(
            {
                "numero_destino": numero_destino.strip(),
                "cuerpo": cuerpo.strip(),
                "referencia": referencia,
            }
        )
        return referencia
