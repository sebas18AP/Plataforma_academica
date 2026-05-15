import sqlite3
from werkzeug.security import generate_password_hash


from models.estudiante import Estudiante
from models.asignatura import Asignatura
from models.calificacion import Calificacion
from models.matricula import Matricula
from models.profesor import Profesor


class SistemaAcademico:
    """
    Clase central del sistema académico.
    Todos los datos se leen y escriben directamente en la base de datos SQLite.
    Ya NO se usan listas en memoria.
    """

    def __init__(self, db_path):
        self.db_path = db_path

    # ================================================================
    #  CONEXIÓN A LA BASE DE DATOS
    # ================================================================

    def _get_connection(self):
        """Abre una conexión a SQLite con acceso por nombre de columna."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    # ================================================================
    #  USUARIOS (Autenticación y Registro)
    # ================================================================

    def registrar_usuario(self, nombre, identificacion, correo, contrasena, rol):
        """
        Registra un usuario en la tabla de credenciales y en su tabla de perfil.
        Usa hashing para la contraseña.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Hashear la contraseña antes de guardar
        hash_password = generate_password_hash(contrasena)
        
        try:
            # 1. Insertar en tabla de autenticación
            cursor.execute(
                "INSERT INTO usuarios (nombre, correo_institucional, contrasena, rol) VALUES (?, ?, ?, ?)",
                (nombre, correo, hash_password, rol)
            )
            
            # 2. Insertar en tabla de perfil según el rol
            if rol == 'Estudiante':
                cursor.execute(
                    "INSERT INTO estudiantes (id, nombre, correo) VALUES (?, ?, ?)",
                    (identificacion, nombre, correo)
                )
            elif rol == 'Profesor':
                cursor.execute(
                    "INSERT INTO profesores (id, nombre, correo) VALUES (?, ?, ?, ?)",
                    (identificacion, nombre, correo, "Departamento por asignar")
                )
            
            conn.commit()
            return True, "Usuario registrado exitosamente"
        except sqlite3.IntegrityError:
            return False, "El correo o la identificación ya están registrados"
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"
        finally:
            conn.close()

    # ================================================================
    #  PROPIEDADES — compatibilidad con reportes.py
    #  (reportes.py usa self.sistema.estudiantes, .calificaciones, etc.)
    # ================================================================

    @property
    def estudiantes(self):
        """Retorna todos los estudiantes desde la BD."""
        return self.obtener_estudiantes()

    @property
    def asignaturas(self):
        """Retorna todas las asignaturas desde la BD."""
        return self.obtener_asignaturas()

    @property
    def calificaciones(self):
        """Retorna todas las calificaciones desde la BD."""
        return self.obtener_calificaciones()

    # ================================================================
    #  ESTUDIANTES
    # ================================================================

    def registrar_estudiante(self, estudiante):
        """Inserta un estudiante en la BD."""
        conn = self._get_connection()
        try:
            conn.execute(
                "INSERT INTO estudiantes (id, nombre, correo) VALUES (?, ?, ?)",
                (estudiante.identificacion, estudiante.nombre, estudiante.correo),
            )
            conn.commit()
            return f"Estudiante {estudiante.nombre} registrado con éxito."
        except sqlite3.IntegrityError:
            return f"El estudiante con ID {estudiante.identificacion} ya existe."
        finally:
            conn.close()

    def obtener_estudiantes(self):
        """Retorna lista de objetos Estudiante desde la BD."""
        conn = self._get_connection()
        filas = conn.execute("SELECT id, nombre, correo FROM estudiantes").fetchall()
        conn.close()
        return [Estudiante(f["id"], f["nombre"], f["correo"]) for f in filas]

    def buscar_estudiante(self, identificacion):
        """Busca un estudiante por ID. Retorna Estudiante o None."""
        conn = self._get_connection()
        fila = conn.execute(
            "SELECT id, nombre, correo FROM estudiantes WHERE id = ?",
            (identificacion,),
        ).fetchone()
        conn.close()
        if fila:
            return Estudiante(fila["id"], fila["nombre"], fila["correo"])
        return None

    # ================================================================
    #  PROFESORES
    # ================================================================

    def obtener_profesores(self):
        """Retorna lista de objetos Profesor desde la BD."""
        conn = self._get_connection()
        filas = conn.execute(
            "SELECT id, nombre, correo, departamento FROM profesores"
        ).fetchall()
        conn.close()
        return [
            Profesor(f["id"], f["nombre"], f["correo"], f["departamento"])
            for f in filas
        ]

    # ================================================================
    #  ASIGNATURAS
    # ================================================================

    def obtener_asignaturas(self):
        """Retorna lista de objetos Asignatura (con su Profesor asociado) desde la BD."""
        conn = self._get_connection()
        filas = conn.execute("""
            SELECT a.codigo, a.nombre, a.creditos,
                   p.id   AS prof_id,   p.nombre AS prof_nombre,
                   p.correo AS prof_correo, p.departamento AS prof_dep
            FROM asignaturas a
            LEFT JOIN profesores p ON a.profesor_id = p.id
        """).fetchall()
        conn.close()

        resultado = []
        for f in filas:
            profesor = None
            if f["prof_id"]:
                profesor = Profesor(
                    f["prof_id"], f["prof_nombre"],
                    f["prof_correo"], f["prof_dep"],
                )
            resultado.append(Asignatura(f["codigo"], f["nombre"], f["creditos"], profesor))
        return resultado

    # ================================================================
    #  CALIFICACIONES
    # ================================================================

    def registrar_calificacion(self, calificacion):
        """Inserta una calificación en la BD."""
        conn = self._get_connection()
        try:
            conn.execute(
                "INSERT INTO calificaciones (estudiante_id, codigo_asignatura, nota, corte) "
                "VALUES (?, ?, ?, ?)",
                (
                    calificacion.estudiante_id,
                    calificacion.codigo_asignatura,
                    calificacion.nota_obtenida,
                    calificacion.corte,
                ),
            )
            conn.commit()
            return "Calificacion registrada con exito."
        except sqlite3.IntegrityError as e:
            return f"Error al registrar calificacion: {e}"
        finally:
            conn.close()

    def obtener_calificaciones(self):
        """Retorna lista de objetos Calificacion desde la BD."""
        conn = self._get_connection()
        filas = conn.execute(
            "SELECT estudiante_id, codigo_asignatura, nota, corte FROM calificaciones"
        ).fetchall()
        conn.close()
        return [
            Calificacion(f["estudiante_id"], f["codigo_asignatura"], f["nota"], f["corte"])
            for f in filas
        ]

    # ================================================================
    #  MATRÍCULAS
    # ================================================================

    def registrar_matricula(self, matricula):
        """Inserta una matricula en la BD."""
        conn = self._get_connection()
        try:
            conn.execute(
                "INSERT INTO matriculas (estudiante_id, codigo_asignatura, periodo) "
                "VALUES (?, ?, ?)",
                (matricula.estudiante_id, matricula.codigo_asignatura, matricula.periodo),
            )
            conn.commit()
            return "Matricula registrada con exito."
        except sqlite3.IntegrityError as e:
            return f"Error al registrar matricula: {e}"
        finally:
            conn.close()

    def matricular_estudiante(self, estudiante_id, codigo_asignatura, periodo):
        """Metodo de conveniencia para matricular un estudiante creando el objeto Matricula."""
        nueva_matricula = Matricula(estudiante_id, codigo_asignatura, periodo)
        return self.registrar_matricula(nueva_matricula)

    def obtener_matriculas(self):
        """Retorna lista de objetos Matricula desde la BD."""
        conn = self._get_connection()
        filas = conn.execute(
            "SELECT estudiante_id, codigo_asignatura, periodo FROM matriculas"
        ).fetchall()
        conn.close()
        return [
            Matricula(f["estudiante_id"], f["codigo_asignatura"], f["periodo"])
            for f in filas
        ]

    # ================================================================
    #  ESTADÍSTICAS (consultas SQL directas, sin cargar todo a RAM)
    # ================================================================

    def calcular_promedio_estudiante(self, identificacion):
        """Calcula el promedio de un estudiante directamente con SQL."""
        conn = self._get_connection()
        fila = conn.execute(
            "SELECT ROUND(AVG(nota), 2) AS promedio FROM calificaciones WHERE estudiante_id = ?",
            (identificacion,),
        ).fetchone()
        conn.close()
        return fila["promedio"] if fila["promedio"] is not None else 0.0

    def calcular_promedio_asignatura(self, codigo_asignatura):
        """Calcula el promedio de una asignatura directamente con SQL."""
        conn = self._get_connection()
        fila = conn.execute(
            "SELECT ROUND(AVG(nota), 2) AS promedio FROM calificaciones WHERE codigo_asignatura = ?",
            (codigo_asignatura,),
        ).fetchone()
        conn.close()
        return fila["promedio"] if fila["promedio"] is not None else 0.0

    def obtener_distribucion_notas(self):
        """Cuenta aprobados y reprobados directamente con SQL."""
        conn = self._get_connection()
        fila = conn.execute("""
            SELECT
                COUNT(CASE WHEN nota >= 3.0 THEN 1 END) AS aprobados,
                COUNT(CASE WHEN nota <  3.0 THEN 1 END) AS reprobados,
                COUNT(*) AS total
            FROM calificaciones
        """).fetchone()
        conn.close()
        return {
            "Aprobados": fila["aprobados"],
            "Reprobados": fila["reprobados"],
            "Total_Calificaciones": fila["total"],
        }
