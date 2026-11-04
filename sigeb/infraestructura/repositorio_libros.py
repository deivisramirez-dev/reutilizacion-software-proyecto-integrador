"""Catálogo de títulos en memoria, indexado por ISBN."""

from sigeb.dominio.libro import Libro


class RepositorioLibros:
    def __init__(self) -> None:
        self._libros: dict[str, Libro] = {}

    def guardar(self, libro: Libro) -> None:
        self._libros[libro.isbn] = libro

    def obtener(self, isbn: str) -> Libro | None:
        return self._libros.get(isbn)

    def existe(self, isbn: str) -> bool:
        return isbn in self._libros

    def listar(self) -> list[Libro]:
        return [self._libros[isbn] for isbn in sorted(self._libros)]
