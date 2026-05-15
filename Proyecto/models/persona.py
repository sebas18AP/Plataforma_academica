class Persona:
    """
    Clase base para Estudiante y Profesor.
    Contiene los atributos comunes: identificación, nombre y correo.
    """

    def __init__(self, identificacion, nombre, correo):
        self.identificacion = identificacion
        self.nombre = nombre
        self.correo = correo

    def __str__(self):
        return f"{self.nombre} (ID: {self.identificacion})"

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.identificacion}', '{self.nombre}', '{self.correo}')"
