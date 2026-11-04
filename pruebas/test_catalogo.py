"""Prueba de aceptación 1: un título con dos ejemplares y un solo ISBN."""

import unittest

from sigeb.aplicacion.catalogo import ServicioCatalogo
from sigeb.infraestructura.repositorio_libros import RepositorioLibros


class TestAceptacionCatalogo(unittest.TestCase):
    def setUp(self) -> None:
        self.repositorio = RepositorioLibros()
        self.catalogo = ServicioCatalogo(self.repositorio)

    def test_aceptacion_1_un_isbn_con_dos_ejemplares(self) -> None:
        self.catalogo.registrar_libro(
            isbn="978-0306406157",
            titulo="El nombre del viento",
            autor="Patrick Rothfuss",
            categoria="Novela",
            ejemplares=2,
        )

        consultado = self.catalogo.consultar_disponibilidad("978-0306406157")

        self.assertEqual(len(self.repositorio.listar()), 1)
        self.assertEqual(consultado.isbn, "978-0306406157")
        self.assertEqual(consultado.ejemplares_totales, 2)
        self.assertEqual(consultado.ejemplares_disponibles, 2)


if __name__ == "__main__":
    unittest.main()
