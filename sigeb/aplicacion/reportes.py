"""Arma un reporte del estado actual con las secciones que se pidan."""

from datetime import date

from sigeb.aplicacion.catalogo import ServicioCatalogo
from sigeb.aplicacion.prestamos import ServicioPrestamos
from sigeb.aplicacion.usuarios import ServicioUsuarios
from sigeb.dominio.errores import DatosInvalidos
from sigeb.reportes.constructor_reporte import ConstructorReporte
from sigeb.reportes.reporte import Reporte


class ServicioReportes:
    def __init__(
        self,
        catalogo: ServicioCatalogo,
        usuarios: ServicioUsuarios,
        prestamos: ServicioPrestamos,
    ) -> None:
        self._catalogo = catalogo
        self._usuarios = usuarios
        self._prestamos = prestamos

    def generar(
        self,
        titulo: str,
        incluir_resumen: bool,
        incluir_detalle: bool,
        incluir_pie: bool,
        hoy: date,
    ) -> Reporte:
        fecha = _fecha(hoy)
        constructor = ConstructorReporte().con_titulo(titulo)
        if _marca(incluir_resumen, "El resumen"):
            constructor.con_resumen(self._resumen(fecha))
        if _marca(incluir_detalle, "El detalle"):
            constructor.con_detalle(self._detalle())
        if _marca(incluir_pie, "El pie"):
            constructor.con_pie(f"Generado el {fecha.isoformat()}. SIGEB.")
        return constructor.construir()

    def _resumen(self, hoy: date) -> str:
        libros = self._catalogo.listar()
        usuarios = self._usuarios.listar()
        activos = self._prestamos.consultar("activo", hoy)
        vencidos = self._prestamos.consultar("vencido", hoy)
        return (
            f"Libros: {len(libros)}. "
            f"Usuarios: {len(usuarios)}. "
            f"Préstamos activos: {len(activos)}. "
            f"Préstamos vencidos: {len(vencidos)}."
        )

    def _detalle(self) -> list[str]:
        lineas = [
            (
                f"{libro.isbn} | {libro.titulo} | {libro.autor} | {libro.categoria} | "
                f"{libro.ejemplares_disponibles}/{libro.ejemplares_totales}"
            )
            for libro in self._catalogo.listar()
        ]
        lineas.extend(
            (
                f"{usuario.id_usuario} | {usuario.nombre} | {usuario.tipo} | "
                f"{'activo' if usuario.activo else 'inactivo'}"
            )
            for usuario in self._usuarios.listar()
        )
        if not lineas:
            return ["Sin libros ni usuarios registrados."]
        return lineas


def _fecha(valor: date) -> date:
    if type(valor) is not date:
        raise DatosInvalidos("La fecha debe ser un día de calendario.")
    return valor


def _marca(valor: bool, nombre: str) -> bool:
    if type(valor) is not bool:
        raise DatosInvalidos(f"{nombre} debe ser verdadero o falso.")
    return valor
