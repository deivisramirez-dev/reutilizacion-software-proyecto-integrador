"""Casos de uso de usuarios (RF-06 y RF-07)."""

from sigeb.dominio.errores import DatosInvalidos, UsuarioDuplicado, UsuarioNoEncontrado
from sigeb.dominio.usuario import Usuario
from sigeb.infraestructura.repositorio_usuarios import RepositorioUsuarios


class ServicioUsuarios:
    def __init__(self, usuarios: RepositorioUsuarios) -> None:
        self._usuarios = usuarios

    def registrar_usuario(
        self,
        id_usuario: str,
        nombre: str,
        tipo: str,
        activo: bool = True,
    ) -> Usuario:
        if not isinstance(id_usuario, str) or not id_usuario.strip():
            raise DatosInvalidos("El id de usuario no puede estar vacío.")
        id_limpio = id_usuario.strip()
        if self._usuarios.existe(id_limpio):
            raise UsuarioDuplicado(id_limpio)
        usuario = Usuario(
            id_usuario=id_limpio,
            nombre=nombre,
            tipo=tipo,
            activo=activo,
        )
        self._usuarios.guardar(usuario)
        return usuario

    def listar(self) -> list[Usuario]:
        return self._usuarios.listar()

    def obtener(self, id_usuario: str) -> Usuario:
        if not isinstance(id_usuario, str) or not id_usuario.strip():
            raise DatosInvalidos("El id de usuario no puede estar vacío.")
        usuario = self._usuarios.obtener(id_usuario.strip())
        if usuario is None:
            raise UsuarioNoEncontrado(id_usuario.strip())
        return usuario
