"""Pruebas de aceptación 2 a 6: préstamo, devolución, usuario inactivo y vencimiento."""

import unittest
from datetime import date

from sigeb.aplicacion.catalogo import ServicioCatalogo
from sigeb.aplicacion.prestamos import ServicioPrestamos
from sigeb.aplicacion.usuarios import ServicioUsuarios
from sigeb.dominio.errores import PrestamoYaDevuelto, SinDisponibilidad, UsuarioInactivo
from sigeb.infraestructura.repositorio_libros import RepositorioLibros
from sigeb.infraestructura.repositorio_prestamos import RepositorioPrestamos
from sigeb.infraestructura.repositorio_usuarios import RepositorioUsuarios

HOY = date(2026, 11, 4)
ISBN = "978-0306406157"
USUARIO = "U-100"


class TestAceptacionPrestamos(unittest.TestCase):
    def setUp(self) -> None:
        self.libros = RepositorioLibros()
        self.usuarios = RepositorioUsuarios()
        self.prestamos_repo = RepositorioPrestamos()
        self.catalogo = ServicioCatalogo(self.libros)
        self.servicio_usuarios = ServicioUsuarios(self.usuarios)
        self.prestamos = ServicioPrestamos(
            self.prestamos_repo, self.libros, self.usuarios
        )

    def test_aceptacion_2_sin_disponibilidad_no_modifica_repositorios(self) -> None:
        self._registrar_libro(ejemplares=0)
        self._registrar_usuario()

        with self.assertRaises(SinDisponibilidad):
            self.prestamos.prestar(ISBN, USUARIO, HOY)

        libro = self.libros.obtener(ISBN)
        assert libro is not None
        self.assertEqual(libro.ejemplares_totales, 0)
        self.assertEqual(libro.ejemplares_disponibles, 0)
        self.assertEqual(self.prestamos_repo.listar(), [])
        self.assertEqual(len(self.usuarios.listar()), 1)

    def test_aceptacion_3_prestar_descuenta_y_fija_limite(self) -> None:
        self._registrar_libro(ejemplares=2)
        self._registrar_usuario()

        prestamo = self.prestamos.prestar(ISBN, USUARIO, HOY)

        libro = self.libros.obtener(ISBN)
        assert libro is not None
        self.assertEqual(libro.ejemplares_disponibles, 1)
        self.assertEqual(libro.ejemplares_totales, 2)
        self.assertEqual(prestamo.fecha_inicio, HOY)
        self.assertEqual(prestamo.fecha_limite, date(2026, 11, 11))
        self.assertIsNone(prestamo.fecha_devolucion)
        self.assertEqual(self.prestamos_repo.listar(), [prestamo])

    def test_aceptacion_4_segunda_devolucion_no_incrementa_inventario(self) -> None:
        self._registrar_libro(ejemplares=1)
        self._registrar_usuario()
        prestamo = self.prestamos.prestar(ISBN, USUARIO, HOY)
        devuelto = self.prestamos.devolver(prestamo.id_prestamo, HOY)
        libro = self.libros.obtener(ISBN)
        assert libro is not None
        disponibles = libro.ejemplares_disponibles

        with self.assertRaises(PrestamoYaDevuelto):
            self.prestamos.devolver(prestamo.id_prestamo, HOY)

        self.assertEqual(libro.ejemplares_disponibles, disponibles)
        self.assertEqual(libro.ejemplares_totales, 1)
        self.assertEqual(devuelto.fecha_devolucion, HOY)

    def test_aceptacion_5_usuario_inactivo_no_puede_prestar(self) -> None:
        self._registrar_libro(ejemplares=1)
        self._registrar_usuario(activo=False)

        with self.assertRaises(UsuarioInactivo):
            self.prestamos.prestar(ISBN, USUARIO, HOY)

        libro = self.libros.obtener(ISBN)
        assert libro is not None
        self.assertEqual(libro.ejemplares_disponibles, 1)
        self.assertEqual(self.prestamos_repo.listar(), [])

    def test_aceptacion_6_prestamo_activo_con_limite_anterior_esta_vencido(self) -> None:
        self._registrar_libro(ejemplares=1)
        self._registrar_usuario()
        inicio = date(2026, 11, 1)
        prestamo = self.prestamos.prestar(ISBN, USUARIO, inicio)
        consulta = date(2026, 11, 9)

        vencidos = self.prestamos.consultar("vencido", consulta)

        self.assertEqual(prestamo.fecha_limite, date(2026, 11, 8))
        self.assertTrue(prestamo.esta_vencido(consulta))
        self.assertEqual(vencidos, [prestamo])
        self.assertEqual(self.prestamos.consultar("activo", consulta), [])
        self.assertEqual(self.prestamos.consultar("vencido", prestamo.fecha_limite), [])
        self.assertEqual(self.prestamos.consultar("activo", prestamo.fecha_limite), [prestamo])

    def _registrar_libro(self, ejemplares: int) -> None:
        self.catalogo.registrar_libro(
            ISBN,
            "El nombre del viento",
            "Patrick Rothfuss",
            "Novela",
            ejemplares,
        )

    def _registrar_usuario(self, activo: bool = True) -> None:
        self.servicio_usuarios.registrar_usuario(
            USUARIO, "Ana Pérez", "estudiante", activo
        )


if __name__ == "__main__":
    unittest.main()
