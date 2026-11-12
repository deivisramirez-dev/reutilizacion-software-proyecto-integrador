"""Aceptación 7 y 8: Factory Method entrega el canal y el Adapter traduce el SMS."""

import unittest
from datetime import date

from sigeb.aplicacion.catalogo import ServicioCatalogo
from sigeb.aplicacion.notificaciones import ServicioNotificaciones
from sigeb.aplicacion.prestamos import ServicioPrestamos
from sigeb.aplicacion.usuarios import ServicioUsuarios
from sigeb.dominio.errores import ErrorNotificacion
from sigeb.infraestructura.proveedor_sms_simulado import (
    ErrorProveedorSMS,
    ProveedorSMSSimulado,
)
from sigeb.infraestructura.repositorio_libros import RepositorioLibros
from sigeb.infraestructura.repositorio_prestamos import RepositorioPrestamos
from sigeb.infraestructura.repositorio_usuarios import RepositorioUsuarios
from sigeb.notificaciones.adaptador_sms import AdaptadorSMS
from sigeb.notificaciones.canales import NotificacionConsola, NotificacionCorreo
from sigeb.notificaciones.fabrica import (
    FabricaConsola,
    FabricaCorreo,
    FabricaNotificacion,
    FabricaSMS,
)


def consumir(fabrica: FabricaNotificacion, mensaje: str) -> None:
    """El mismo consumidor sirve para cualquier canal: no pregunta el tipo."""
    fabrica.crear().enviar(mensaje)


class TestNotificaciones(unittest.TestCase):
    def test_aceptacion_7_factory_method_devuelve_el_canal_pedido(self) -> None:
        consola: list[str] = []
        buzon: list[tuple[str, str]] = []
        proveedor = ProveedorSMSSimulado()
        pedido = {
            "consola": (FabricaConsola(consola.append), NotificacionConsola),
            "correo": (FabricaCorreo("ana@ejemplo.edu", buzon), NotificacionCorreo),
            "sms": (FabricaSMS(proveedor, "3001112233"), AdaptadorSMS),
        }

        for nombre, (fabrica, tipo) in pedido.items():
            self.assertIsInstance(fabrica.crear(), tipo)
            consumir(fabrica, f"aviso {nombre}")

        self.assertEqual(consola, ["aviso consola"])
        self.assertEqual(buzon, [("ana@ejemplo.edu", "aviso correo")])
        self.assertEqual(proveedor.enviados[0]["numero_destino"], "3001112233")
        self.assertEqual(proveedor.enviados[0]["cuerpo"], "aviso sms")

    def test_aceptacion_8_adaptador_traduce_enviar_a_la_api_del_proveedor(self) -> None:
        proveedor = ProveedorSMSSimulado()
        adaptador = AdaptadorSMS(proveedor, "3001112233")

        adaptador.enviar("Préstamo registrado")

        self.assertEqual(len(proveedor.enviados), 1)
        envio = proveedor.enviados[0]
        self.assertEqual(envio["numero_destino"], "3001112233")
        self.assertEqual(envio["cuerpo"], "Préstamo registrado")
        self.assertEqual(envio["referencia"], "SMS-0001")

    def test_fallo_de_sms_no_revierte_un_prestamo_confirmado(self) -> None:
        libros = RepositorioLibros()
        usuarios = RepositorioUsuarios()
        prestamos_repo = RepositorioPrestamos()
        catalogo = ServicioCatalogo(libros)
        servicio_usuarios = ServicioUsuarios(usuarios)
        prestamos = ServicioPrestamos(prestamos_repo, libros, usuarios)
        catalogo.registrar_libro("978-1", "Clean Code", "Martin", "Software", 1)
        servicio_usuarios.registrar_usuario("U1", "Ana", "estudiante", True)
        prestamo = prestamos.prestar("978-1", "U1", date(2026, 11, 11))
        libro = libros.obtener("978-1")
        assert libro is not None
        disponibles = libro.ejemplares_disponibles

        class ProveedorRoto:
            def despachar(self, numero_destino: str, cuerpo: str) -> str:
                raise ErrorProveedorSMS("sin señal")

        servicio = ServicioNotificaciones(ProveedorRoto())
        with self.assertRaises(ErrorNotificacion):
            servicio.enviar("sms", "Aviso de préstamo", "3001112233")

        self.assertEqual(libro.ejemplares_disponibles, disponibles)
        self.assertIsNone(prestamo.fecha_devolucion)
        self.assertEqual(prestamos_repo.listar(), [prestamo])


if __name__ == "__main__":
    unittest.main()
