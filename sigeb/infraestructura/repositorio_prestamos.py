"""Préstamos en memoria. El contador de ids solo crece."""

from sigeb.dominio.prestamo import Prestamo


class RepositorioPrestamos:
    def __init__(self) -> None:
        self._prestamos: dict[str, Prestamo] = {}
        self._secuencia = 0

    def siguiente_id(self) -> str:
        self._secuencia += 1
        return f"P-{self._secuencia:04d}"

    def guardar(self, prestamo: Prestamo) -> None:
        self._prestamos[prestamo.id_prestamo] = prestamo

    def eliminar(self, id_prestamo: str) -> None:
        """Quita un préstamo recién guardado si la operación no pudo completarse."""
        self._prestamos.pop(id_prestamo, None)

    def obtener(self, id_prestamo: str) -> Prestamo | None:
        return self._prestamos.get(id_prestamo)

    def listar(self) -> list[Prestamo]:
        return [self._prestamos[clave] for clave in sorted(self._prestamos)]
