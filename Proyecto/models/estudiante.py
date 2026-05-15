from models.persona import Persona


class Estudiante(Persona):
    """
    Representa a un estudiante de la plataforma académica.
    Hereda de Persona e incluye una lista de matrículas asociadas.
    """

    def __init__(self, identificacion, nombre, correo):
        super().__init__(identificacion, nombre, correo)
        self.matriculas = []  # Lista de objetos Matricula

    def agregar_matricula(self, matricula):
        """Asocia una matrícula al estudiante."""
        self.matriculas.append(matricula)

    def __str__(self):
        return f"Estudiante: {self.nombre} - ID: {self.identificacion}"

    def __repr__(self):
        return (
            f"Estudiante('{self.identificacion}', '{self.nombre}', "
            f"'{self.correo}')"
        )