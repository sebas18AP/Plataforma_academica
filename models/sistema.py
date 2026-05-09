class SistemaAcademico:
    def __init__(self):
        # Aquí guardamos los datos temporalmente mientras el programa está abierto
        self.estudiantes = []
        self.asignaturas = []
        self.matriculas = []
        self.calificaciones = []

    def registrar_estudiante(self, estudiante):
        self.estudiantes.append(estudiante)
        return f"Estudiante {estudiante.nombre} registrado con éxito."

    # Aquí es donde tú brillas con las estadísticas que pide el profesor
    def calcular_promedio_estudiante(self, identificacion):
        # Filtramos solo las calificaciones que le pertenecen a este estudiante
        notas = [c.nota_obtenida for c in self.calificaciones if c.estudiante_id == identificacion]
        
        if not notas:
            return 0.0 # Si no tiene notas, su promedio es 0
            
        promedio = sum(notas) / len(notas)
        return round(promedio, 2) 