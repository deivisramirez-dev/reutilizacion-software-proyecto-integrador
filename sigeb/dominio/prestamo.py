"""Préstamo de un ejemplar a un usuario, entre dos fechas."""

from datetime import date

from sigeb.dominio.errores import DatosInvalidos, PrestamoYaDevuelto


class Prestamo:
    def __init__(
        self,
        id_prestamo: str,
        isbn_libro: str,
        id_usuario: str,
        fecha_inicio: date,
        fecha_limite: date,
        fecha_devolucion: date | None = None,
    ) -> None:
        self.id_prestamo = _texto(id_prestamo, "El id de préstamo")
        self.isbn_libro = _texto(isbn_libro, "El ISBN")
        self.id_usuario = _texto(id_usuario, "El id de usuario")
        self.fecha_inicio = _fecha(fecha_inicio, "La fecha de inicio")
        self.fecha_limite = _fecha(fecha_limite, "La fecha límite")
        if self.fecha_limite < self.fecha_inicio:
            raise DatosInvalidos("La fecha límite no puede ser anterior al inicio.")
        self.fecha_devolucion = (
            None
            if fecha_devolucion is None
            else _fecha(fecha_devolucion, "La fecha de devolución")
        )

    def esta_devuelto(self) -> bool:
        return self.fecha_devolucion is not None

    def esta_activo(self) -> bool:
        """Activo significa que todavía no se devolvió (RN-08)."""
        return self.fecha_devolucion is None

    def esta_vencido(self, hoy: date) -> bool:
        """Vencido = activo y hoy es posterior a la fecha límite (RN-08)."""
        return self.esta_activo() and _fecha(hoy, "La fecha de consulta") > self.fecha_limite

    def marcar_devuelto(self, hoy: date) -> None:
        if self.esta_devuelto():
            raise PrestamoYaDevuelto(self.id_prestamo)
        fecha = _fecha(hoy, "La fecha de devolución")
        if fecha < self.fecha_inicio:
            raise DatosInvalidos(
                "La fecha de devolución no puede ser anterior al inicio del préstamo."
            )
        self.fecha_devolucion = fecha


def _texto(valor: str, nombre: str) -> str:
    if not isinstance(valor, str):
        raise DatosInvalidos(f"{nombre} debe ser texto.")
    limpio = valor.strip()
    if not limpio:
        raise DatosInvalidos(f"{nombre} no puede estar vacío.")
    return limpio


def _fecha(valor: date, nombre: str) -> date:
    if type(valor) is not date:
        raise DatosInvalidos(f"{nombre} debe ser una fecha.")
    return valor
