from models.persona import Persona


class Profesor(Persona):
    """
    Representa a un profesor de la plataforma académica.
    Hereda de Persona e incluye el departamento al que pertenece.
    """

    def __init__(self, identificacion, nombre, correo, departamento=""):
        super().__init__(identificacion, nombre, correo)
        self.departamento = departamento

    def __str__(self):
        dep = f" - {self.departamento}" if self.departamento else ""
        return f"Prof. {self.nombre}{dep}"

    def __repr__(self):
        return (
            f"Profesor('{self.identificacion}', '{self.nombre}', "
            f"'{self.correo}', '{self.departamento}')"
        )
