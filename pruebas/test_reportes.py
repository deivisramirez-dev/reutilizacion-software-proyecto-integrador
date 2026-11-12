"""Aceptación 12: el Builder arma un reporte sin exigir todas las secciones."""

import unittest
from datetime import date

from sigeb.aplicacion.catalogo import ServicioCatalogo
from sigeb.aplicacion.prestamos import ServicioPrestamos
from sigeb.aplicacion.reportes import ServicioReportes
from sigeb.aplicacion.usuarios import ServicioUsuarios
from sigeb.infraestructura.repositorio_libros import RepositorioLibros
from sigeb.infraestructura.repositorio_prestamos import RepositorioPrestamos
from sigeb.infraestructura.repositorio_usuarios import RepositorioUsuarios
from sigeb.reportes.constructor_reporte import ConstructorReporte


class TestReportes(unittest.TestCase):
    def test_aceptacion_12_builder_secciones_opcionales(self) -> None:
        vacio = ConstructorReporte().construir()
        self.assertIsNone(vacio.titulo)
        self.assertIsNone(vacio.resumen)
        self.assertIsNone(vacio.detalle)
        self.assertIsNone(vacio.pie)
        self.assertEqual(vacio.texto(), "")

        solo_titulo = ConstructorReporte().con_titulo("Inventario").construir()
        self.assertEqual(solo_titulo.titulo, "Inventario")
        self.assertIsNone(solo_titulo.resumen)
        self.assertIsNone(solo_titulo.detalle)
        self.assertIsNone(solo_titulo.pie)
        self.assertNotIn("Resumen", solo_titulo.texto())
        self.assertNotIn("Detalle", solo_titulo.texto())
        self.assertNotIn("Pie", solo_titulo.texto())

        completo = (
            ConstructorReporte()
            .con_titulo("Inventario")
            .con_resumen("2 libros")
            .con_detalle(["978-1 | Clean Code", "978-2 | DDD"])
            .con_pie("Fin del reporte")
            .construir()
        )
        texto = completo.texto()
        self.assertEqual(completo.resumen, "2 libros")
        self.assertEqual(completo.detalle, ("978-1 | Clean Code", "978-2 | DDD"))
        self.assertIn("Inventario", texto)
        self.assertIn("2 libros", texto)
        self.assertIn("978-2 | DDD", texto)
        self.assertIn("Fin del reporte", texto)

    def test_el_reporte_del_servicio_incluye_solo_las_secciones_pedidas(self) -> None:
        libros = RepositorioLibros()
        usuarios = RepositorioUsuarios()
        prestamos = RepositorioPrestamos()
        catalogo = ServicioCatalogo(libros)
        servicio_usuarios = ServicioUsuarios(usuarios)
        servicio_prestamos = ServicioPrestamos(prestamos, libros, usuarios)
        catalogo.registrar_libro(
            "978-1", "Clean Code", "Robert Martin", "Software", 2
        )
        reportes = ServicioReportes(catalogo, servicio_usuarios, servicio_prestamos)

        reporte = reportes.generar(
            "Catálogo del día",
            incluir_resumen=False,
            incluir_detalle=True,
            incluir_pie=False,
            hoy=date(2026, 11, 11),
        )

        self.assertEqual(reporte.titulo, "Catálogo del día")
        self.assertIsNone(reporte.resumen)
        self.assertIsNone(reporte.pie)
        self.assertIn("978-1 | Clean Code | Robert Martin | Software | 2/2", reporte.texto())
        self.assertNotIn("Resumen", reporte.texto())
        self.assertNotIn("Pie", reporte.texto())


if __name__ == "__main__":
    unittest.main()
