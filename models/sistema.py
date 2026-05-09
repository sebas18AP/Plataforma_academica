class SistemaAcademico:
  
   def __init__(self):
        # Aquí se guardan los datos temporalmente mientras el programa está abierto
        self.estudiantes = []
        self.asignaturas = []
        self.matriculas = []
        self.calificaciones = []
        
        #  Sistema  de usuarios (Usuario: {contraseña, rol})
        self.usuarios_registrados = {
            "profesor_johan": {"password": "admin123", "rol": "profesor"},
            "estudiante_01": {"password": "pass", "rol": "estudiante"}
        }

    # : Función para que la GUI valide el Login
    def iniciar_sesion(self, usuario, password):
        if usuario in self.usuarios_registrados:
            if self.usuarios_registrados[usuario]["password"] == password:
                return self.usuarios_registrados[usuario]["rol"]
        return None

    def registrar_estudiante(self, estudiante):
        self.estudiantes.append(estudiante)
        return f"Estudiante {estudiante.nombre} registrado con éxito."

    # Estadisticas 
    def calcular_promedio_estudiante(self, identificacion):
        # Filtramos solo las calificaciones que le pertenecen a este estudiante
        notas = [c.nota_obtenida for c in self.calificaciones if c.estudiante_id == identificacion]
        
        if not notas:
            return 0.0 # Si no tiene notas, su promedio es 0
            
        promedio = sum(notas) / len(notas)
        return round(promedio, 2)

        def calcular_promedio_asignatura(self, codigo_asignatura):
        # aca se filtran las notas de una materia específica
        notas = [c.nota_obtenida for c in self.calificaciones if c.codigo_asignatura == codigo_asignatura]
        
        if not notas:
            return 0.0 # Si nadie tiene notas en esa materia, es 0
            
        promedio = sum(notas) / len(notas)
        return round(promedio, 2)

    def obtener_distribucion_notas(self):
        # se cuentan cunatos pasaron y cuantos perdieron.
        # Suponiendo que se aprueba con 3.0
        aprobados = len([c for c in self.calificaciones if c.nota_obtenida >= 3.0])
        reprobados = len([c for c in self.calificaciones if c.nota_obtenida < 3.0])
        
        return {
            "Aprobados": aprobados,
            "Reprobados": reprobados,
            "Total_Calificaciones": len(self.calificaciones)
        }

    
    #  Requerimiento de Consultas y búsquedas avanzadas
    def buscar_estudiante(self, identificacion):
        # Se recorre la lista de estudiantes para buscar coincidencias
        for estudiante in self.estudiantes:
            if estudiante.identificacion == identificacion:
                return estudiante # Si lo encuentra, devuelve todos los datos del estudiante
                
        return None # Si se termina de buscar y se encuentra devuelve None
            
    

 

