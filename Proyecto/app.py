# pyrefly: ignore [missing-import]
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from models.sistema import SistemaAcademico
from models.estudiante import Estudiante
from models.asignatura import Asignatura
from models.calificacion import Calificacion
from models.matricula import Matricula
from models.profesor import Profesor
from models.reportes import GestorReportes
import os
import sqlite3

# --- Ruta de la base de datos SQLite ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data_base', 'academico.db')

def get_db_connection():
    """Abre una conexión a la base de datos y devuelve filas como diccionarios."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # acceso por nombre de columna
    return conn

def init_db():
    """
    Inicializa la base de datos con todas las tablas y datos de prueba.
    Se ejecuta automáticamente al arrancar la app si el .db no existe.
    Esto es necesario para Render (sistema de archivos efímero).
    Delega la creación de tablas a database_setup.py para no duplicar SQL.
    """
    from database_setup import crear_tablas, insertar_datos_prueba, DB_PATH as _DB_PATH

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    crear_tablas(conn, cursor)
    insertar_datos_prueba(conn, cursor)

    conn.commit()
    conn.close()

# --- Inicializar BD al arrancar ---
init_db()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'clave_local_desarrollo')

# Instancia global del sistema
sistema = SistemaAcademico()
gestor_reportes = GestorReportes(sistema)

# Datos de prueba 
def cargar_datos_prueba():
    """Carga datos de demostración para visualizar reportes"""
    # Estudiantes
    est1 = Estudiante("1001", "Juan Pérez", "juan@unitec.edu")
    est2 = Estudiante("1002", "María García", "maria@unitec.edu")
    est3 = Estudiante("1003", "Carlos López", "carlos@unitec.edu")
    est4 = Estudiante("1004", "Ana Rodríguez", "ana@unitec.edu")
    est5 = Estudiante("1005", "Pedro Martínez", "pedro@unitec.edu")
    
    sistema.estudiantes = [est1, est2, est3, est4, est5]
    
    # Profesores
    prof1 = Profesor("P001", "Dr. Johan", "johan@unitec.edu", "Ingeniería Eléctrica")
    prof2 = Profesor("P002", "Dra. María", "maria.prof@unitec.edu", "Física")
    prof3 = Profesor("P003", "Dr. Carlos", "carlos.prof@unitec.edu", "Matemáticas")

    # Asignaturas (ahora reciben objetos Profesor en vez de strings)
    asig1 = Asignatura("ING101", "Cálculo I", 4, prof1)
    asig2 = Asignatura("ING102", "Programación I", 3, prof1)
    asig3 = Asignatura("ING103", "Física I", 4, prof2)
    asig4 = Asignatura("ING104", "Álgebra Lineal", 3, prof3)
    
    sistema.asignaturas = [asig1, asig2, asig3, asig4]
    
    # Calificaciones 
    calificaciones_data = [
        ("1001", "ING101", 4.5, "Corte 1"),
        ("1001", "ING102", 3.8, "Corte 1"),
        ("1001", "ING103", 4.2, "Corte 1"),
        ("1002", "ING101", 2.8, "Corte 1"),
        ("1002", "ING102", 3.1, "Corte 1"),
        ("1002", "ING103", 2.5, "Corte 1"),
        ("1003", "ING101", 3.9, "Corte 1"),
        ("1003", "ING102", 4.0, "Corte 1"),
        ("1003", "ING104", 3.5, "Corte 1"),
        ("1004", "ING102", 4.8, "Corte 1"),
        ("1004", "ING103", 4.6, "Corte 1"),
        ("1004", "ING104", 4.3, "Corte 1"),
        ("1005", "ING101", 2.2, "Corte 1"),
        ("1005", "ING102", 2.9, "Corte 1"),
        ("1005", "ING103", 2.1, "Corte 1"),
    ]
    
    sistema.calificaciones = [Calificacion(*datos) for datos in calificaciones_data]

cargar_datos_prueba()

# rutas de autenticacion
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    estadisticas = gestor_reportes.obtener_estadisticas_generales()
    return render_template('dashboard.html', 
                         usuario=session.get('usuario'),
                         rol=session.get('rol'),
                         estadisticas=estadisticas)

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    correo = data.get('usuario')   # el campo 'usuario' del form lleva el correo
    password = data.get('password')

    # --- Autenticación contra la base de datos SQLite ---
    try:
        conn = get_db_connection()
        usuario_db = conn.execute(
            'SELECT * FROM usuarios WHERE correo_institucional = ? AND contrasena = ?',
            (correo, password)
        ).fetchone()
        conn.close()
    except Exception as e:
        return jsonify({'success': False, 'mensaje': f'Error en la base de datos: {str(e)}'}), 500

    if usuario_db:
        session['usuario'] = usuario_db['nombre']
        session['correo'] = usuario_db['correo_institucional']
        session['rol'] = usuario_db['rol']
        return jsonify({'success': True, 'rol': usuario_db['rol'], 'nombre': usuario_db['nombre']})

    return jsonify({'success': False, 'mensaje': 'Correo o contraseña incorrectos'}), 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# rutas de reportes 
@app.route('/reportes')
def reportes():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    return render_template('reportes.html', usuario=session.get('usuario'))

@app.route('/reportes/distribucion-notas')
def reporte_distribucion():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    grafico = gestor_reportes.grafico_distribucion_notas()
    return render_template('reporte_individual.html', 
                         titulo='Distribución de Notas',
                         grafico=grafico,
                         usuario=session.get('usuario'))

@app.route('/reportes/promedios-estudiantes')
def reporte_promedios_estudiantes():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    grafico = gestor_reportes.grafico_promedios_estudiantes()
    return render_template('reporte_individual.html',
                         titulo='Promedios por Estudiante',
                         grafico=grafico,
                         usuario=session.get('usuario'))

@app.route('/reportes/promedios-asignaturas')
def reporte_promedios_asignaturas():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    grafico = gestor_reportes.grafico_promedios_asignaturas()
    return render_template('reporte_individual.html',
                         titulo='Promedios por Asignatura',
                         grafico=grafico,
                         usuario=session.get('usuario'))

@app.route('/reportes/aprobacion')
def reporte_aprobacion():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    grafico = gestor_reportes.grafico_aprobacion()
    return render_template('reporte_individual.html',
                         titulo='Distribución: Aprobados vs Reprobados',
                         grafico=grafico,
                         usuario=session.get('usuario'))

@app.route('/reportes/rangos')
def reporte_rangos():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    grafico = gestor_reportes.grafico_comparacion_rangos()
    return render_template('reporte_individual.html',
                         titulo='Distribución por Rangos de Calificaciones',
                         grafico=grafico,
                         usuario=session.get('usuario'))

@app.route('/api/estadisticas')
def api_estadisticas():
    if 'usuario' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    return jsonify(gestor_reportes.obtener_estadisticas_generales())

if __name__ == '__main__':
    app.run(debug=True, port=5000)