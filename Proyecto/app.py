# pyrefly: ignore [missing-import]
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import check_password_hash

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
    from database_setup import crear_tablas, insertar_datos_prueba

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

# Instancia global del sistema (ahora conectada a SQLite)
sistema = SistemaAcademico(DB_PATH)
gestor_reportes = GestorReportes(sistema)

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

    if usuario_db and check_password_hash(usuario_db['contrasena'], password):
        session['usuario'] = usuario_db['nombre']
        session['correo'] = usuario_db['correo_institucional']
        session['rol'] = usuario_db['rol']
        return jsonify({'success': True, 'rol': usuario_db['rol'], 'nombre': usuario_db['nombre']})

    return jsonify({'success': False, 'mensaje': 'Correo o contraseña incorrectos'}), 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- Rutas de Registro ---

@app.route('/registro')
def registro():
    return render_template('registro.html')

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    nombre = data.get('nombre')
    identificacion = data.get('identificacion')
    correo = data.get('correo')
    password = data.get('password')
    rol = data.get('rol')
    
    # Validaciones básicas
    if not all([nombre, identificacion, correo, password, rol]):
        return jsonify({'success': False, 'mensaje': 'Todos los campos son obligatorios'}), 400
    
    success, mensaje = sistema.registrar_usuario(nombre, identificacion, correo, password, rol)
    
    if success:
        return jsonify({'success': True, 'mensaje': mensaje})
    else:
        return jsonify({'success': False, 'mensaje': mensaje}), 400

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