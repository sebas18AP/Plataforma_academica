class Estudiante:
    def __init__(self, identificacion, nombre, correo):
        self.identificacion = identificacion
        self.nombre = nombre
        self.correo = correo
    
    def mostrar_info(self):
        return f"Estudiante: {self.nombre} - ID: {self.identificacion}" 