import unittest
import os
import sqlite3
from models.sistema import SistemaAcademico
from database_setup import crear_tablas

class TestSistemaAcademico(unittest.TestCase):
    def setUp(self):
        # Crear base de datos temporal en memoria o archivo temporal
        self.db_path = "test_academico.db"
        
        # Limpiar si existe de una corrida fallida anterior
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        crear_tablas(conn, cursor)
        conn.close()
        
        self.sistema = SistemaAcademico(self.db_path)

    def tearDown(self):
        # Eliminar BD de pruebas
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_registro_calificacion_invalida(self):
        # Primero necesitamos crear un estudiante y una asignatura
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT INTO estudiantes (id, nombre, correo) VALUES ('E001', 'Test', 't@t.com')")
        conn.execute("INSERT INTO profesores (id, nombre, correo) VALUES ('P001', 'Prof', 'p@t.com')")
        conn.execute("INSERT INTO asignaturas (codigo, nombre, creditos, profesor_id) VALUES ('A001', 'Asig', 3, 'P001')")
        conn.commit()
        conn.close()

        # Intentar registrar nota inválida
        resultado = self.sistema.registrar_calificacion('E001', 'A001', 6.0, 'Corte 1')
        self.assertEqual(resultado, "Error: La nota debe estar entre 0.0 y 5.0")

        resultado2 = self.sistema.registrar_calificacion('E001', 'A001', -1.0, 'Corte 1')
        self.assertEqual(resultado2, "Error: La nota debe estar entre 0.0 y 5.0")

        # Intentar registrar nota válida
        resultado3 = self.sistema.registrar_calificacion('E001', 'A001', 4.5, 'Corte 1')
        self.assertIn("exito", resultado3.lower())

if __name__ == '__main__':
    unittest.main()
