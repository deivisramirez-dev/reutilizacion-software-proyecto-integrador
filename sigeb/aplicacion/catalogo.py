"""Casos de uso del catálogo (RF-01 a RF-05)."""

from sigeb.dominio.errores import DatosInvalidos, IsbnDuplicado, LibroNoEncontrado
from sigeb.dominio.libro import Libro
from sigeb.infraestructura.repositorio_libros import RepositorioLibros


class ServicioCatalogo:
    def __init__(self, libros: RepositorioLibros) -> None:
        self._libros = libros

    def registrar_libro(
        self,
        isbn: str,
        titulo: str,
        autor: str,
        categoria: str,
        ejemplares: int,
    ) -> Libro:
        """Registra un título. `ejemplares` inicia totales y disponibles por igual."""
        if not isinstance(isbn, str) or not isbn.strip():
            raise DatosInvalidos("El ISBN no puede estar vacío.")
        isbn_limpio = isbn.strip()
        if self._libros.existe(isbn_limpio):
            raise IsbnDuplicado(isbn_limpio)
        libro = Libro(
            isbn=isbn_limpio,
            titulo=titulo,
            autor=autor,
            categoria=categoria,
            ejemplares_totales=ejemplares,
            ejemplares_disponibles=ejemplares,
        )
        self._libros.guardar(libro)
        return libro

    def listar(self) -> list[Libro]:
        return self._libros.listar()

    def buscar(
        self,
        *,
        isbn: str | None = None,
        titulo: str | None = None,
        autor: str | None = None,
    ) -> list[Libro]:
        """ISBN exacto. Título y autor por coincidencia parcial, sin distinguir mayúsculas.

        Si se indican varios criterios, el libro debe cumplir todos.
        """
        isbn_limpio = _criterio(isbn, "El ISBN", normalizar=False)
        titulo_limpio = _criterio(titulo, "El título", normalizar=True)
        autor_limpio = _criterio(autor, "El autor", normalizar=True)
        if isbn_limpio is None and titulo_limpio is None and autor_limpio is None:
            raise DatosInvalidos("Indique ISBN, título o autor para buscar.")

        encontrados: list[Libro] = []
        for libro in self._libros.listar():
            if isbn_limpio is not None and libro.isbn != isbn_limpio:
                continue
            if titulo_limpio is not None and titulo_limpio not in libro.titulo.lower():
                continue
            if autor_limpio is not None and autor_limpio not in libro.autor.lower():
                continue
            encontrados.append(libro)
        return encontrados

    def consultar_disponibilidad(self, isbn: str) -> Libro:
        return self._exigir(isbn)

    def agregar_ejemplares(self, isbn: str, cantidad: int) -> Libro:
        """Suma la misma cantidad a totales y a disponibles."""
        libro = self._exigir(isbn)
        libro.agregar_ejemplares(cantidad)
        return libro

    def _exigir(self, isbn: str) -> Libro:
        if not isinstance(isbn, str) or not isbn.strip():
            raise DatosInvalidos("El ISBN no puede estar vacío.")
        libro = self._libros.obtener(isbn.strip())
        if libro is None:
            raise LibroNoEncontrado(isbn.strip())
        return libro


def _criterio(valor: str | None, nombre: str, *, normalizar: bool) -> str | None:
    if valor is None:
        return None
    if not isinstance(valor, str):
        raise DatosInvalidos(f"{nombre} debe ser texto.")
    limpio = valor.strip()
    if not limpio:
        raise DatosInvalidos(f"{nombre} no puede estar vacío.")
    if normalizar:
        return limpio.lower()
    return limpio
