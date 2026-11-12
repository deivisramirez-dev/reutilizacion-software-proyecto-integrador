"""Builder. Cada sección es opcional y el armado termina en `construir()`."""

from sigeb.dominio.errores import DatosInvalidos
from sigeb.reportes.reporte import Reporte


class ConstructorReporte:
    def __init__(self) -> None:
        self._titulo: str | None = None
        self._resumen: str | None = None
        self._detalle: tuple[str, ...] | None = None
        self._pie: str | None = None

    def con_titulo(self, titulo: str) -> "ConstructorReporte":
        self._titulo = _texto(titulo, "El título")
        return self

    def con_resumen(self, resumen: str) -> "ConstructorReporte":
        self._resumen = _texto(resumen, "El resumen")
        return self

    def con_detalle(self, lineas: list[str]) -> "ConstructorReporte":
        if isinstance(lineas, str) or not isinstance(lineas, list) or not lineas:
            raise DatosInvalidos("El detalle debe incluir al menos una línea.")
        limpias: list[str] = []
        for linea in lineas:
            limpias.append(_texto(linea, "Cada línea del detalle"))
        self._detalle = tuple(limpias)
        return self

    def con_pie(self, pie: str) -> "ConstructorReporte":
        self._pie = _texto(pie, "El pie")
        return self

    def construir(self) -> Reporte:
        return Reporte(self._titulo, self._resumen, self._detalle, self._pie)


def _texto(valor: str, nombre: str) -> str:
    if not isinstance(valor, str) or not valor.strip():
        raise DatosInvalidos(f"{nombre} debe ser texto.")
    return valor.strip()
