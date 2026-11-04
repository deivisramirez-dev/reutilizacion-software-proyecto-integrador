"""Usuarios en memoria, indexados por id."""

from sigeb.dominio.usuario import Usuario


class RepositorioUsuarios:
    def __init__(self) -> None:
        self._usuarios: dict[str, Usuario] = {}

    def guardar(self, usuario: Usuario) -> None:
        self._usuarios[usuario.id_usuario] = usuario

    def obtener(self, id_usuario: str) -> Usuario | None:
        return self._usuarios.get(id_usuario)

    def existe(self, id_usuario: str) -> bool:
        return id_usuario in self._usuarios

    def listar(self) -> list[Usuario]:
        return [self._usuarios[clave] for clave in sorted(self._usuarios)]
