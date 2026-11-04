"""Punto de entrada de SIGEB. Arma repositorios, servicios y menú."""

from sigeb.aplicacion.catalogo import ServicioCatalogo
from sigeb.aplicacion.prestamos import ServicioPrestamos
from sigeb.aplicacion.usuarios import ServicioUsuarios
from sigeb.infraestructura.repositorio_libros import RepositorioLibros
from sigeb.infraestructura.repositorio_prestamos import RepositorioPrestamos
from sigeb.infraestructura.repositorio_usuarios import RepositorioUsuarios
from sigeb.presentacion.menu import MenuConsola


def construir_menu() -> MenuConsola:
    libros = RepositorioLibros()
    usuarios = RepositorioUsuarios()
    prestamos = RepositorioPrestamos()
    return MenuConsola(
        ServicioCatalogo(libros),
        ServicioUsuarios(usuarios),
        ServicioPrestamos(prestamos, libros, usuarios),
    )


def main() -> None:
    construir_menu().ejecutar()


if __name__ == "__main__":
    main()
