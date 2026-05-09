class Asignatura:
    def __init__(self, codigo, nombre, creditos, profesor=""):
        self.codigo = codigo
        self.nombre = nombre
        self.creditos = creditos
        self.profesor = profesor

    def mostrar_info(self):
        return f"[{self.codigo}] {self.nombre} - Profesor: {self.profesor}"
        