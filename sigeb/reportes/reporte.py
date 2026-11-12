"""Reporte ya construido. Las secciones ausentes quedan en None."""


class Reporte:
    def __init__(
        self,
        titulo: str | None,
        resumen: str | None,
        detalle: tuple[str, ...] | None,
        pie: str | None,
    ) -> None:
        self.titulo = titulo
        self.resumen = resumen
        self.detalle = detalle
        self.pie = pie

    def texto(self) -> str:
        bloques: list[str] = []
        if self.titulo is not None:
            bloques.append(self.titulo)
        if self.resumen is not None:
            bloques.append(f"Resumen\n{self.resumen}")
        if self.detalle is not None:
            bloques.append("Detalle\n" + "\n".join(self.detalle))
        if self.pie is not None:
            bloques.append(f"Pie\n{self.pie}")
        return "\n\n".join(bloques)
