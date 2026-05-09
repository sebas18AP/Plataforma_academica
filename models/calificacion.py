class Calificacion:
    def __init__(self, estudiante_id, codigo_asignatura, nota_obtenida, corte):
        self.estudiante_id = estudiante_id
        self.codigo_asignatura = codigo_asignatura
        self.nota_obtenida = nota_obtenida
        self.corte = corte # Ejemplo: "Corte 1", "Parcial"

    def es_aprobada(self):
        return self.nota_obtenida >= 3.0  