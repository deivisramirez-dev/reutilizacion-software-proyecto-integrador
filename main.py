"""Punto de entrada de SIGEB. Arma repositorios, servicios y menú."""

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
from sigeb.notificaciones.eventos import CentroEventos, ObservadorNotificacion
from sigeb.presentacion.menu import MenuConsola


def construir_menu() -> MenuConsola:
    libros = RepositorioLibros()
    usuarios = RepositorioUsuarios()
    prestamos = RepositorioPrestamos()
    catalogo = ServicioCatalogo(libros)
    servicio_usuarios = ServicioUsuarios(usuarios)
    notificaciones = ServicioNotificaciones(ProveedorSMSSimulado())
    eventos = CentroEventos()
    eventos.suscribir(
        ObservadorNotificacion(lambda mensaje: notificaciones.enviar("consola", mensaje))
    )
    servicio_prestamos = ServicioPrestamos(prestamos, libros, usuarios, eventos)
    fachada = BibliotecaFacade(
        catalogo,
        servicio_usuarios,
        servicio_prestamos,
        notificaciones,
        ServicioReportes(catalogo, servicio_usuarios, servicio_prestamos),
    )
    return MenuConsola(fachada)


def main() -> None:
    construir_menu().ejecutar()


if __name__ == "__main__":
    main()
