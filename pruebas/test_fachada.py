"""Aceptación 9: el menú presta a través de la fachada y no conoce los repositorios."""

import inspect
import unittest
from datetime import date

from sigeb.aplicacion.catalogo import ServicioCatalogo
from sigeb.aplicacion.fachada_biblioteca import BibliotecaFacade
from sigeb.aplicacion.notificaciones import ServicioNotificaciones
from sigeb.aplicacion.prestamos import ServicioPrestamos
from sigeb.aplicacion.reportes import ServicioReportes
from sigeb.aplicacion.usuarios import ServicioUsuarios
from sigeb.infraestructura.proveedor_sms_simulado import ProveedorSMSSimulado
from sigeb.infraestructura.repositorio_libros import RepositorioLibros
from sigeb.infraestructura.repositorio_prestamos import RepositorioPrestamos
from sigeb.infraestructura.repositorio_usuarios import RepositorioUsuarios
from sigeb.presentacion import menu as modulo_menu
from sigeb.presentacion.menu import MenuConsola

HOY = date(2026, 11, 18)
ISBN = "978-0306406157"
USUARIO = "U-100"


class TestFachada(unittest.TestCase):
    def test_aceptacion_9_el_menu_presta_sin_conocer_repositorios(self) -> None:
        fuente = inspect.getsource(modulo_menu)
        self.assertNotIn("repositorio", fuente.lower())
        self.assertNotIn("infraestructura", fuente)
        self.assertNotIn("ServicioPrestamos", fuente)
        self.assertNotIn("ServicioCatalogo", fuente)

        libros = RepositorioLibros()
        usuarios = RepositorioUsuarios()
        prestamos = RepositorioPrestamos()
        catalogo = ServicioCatalogo(libros)
        servicio_usuarios = ServicioUsuarios(usuarios)
        servicio_prestamos = ServicioPrestamos(prestamos, libros, usuarios)
        fachada = BibliotecaFacade(
            catalogo,
            servicio_usuarios,
            servicio_prestamos,
            ServicioNotificaciones(ProveedorSMSSimulado()),
            ServicioReportes(catalogo, servicio_usuarios, servicio_prestamos),
        )
        catalogo.registrar_libro(ISBN, "El nombre del viento", "Rothfuss", "Novela", 1)
        servicio_usuarios.registrar_usuario(USUARIO, "Ana Pérez", "estudiante", True)
        entradas = iter(["9", ISBN, USUARIO, "", "0"])
        menu = MenuConsola(
            fachada,
            entrada=lambda _etiqueta: next(entradas),
            salida=lambda _mensaje: None,
            hoy=lambda: HOY,
        )
        menu.ejecutar()

        libro = libros.obtener(ISBN)
        assert libro is not None
        prestamo = prestamos.listar()[0]
        self.assertEqual(libro.ejemplares_disponibles, 0)
        self.assertEqual(prestamo.isbn_libro, ISBN)
        self.assertEqual(prestamo.id_usuario, USUARIO)
        self.assertEqual(prestamo.fecha_inicio, HOY)
        self.assertEqual(prestamo.fecha_limite, date(2026, 11, 25))


if __name__ == "__main__":
    unittest.main()
