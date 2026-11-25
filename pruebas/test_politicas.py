"""Aceptación 11: Strategy asigna plazo y cupo según el tipo de usuario."""

import unittest
from datetime import date, timedelta

from sigeb.aplicacion.catalogo import ServicioCatalogo
from sigeb.aplicacion.prestamos import ServicioPrestamos
from sigeb.aplicacion.usuarios import ServicioUsuarios
from sigeb.dominio.errores import CupoAgotado
from sigeb.dominio.politicas import politica_para
from sigeb.infraestructura.repositorio_libros import RepositorioLibros
from sigeb.infraestructura.repositorio_prestamos import RepositorioPrestamos
from sigeb.infraestructura.repositorio_usuarios import RepositorioUsuarios

HOY = date(2026, 11, 25)
ISBN = "978-1"


class TestPoliticas(unittest.TestCase):
    def test_aceptacion_11_plazo_y_cupo_segun_tipo(self) -> None:
        esperado = {
            "estudiante": (7, 3),
            "docente": (15, 5),
            "administrativo": (10, 3),
        }
        for tipo, (dias, cupo) in esperado.items():
            politica = politica_para(tipo)
            self.assertEqual(politica.dias_permitidos(), dias)
            self.assertEqual(politica.maximo_activos(), cupo)
            prestamo = self._prestar(tipo, ejemplares=cupo + 1, veces=1)
            self.assertEqual(prestamo.fecha_limite, HOY + timedelta(days=dias))

        self._exige_cupo("estudiante", 3)
        self._exige_cupo("docente", 5)
        self._exige_cupo("administrativo", 3)

    def _exige_cupo(self, tipo: str, cupo: int) -> None:
        libros, prestamos = self._servicios(tipo, ejemplares=cupo + 1)
        for _ in range(cupo):
            prestamos.prestar(ISBN, "U1", HOY)
        disponibles = libros.obtener(ISBN).ejemplares_disponibles
        with self.assertRaises(CupoAgotado):
            prestamos.prestar(ISBN, "U1", HOY)
        self.assertEqual(libros.obtener(ISBN).ejemplares_disponibles, disponibles)
        self.assertEqual(len(prestamos.historial("U1")), cupo)

    def _prestar(self, tipo: str, ejemplares: int, veces: int):
        _libros, prestamos = self._servicios(tipo, ejemplares)
        prestamo = None
        for _ in range(veces):
            prestamo = prestamos.prestar(ISBN, "U1", HOY)
        return prestamo

    def _servicios(self, tipo: str, ejemplares: int):
        libros = RepositorioLibros()
        usuarios = RepositorioUsuarios()
        repo = RepositorioPrestamos()
        catalogo = ServicioCatalogo(libros)
        servicio_usuarios = ServicioUsuarios(usuarios)
        catalogo.registrar_libro(ISBN, "Clean Code", "Martin", "Software", ejemplares)
        servicio_usuarios.registrar_usuario("U1", "Ana", tipo, True)
        return libros, ServicioPrestamos(repo, libros, usuarios)


if __name__ == "__main__":
    unittest.main()
