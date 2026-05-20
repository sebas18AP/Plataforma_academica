import hashlib
import sqlite3

# pyrefly: ignore [missing-import]
from werkzeug.security import generate_password_hash

from models.asignatura import Asignatura
from models.calificacion import Calificacion
from models.estudiante import Estudiante
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

    def obtener_perfil_usuario(self, correo, rol):
        """Obtiene los datos completos del usuario según su rol."""
        conn = self._get_connection()
        try:
            if rol == 'Estudiante':
                return conn.execute("SELECT id as identificacion, nombre, correo FROM estudiantes WHERE correo = ?", (correo,)).fetchone()
            elif rol == 'Profesor':
                return conn.execute("SELECT id as identificacion, nombre, correo, departamento FROM profesores WHERE correo = ?", (correo,)).fetchone()
        finally:
            conn.close()
        return None

    def obtener_usuario_por_correo(self, correo):
        """Busca un usuario en la tabla de credenciales para autenticación."""
        conn = self._get_connection()
        try:
            return conn.execute("SELECT * FROM usuarios WHERE correo_institucional = ?", (correo,)).fetchone()
        finally:
            conn.close()

    def actualizar_usuario(self, correo_actual, rol, nombre, contrasena_nueva=None, departamento=None):
        """Actualiza la información del usuario en la tabla de autenticación y su perfil."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            # 1. Actualizar tabla usuarios (auth)
            if contrasena_nueva:
                hash_pwd = generate_password_hash(contrasena_nueva)
                cursor.execute("UPDATE usuarios SET nombre = ?, contrasena = ? WHERE correo_institucional = ?", 
                               (nombre, hash_pwd, correo_actual))
            else:
                cursor.execute("UPDATE usuarios SET nombre = ? WHERE correo_institucional = ?", 
                               (nombre, correo_actual))
            
            # 2. Actualizar tabla de perfil
            if rol == 'Estudiante':
                cursor.execute("UPDATE estudiantes SET nombre = ? WHERE correo = ?", (nombre, correo_actual))
            elif rol == 'Profesor':
                # Si no se envía departamento, se mantiene el actual
                if departamento is not None:
                    cursor.execute("UPDATE profesores SET nombre = ?, departamento = ? WHERE correo = ?", 
                                   (nombre, departamento, correo_actual))
                else:
                    cursor.execute("UPDATE profesores SET nombre = ? WHERE correo = ?", 
                                   (nombre, correo_actual))
            
            conn.commit()
            return True, "Perfil actualizado exitosamente"
        except Exception as e:
            return False, f"Error al actualizar: {str(e)}"
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

    def registrar_calificacion(self, estudiante_id, codigo_asignatura, nota, corte):
        """Inserta una calificación en la BD, validando la nota."""
        try:
            nota = float(nota)
            if not (0.0 <= nota <= 5.0):
                return "Error: La nota debe estar entre 0.0 y 5.0"
        except ValueError:
            return "Error: La nota debe ser un número"

        conn = self._get_connection()
        try:
            conn.execute(
                "INSERT INTO calificaciones (estudiante_id, codigo_asignatura, nota, corte) "
                "VALUES (?, ?, ?, ?)",
                (estudiante_id, codigo_asignatura, nota, corte),
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

    def obtener_promedios_todos_estudiantes(self):
        """Obtiene el promedio de todos los estudiantes en una sola consulta SQL (Evita N+1)."""
        conn = self._get_connection()
        filas = conn.execute("""
            SELECT e.id, e.nombre, ROUND(AVG(c.nota), 2) AS promedio
            FROM estudiantes e
            LEFT JOIN calificaciones c ON e.id = c.estudiante_id
            GROUP BY e.id, e.nombre
        """).fetchall()
        conn.close()
        return [{"id": f["id"], "nombre": f["nombre"], "promedio": f["promedio"] if f["promedio"] is not None else 0.0} for f in filas]

    def obtener_promedios_todas_asignaturas(self):
        """Obtiene el promedio de todas las asignaturas en una sola consulta SQL (Evita N+1)."""
        conn = self._get_connection()
        filas = conn.execute("""
            SELECT a.codigo, a.nombre, ROUND(AVG(c.nota), 2) AS promedio
            FROM asignaturas a
            LEFT JOIN calificaciones c ON a.codigo = c.codigo_asignatura
            GROUP BY a.codigo, a.nombre
        """).fetchall()
        conn.close()
        return [{"codigo": f["codigo"], "nombre": f["nombre"], "promedio": f["promedio"] if f["promedio"] is not None else 0.0} for f in filas]

    def obtener_estadisticas_globales_sql(self):
        """Obtiene estadísticas globales agregadas de toda la BD en una sola consulta."""
        conn = self._get_connection()
        fila = conn.execute("""
            SELECT 
                COUNT(*) AS total_calificaciones,
                ROUND(AVG(nota), 2) AS promedio_general,
                MAX(nota) AS nota_maxima,
                MIN(nota) AS nota_minima
            FROM calificaciones
        """).fetchone()
        
        aprobados_fila = conn.execute("SELECT COUNT(*) as aprobados FROM calificaciones WHERE nota >= 3.0").fetchone()
        conn.close()
        
        total_calif = fila["total_calificaciones"] or 0
        aprobados = aprobados_fila["aprobados"] or 0
        reprobados = total_calif - aprobados
        
        return {
            "total_calificaciones": total_calif,
            "promedio_general": fila["promedio_general"] if fila["promedio_general"] is not None else 0.0,
            "nota_maxima": fila["nota_maxima"] if fila["nota_maxima"] is not None else 0.0,
            "nota_minima": fila["nota_minima"] if fila["nota_minima"] is not None else 0.0,
            "aprobados": aprobados,
            "reprobados": reprobados,
            "tasa_aprobacion": round((aprobados / total_calif * 100), 1) if total_calif > 0 else 0
        }

    def obtener_estadisticas_estudiante(self, estudiante_id):
        """Obtiene estadísticas específicas de un estudiante."""
        conn = self._get_connection()
        total_asignaturas = conn.execute("SELECT COUNT(*) as count FROM matriculas WHERE estudiante_id = ?", (estudiante_id,)).fetchone()["count"]
        
        fila = conn.execute("""
            SELECT 
                COUNT(*) AS total_calificaciones,
                ROUND(AVG(nota), 2) AS promedio_general,
                MAX(nota) AS nota_maxima,
                MIN(nota) AS nota_minima
            FROM calificaciones
            WHERE estudiante_id = ?
        """, (estudiante_id,)).fetchone()
        
        aprobados_fila = conn.execute("SELECT COUNT(*) as aprobados FROM calificaciones WHERE estudiante_id = ? AND nota >= 3.0", (estudiante_id,)).fetchone()
        conn.close()
        
        total_calif = fila["total_calificaciones"] or 0
        aprobados = aprobados_fila["aprobados"] or 0
        reprobados = total_calif - aprobados
        
        return {
            "total_estudiantes": 1,
            "total_asignaturas": total_asignaturas,
            "total_calificaciones": total_calif,
            "promedio_general": fila["promedio_general"] if fila["promedio_general"] is not None else 0.0,
            "nota_maxima": fila["nota_maxima"] if fila["nota_maxima"] is not None else 0.0,
            "nota_minima": fila["nota_minima"] if fila["nota_minima"] is not None else 0.0,
            "aprobados": aprobados,
            "reprobados": reprobados,
            "tasa_aprobacion": round((aprobados / total_calif * 100), 1) if total_calif > 0 else 0
        }

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

    def obtener_estudiantes_en_riesgo(self):
        """Retorna lista de estudiantes con promedio < 3.0 mediante consulta SQL."""
        conn = self._get_connection()
        filas = conn.execute("""
            SELECT e.id, e.nombre, ROUND(AVG(c.nota), 2) AS promedio
            FROM estudiantes e
            JOIN calificaciones c ON e.id = c.estudiante_id
            GROUP BY e.id, e.nombre
            HAVING promedio < 3.0
            ORDER BY promedio ASC
        """).fetchall()
        conn.close()
        return [{"id": f["id"], "nombre": f["nombre"], "promedio": f["promedio"]} for f in filas]

    def obtener_notas_estudiante(self, estudiante_id):
        """Obtiene el historial detallado de notas de un estudiante por cortes."""
        conn = self._get_connection()
        try:
            filas = conn.execute("""
                SELECT a.codigo, a.nombre as asignatura, c.corte, c.nota
                FROM matriculas m
                JOIN asignaturas a ON m.codigo_asignatura = a.codigo
                LEFT JOIN calificaciones c ON m.estudiante_id = c.estudiante_id AND m.codigo_asignatura = c.codigo_asignatura
                WHERE m.estudiante_id = ?
                ORDER BY a.nombre, c.corte
            """, (estudiante_id,)).fetchall()
            
            resultados = {}
            for f in filas:
                codigo = f["codigo"]
                if codigo not in resultados:
                    resultados[codigo] = {
                        "asignatura": f["asignatura"],
                        "Corte 1": "-",
                        "Corte 2": "-",
                        "Corte 3": "-",
                        "Final": "-",
                        "definitiva": 0.0
                    }
                if f["corte"] and f["nota"] is not None:
                    resultados[codigo][f["corte"]] = f["nota"]
                    
            for codigo, datos in resultados.items():
                notas = [datos[c] for c in ["Corte 1", "Corte 2", "Corte 3", "Final"] if datos[c] != "-"]
                if notas:
                    datos["definitiva"] = round(sum(notas) / len(notas), 2)
                else:
                    datos["definitiva"] = "-"
                    
            return list(resultados.values())
        finally:
            conn.close()

    def obtener_proyeccion_estudiante(self, estudiante_id):
        """
        Calcula la proyección de notas con pesos exactos:
        Corte 1 (30%), Corte 2 (20%), Corte 3 (20%), Final (30%).
        Genera opciones de distribución variable para múltiples cortes faltantes.
        """
        notas_actuales = self.obtener_notas_estudiante(estudiante_id)
        pesos = {
            "Corte 1": 0.30,
            "Corte 2": 0.20,
            "Corte 3": 0.20,
            "Final": 0.30
        }
        
        proyecciones = []
        for mat in notas_actuales:
            acumulado = 0.0
            peso_evaluado = 0.0
            faltantes = []
            
            for corte, peso in pesos.items():
                if mat[corte] != "-":
                    acumulado += mat[corte] * peso
                    peso_evaluado += peso
                else:
                    faltantes.append(corte)
            
            peso_restante = round(1.0 - peso_evaluado, 2)
            porcentaje_evaluado = int(round(peso_evaluado * 100))
            porcentaje_restante = int(round(peso_restante * 100))
            
            opciones = []
            
            if len(faltantes) == 0:
                nota_requerida = 0.0
                if acumulado >= 3.0:
                    estado = "aprobada"
                    mensaje = "¡Materia superada con éxito! Has completado el 100% de los cortes."
                else:
                    estado = "imposible"
                    mensaje = f"Materia finalizada. Definitiva ({round(acumulado, 2)}) inferior a 3.0."
            else:
                puntos_faltantes = round(3.0 - acumulado, 4)
                nota_requerida = round(puntos_faltantes / peso_restante, 2)
                
                if nota_requerida <= 0.0:
                    estado = "aprobada"
                    nota_requerida = 0.0
                    mensaje = "¡Felicidades! Ya tienes suficientes puntos acumulados para asegurar la materia."
                elif nota_requerida > 5.0:
                    estado = "imposible"
                    mensaje = f"Matemáticamente imposible. Necesitarías {nota_requerida} en promedio."
                else:
                    if nota_requerida <= 3.0:
                        estado = "facil"
                        mensaje = f"Buen panorama: necesitas un promedio accesible de {nota_requerida} en lo que falta."
                    elif nota_requerida <= 4.2:
                        estado = "moderado"
                        mensaje = f"Requiere constancia: necesitas promediar {nota_requerida} en los cortes restantes."
                    else:
                        estado = "dificil"
                        mensaje = f"¡Alerta! Necesitas un rendimiento sobresaliente de {nota_requerida} para aprobar."
                    
                    if len(faltantes) > 1:
                        opciones.append(f"Uniforme: Promediar {nota_requerida} en los cortes restantes ({', '.join(faltantes)}).")
                        
                        proximo = faltantes[0]
                        peso_proximo = pesos[proximo]
                        peso_subsiguiente = round(peso_restante - peso_proximo, 2)
                        
                        puntos_si_3 = puntos_faltantes - (3.0 * peso_proximo)
                        nota_resto_si_3 = round(puntos_si_3 / peso_subsiguiente, 1)
                        if 1.0 <= nota_resto_si_3 <= 5.0:
                            nombres_resto = ", ".join(faltantes[1:])
                            opciones.append(f"Estratégica: Sacar 3.0 en {proximo} y necesitar {max(1.0, nota_resto_si_3)} en el resto ({nombres_resto}).")
                            
                        puntos_si_4 = puntos_faltantes - (4.0 * peso_proximo)
                        nota_resto_si_4 = round(puntos_si_4 / peso_subsiguiente, 1)
                        if 0.0 <= nota_resto_si_4 <= 5.0:
                            nombres_resto = ", ".join(faltantes[1:])
                            opciones.append(f"Aseguradora: Asegurar 4.0 en {proximo} para relajar la nota a {max(1.0, nota_resto_si_4)} en el resto ({nombres_resto}).")
                    elif len(faltantes) == 1:
                        opciones.append(f"Último esfuerzo: Necesitas exactamente {nota_requerida} en la evaluación de {faltantes[0]} ({int(pesos[faltantes[0]]*100)}%).")

            proyecciones.append({
                "asignatura": mat["asignatura"],
                "acumulado": round(acumulado, 2),
                "definitiva": mat["definitiva"],
                "porcentaje_evaluado": porcentaje_evaluado,
                "porcentaje_restante": porcentaje_restante,
                "cortes_restantes": len(faltantes),
                "cortes_faltantes_nombres": faltantes,
                "nota_requerida": nota_requerida,
                "estado": estado,
                "mensaje": mensaje,
                "opciones": opciones
            })
            
        return proyecciones

    def obtener_boletin_estudiante(self, estudiante_id):
        """Genera los datos consolidados y oficiales para el boletín académico."""
        conn = self._get_connection()
        try:
            estudiante = conn.execute("SELECT id, nombre, correo FROM estudiantes WHERE id = ?", (estudiante_id,)).fetchone()
            if not estudiante:
                return None
                
            notas_materia = self.obtener_notas_estudiante(estudiante_id)
            
            suma_definitivas = 0.0
            materias_con_definitiva = 0
            for mat in notas_materia:
                if mat['definitiva'] != '-' and mat['definitiva'] > 0:
                    suma_definitivas += mat['definitiva']
                    materias_con_definitiva += 1
                    
            promedio_gpa = round(suma_definitivas / materias_con_definitiva, 2) if materias_con_definitiva > 0 else 0.0
            
            raw_data = f"{estudiante['id']}-{estudiante['nombre']}-{promedio_gpa}"
            codigo_verificacion = "UNITEC-" + hashlib.sha256(raw_data.encode()).hexdigest()[:8].upper()
            
            return {
                "estudiante": estudiante,
                "asignaturas": notas_materia,
                "promedio_general": promedio_gpa,
                "total_asignaturas": len(notas_materia),
                "codigo_verificacion": codigo_verificacion
            }
        finally:
            conn.close()

    def generar_consejos_estudiante(self, estudiante_id):
        """Genera un análisis inteligente de tendencias y alertas tempranas para el estudiante."""
        notas_materia = self.obtener_notas_estudiante(estudiante_id)
        proyecciones = self.obtener_proyeccion_estudiante(estudiante_id)
        
        consejos = []
        for mat, proy in zip(notas_materia, proyecciones):
            asig = mat["asignatura"]
            c1 = mat["Corte 1"]
            c2 = mat["Corte 2"]
            
            if c1 != "-" and c2 != "-":
                dif = round(c1 - c2, 2)
                if dif >= 0.6:
                    consejos.append({
                        "tipo": "alerta",
                        "icono": "📉",
                        "titulo": f"Caída de rendimiento en {asig}",
                        "mensaje": f"Tus calificaciones disminuyeron {dif} puntos del Corte 1 al Corte 2. Te sugerimos reforzar los temas actuales y solicitar asesoría docente."
                    })
                elif round(c2 - c1, 2) >= 0.6:
                    consejos.append({
                        "tipo": "exito",
                        "icono": "🚀",
                        "titulo": f"Mejora notable en {asig}",
                        "mensaje": f"¡Gran trabajo! Aumentaste {round(c2 - c1, 2)} puntos en el Corte 2. Sigue manteniendo este excelente ritmo de estudio."
                    })

            if mat["definitiva"] != "-" and mat["definitiva"] >= 4.5 and proy["porcentaje_evaluado"] >= 50:
                consejos.append({
                    "tipo": "excelencia",
                    "icono": "🌟",
                    "titulo": f"Nivel Sobresaliente en {asig}",
                    "mensaje": f"Mantienes un promedio impecable de {mat['definitiva']}. Tienes un dominio destacado de esta materia."
                })
                
            if proy["estado"] in ["moderado", "dificil"]:
                consejos.append({
                    "tipo": "advertencia",
                    "icono": "⚠️",
                    "titulo": f"Alerta Temprana en {asig}",
                    "mensaje": f"Para aprobar necesitas promediar {proy['nota_requerida']} en el {proy['porcentaje_restante']}% restante. Es momento de enfocar tus horas de estudio autónomo aquí."
                })
                
        if not consejos and notas_materia:
            consejos.append({
                "tipo": "info",
                "icono": "💡",
                "titulo": "Estabilidad Académica",
                "mensaje": "Tus calificaciones se mantienen estables y sin riesgos inminentes. ¡Continúa cumpliendo con tus entregas a tiempo!"
            })
            
        return consejos
