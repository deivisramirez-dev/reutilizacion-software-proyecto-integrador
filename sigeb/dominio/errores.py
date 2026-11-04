"""Errores de negocio. La presentación los muestra; no decide la regla."""


class ErrorDominio(Exception):
    """Una operación incumple una regla del dominio."""


class DatosInvalidos(ErrorDominio):
    """Algún dato de entrada no cumple el formato o el rango exigido."""


class IsbnDuplicado(ErrorDominio):
    """Ya existe un título con ese ISBN."""

    def __init__(self, isbn: str) -> None:
        self.isbn = isbn
        super().__init__(f"Ya existe un libro con ISBN {isbn}.")


class LibroNoEncontrado(ErrorDominio):
    """No hay un título registrado con ese ISBN."""

    def __init__(self, isbn: str) -> None:
        self.isbn = isbn
        super().__init__(f"No existe un libro con ISBN {isbn}.")


class UsuarioDuplicado(ErrorDominio):
    """Ya existe un usuario con ese identificador."""

    def __init__(self, id_usuario: str) -> None:
        self.id_usuario = id_usuario
        super().__init__(f"Ya existe un usuario con id {id_usuario}.")


class UsuarioNoEncontrado(ErrorDominio):
    """No hay un usuario registrado con ese identificador."""

    def __init__(self, id_usuario: str) -> None:
        self.id_usuario = id_usuario
        super().__init__(f"No existe un usuario con id {id_usuario}.")


class UsuarioInactivo(ErrorDominio):
    """El usuario está registrado, pero no puede prestar."""

    def __init__(self, id_usuario: str) -> None:
        self.id_usuario = id_usuario
        super().__init__(f"El usuario {id_usuario} está inactivo.")


class SinDisponibilidad(ErrorDominio):
    """El título no tiene ejemplares disponibles."""

    def __init__(self, isbn: str) -> None:
        self.isbn = isbn
        super().__init__(f"No hay ejemplares disponibles del ISBN {isbn}.")


class PrestamoNoEncontrado(ErrorDominio):
    """No hay un préstamo con ese identificador."""

    def __init__(self, id_prestamo: str) -> None:
        self.id_prestamo = id_prestamo
        super().__init__(f"No existe el préstamo {id_prestamo}.")


class PrestamoYaDevuelto(ErrorDominio):
    """El préstamo ya tiene fecha de devolución."""

    def __init__(self, id_prestamo: str) -> None:
        self.id_prestamo = id_prestamo
        super().__init__(f"El préstamo {id_prestamo} ya fue devuelto.")
