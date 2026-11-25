"""Aceptación 10: Observer avisa solo a quien está suscrito."""

import unittest
from datetime import date

from sigeb.aplicacion.catalogo import ServicioCatalogo
from sigeb.aplicacion.prestamos import ServicioPrestamos
from sigeb.aplicacion.usuarios import ServicioUsuarios
from sigeb.dominio.errores import ErrorNotificacion
from sigeb.infraestructura.repositorio_libros import RepositorioLibros
from sigeb.infraestructura.repositorio_prestamos import RepositorioPrestamos
from sigeb.infraestructura.repositorio_usuarios import RepositorioUsuarios
from sigeb.notificaciones.eventos import CentroEventos, Evento, Observador, ObservadorNotificacion

HOY = date(2026, 11, 25)
ISBN = "978-1"


class ObservadorEspia(Observador):
    def __init__(self) -> None:
        self.eventos: list[Evento] = []

    def actualizar(self, evento: Evento) -> None:
        self.eventos.append(evento)


class TestEventos(unittest.TestCase):
    def test_aceptacion_10_solo_los_suscriptores_reciben_el_aviso(self) -> None:
        libros, prestamos, eventos = self._servicios()
        suscrito = ObservadorEspia()
        ausente = ObservadorEspia()
        eventos.suscribir(suscrito)

        prestamo = prestamos.prestar(ISBN, "U1", HOY)
        prestamos.devolver(prestamo.id_prestamo, HOY)

        self.assertEqual([evento.tipo for evento in suscrito.eventos], ["prestamo", "devolucion"])
        self.assertEqual(suscrito.eventos[0].id_prestamo, prestamo.id_prestamo)
        self.assertEqual(ausente.eventos, [])
        self.assertEqual(libros.obtener(ISBN).ejemplares_disponibles, 1)

    def test_un_fallo_al_avisar_no_deshace_el_prestamo(self) -> None:
        libros, prestamos, eventos = self._servicios()

        def enviar_roto(_mensaje: str) -> None:
            raise ErrorNotificacion("sin señal")

        avisos = ObservadorNotificacion(enviar_roto)
        eventos.suscribir(avisos)
        prestamo = prestamos.prestar(ISBN, "U1", HOY)

        self.assertIsNone(prestamo.fecha_devolucion)
        self.assertEqual(libros.obtener(ISBN).ejemplares_disponibles, 0)
        self.assertEqual(avisos.fallos, ["sin señal"])

    def _servicios(self):
        libros = RepositorioLibros()
        usuarios = RepositorioUsuarios()
        repo = RepositorioPrestamos()
        ServicioCatalogo(libros).registrar_libro(ISBN, "Clean Code", "Martin", "Software", 1)
        ServicioUsuarios(usuarios).registrar_usuario("U1", "Ana", "estudiante", True)
        eventos = CentroEventos()
        prestamos = ServicioPrestamos(repo, libros, usuarios, eventos)
        return libros, prestamos, eventos


if __name__ == "__main__":
    unittest.main()
