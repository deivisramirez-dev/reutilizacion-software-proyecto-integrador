"""Título del catálogo. El ISBN identifica un título, no un ejemplar físico."""

from sigeb.dominio.errores import DatosInvalidos


class Libro:
    def __init__(
        self,
        isbn: str,
        titulo: str,
        autor: str,
        categoria: str,
        ejemplares_totales: int,
        ejemplares_disponibles: int,
    ) -> None:
        self.isbn = _texto(isbn, "El ISBN")
        self.titulo = _texto(titulo, "El título")
        self.autor = _texto(autor, "El autor")
        self.categoria = _texto(categoria, "La categoría")
        self.ejemplares_totales = _entero_no_negativo(
            ejemplares_totales, "Los ejemplares totales"
        )
        self.ejemplares_disponibles = _entero_no_negativo(
            ejemplares_disponibles, "Los ejemplares disponibles"
        )
        if self.ejemplares_disponibles > self.ejemplares_totales:
            raise DatosInvalidos(
                "Los ejemplares disponibles no pueden superar a los totales."
            )

    def descontar(self) -> None:
        """Retira un ejemplar disponible. Lo llama el servicio de préstamos."""
        if self.ejemplares_disponibles <= 0:
            raise DatosInvalidos(
                f"No hay ejemplares disponibles del ISBN {self.isbn}."
            )
        self.ejemplares_disponibles -= 1

    def reponer(self) -> None:
        """Devuelve un ejemplar al inventario disponible."""
        if self.ejemplares_disponibles >= self.ejemplares_totales:
            raise DatosInvalidos(
                f"El ISBN {self.isbn} ya tiene todos sus ejemplares disponibles."
            )
        self.ejemplares_disponibles += 1

    def agregar_ejemplares(self, cantidad: int) -> None:
        """Incorpora ejemplares nuevos al título: suben totales y disponibles."""
        cantidad_valida = _entero_no_negativo(cantidad, "La cantidad")
        if cantidad_valida <= 0:
            raise DatosInvalidos("La cantidad de ejemplares debe ser mayor que cero.")
        self.ejemplares_totales += cantidad_valida
        self.ejemplares_disponibles += cantidad_valida


def _texto(valor: str, nombre: str) -> str:
    if not isinstance(valor, str):
        raise DatosInvalidos(f"{nombre} debe ser texto.")
    limpio = valor.strip()
    if not limpio:
        raise DatosInvalidos(f"{nombre} no puede estar vacío.")
    return limpio


def _entero_no_negativo(valor: int, nombre: str) -> int:
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise DatosInvalidos(f"{nombre} debe ser un número entero.")
    if valor < 0:
        raise DatosInvalidos(f"{nombre} no puede ser negativo.")
    return valor
