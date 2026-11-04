"""Usuario que puede tomar libros en préstamo."""

from sigeb.dominio.errores import DatosInvalidos

TIPOS_USUARIO = ("estudiante", "docente", "administrativo")


class Usuario:
    def __init__(self, id_usuario: str, nombre: str, tipo: str, activo: bool) -> None:
        self.id_usuario = _texto(id_usuario, "El id de usuario")
        self.nombre = _texto(nombre, "El nombre")
        self.tipo = _tipo(tipo)
        if type(activo) is not bool:
            raise DatosInvalidos("El estado activo debe ser verdadero o falso.")
        self.activo = activo


def _texto(valor: str, nombre: str) -> str:
    if not isinstance(valor, str):
        raise DatosInvalidos(f"{nombre} debe ser texto.")
    limpio = valor.strip()
    if not limpio:
        raise DatosInvalidos(f"{nombre} no puede estar vacío.")
    return limpio


def _tipo(valor: str) -> str:
    if not isinstance(valor, str):
        raise DatosInvalidos("El tipo de usuario debe ser texto.")
    tipo = valor.strip().lower()
    if tipo not in TIPOS_USUARIO:
        opciones = ", ".join(TIPOS_USUARIO)
        raise DatosInvalidos(f"El tipo de usuario debe ser uno de: {opciones}.")
    return tipo
