class Asignatura:
    """
    Representa una asignatura/materia del programa académico.
    El atributo 'profesor' debe recibir un objeto de tipo Profesor.
    """

    def __init__(self, codigo, nombre, creditos, profesor=None):
        self.codigo = codigo
        self.nombre = nombre
        self.creditos = creditos
        self.profesor = profesor  # Objeto Profesor (o None si no tiene asignado)

    def mostrar_info(self):
        nombre_prof = self.profesor.nombre if self.profesor else "Sin asignar"
        return f"[{self.codigo}] {self.nombre} - Profesor: {nombre_prof}"

    def __str__(self):
        return self.mostrar_info()

    def __repr__(self):
        return (
            f"Asignatura('{self.codigo}', '{self.nombre}', "
            f"{self.creditos}, {self.profesor!r})"
        )
