"""Strategy. El servicio pide días y cupo; no distingue el tipo de usuario."""

from abc import ABC, abstractmethod

from sigeb.dominio.errores import DatosInvalidos


class PoliticaPrestamo(ABC):
    @abstractmethod
    def dias_permitidos(self) -> int:
        """Días entre la fecha de inicio y la fecha límite."""

    @abstractmethod
    def maximo_activos(self) -> int:
        """Cantidad máxima de préstamos sin devolver."""


class PoliticaEstudiante(PoliticaPrestamo):
    def dias_permitidos(self) -> int:
        return 7

    def maximo_activos(self) -> int:
        return 3


class PoliticaDocente(PoliticaPrestamo):
    def dias_permitidos(self) -> int:
        return 15

    def maximo_activos(self) -> int:
        return 5


class PoliticaAdministrativo(PoliticaPrestamo):
    def dias_permitidos(self) -> int:
        return 10

    def maximo_activos(self) -> int:
        return 3


_POLITICAS: dict[str, type[PoliticaPrestamo]] = {
    "estudiante": PoliticaEstudiante,
    "docente": PoliticaDocente,
    "administrativo": PoliticaAdministrativo,
}


def politica_para(tipo: str) -> PoliticaPrestamo:
    """Elige la política del tipo. Una política nueva se registra en este mapa."""
    if not isinstance(tipo, str):
        raise DatosInvalidos("No hay política de préstamo para ese tipo de usuario.")
    clase = _POLITICAS.get(tipo.strip().lower())
    if clase is None:
        raise DatosInvalidos("No hay política de préstamo para ese tipo de usuario.")
    return clase()
