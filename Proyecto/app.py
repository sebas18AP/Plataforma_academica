import csv
from functools import wraps
from io import StringIO
import os
import sqlite3

# pyrefly: ignore [missing-import]
from flask import Flask, Response, flash, jsonify, redirect, render_template, request, session, url_for
# pyrefly: ignore [missing-import]
from werkzeug.security import check_password_hash

from models.reportes import GestorReportes
from models.sistema import SistemaAcademico

# --- Ruta de la base de datos SQLite ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'academico.db')


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

# Decorador de RBAC
def requiere_rol(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if 'usuario' not in session:
                flash('Por favor inicie sesión para acceder a esta página.', 'error')
                return redirect(url_for('login'))
            if session.get('rol') not in roles:
                flash('Acceso denegado. No tiene los permisos necesarios.', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return wrapped
    return wrapper

# rutas de autenticacion
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    rol = session.get('rol')
    consejos = []
    if rol == 'Estudiante':
        correo = session.get('correo')
        estudiante_db = sistema.obtener_perfil_usuario(correo, rol)
        if estudiante_db:
            ident = estudiante_db['identificacion']
            estadisticas = sistema.obtener_estadisticas_estudiante(ident)
            notas = sistema.obtener_notas_estudiante(ident)
            consejos = sistema.generar_consejos_estudiante(ident)
        else:
            estadisticas = gestor_reportes.obtener_estadisticas_generales()
            notas = []
    else:
        estadisticas = gestor_reportes.obtener_estadisticas_generales()
        notas = []
        
    return render_template('dashboard.html', 
                         usuario=session.get('usuario'),
                         rol=rol,
                         estadisticas=estadisticas,
                         notas=notas,
                         consejos=consejos)

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    correo = data.get('usuario')   # el campo 'usuario' del form lleva el correo
    password = data.get('password')

    # --- Autenticación contra la base de datos SQLite ---
    try:
        usuario_db = sistema.obtener_usuario_por_correo(correo)
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

@app.route('/matricular', methods=['GET', 'POST'])
def matricular():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Procesar matrícula (vía formulario tradicional o AJAX)
        estudiante_id = request.form.get('estudiante_id')
        codigo_asig = request.form.get('codigo_asignatura')
        periodo = request.form.get('periodo')
        
        if not all([estudiante_id, codigo_asig, periodo]):
            flash('Error: Faltan campos obligatorios', 'error')
            return redirect(url_for('matricular'))
            
        mensaje = sistema.matricular_estudiante(estudiante_id, codigo_asig, periodo)
        flash(mensaje, 'success' if 'exito' in mensaje.lower() else 'error')
        return redirect(url_for('dashboard'))

    # Cargar datos para los selects
    estudiantes = sistema.obtener_estudiantes()
    asignaturas = sistema.obtener_asignaturas()
    return render_template('matricular.html', 
                         estudiantes=estudiantes, 
                         asignaturas=asignaturas,
                         usuario=session.get('usuario'))

@app.route('/calificar', methods=['GET', 'POST'])
@requiere_rol('Profesor')
def calificar():
    if request.method == 'POST':
        estudiante_id = request.form.get('estudiante_id')
        codigo_asig = request.form.get('codigo_asignatura')
        nota = request.form.get('nota')
        corte = request.form.get('corte')
        
        if not all([estudiante_id, codigo_asig, nota, corte]):
            flash('Error: Faltan campos obligatorios', 'error')
            return redirect(url_for('calificar'))
            
        mensaje = sistema.registrar_calificacion(estudiante_id, codigo_asig, nota, corte)
        flash(mensaje, 'success' if 'exito' in mensaje.lower() else 'error')
        return redirect(url_for('dashboard'))

    # Cargar datos para los selects
    estudiantes = sistema.obtener_estudiantes()
    asignaturas = sistema.obtener_asignaturas()
    return render_template('calificar.html', 
                         estudiantes=estudiantes, 
                         asignaturas=asignaturas,
                         usuario=session.get('usuario'))

@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if 'usuario' not in session:
        return redirect(url_for('login'))
        
    correo = session.get('correo')
    rol = session.get('rol')
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        contrasena = request.form.get('contrasena') # Opcional
        departamento = request.form.get('departamento') # Solo para profesores
        
        if not nombre:
            flash('Error: El nombre es obligatorio', 'error')
            return redirect(url_for('perfil'))
            
        success, mensaje = sistema.actualizar_usuario(
            correo_actual=correo, 
            rol=rol, 
            nombre=nombre, 
            contrasena_nueva=contrasena if contrasena else None, 
            departamento=departamento
        )
        
        if success:
            session['usuario'] = nombre # Actualizar el nombre en la sesión
            flash(mensaje, 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(f"Error al actualizar: {mensaje}", 'error')
            return redirect(url_for('perfil'))

    # GET: Cargar datos actuales
    perfil_data = sistema.obtener_perfil_usuario(correo, rol)
    return render_template('editar_perfil.html', 
                         usuario=session.get('usuario'),
                         rol=rol,
                         perfil=perfil_data)
@app.route('/simulador')
@requiere_rol('Estudiante')
def simulador():
    correo = session.get('correo')
    rol = session.get('rol')
    estudiante_db = sistema.obtener_perfil_usuario(correo, rol)
    
    if not estudiante_db:
        flash('No se pudo encontrar la información del estudiante.', 'error')
        return redirect(url_for('dashboard'))
        
    proyecciones = sistema.obtener_proyeccion_estudiante(estudiante_db['identificacion'])
    return render_template('simulador.html',
                         usuario=session.get('usuario'),
                         rol=rol,
                         proyecciones=proyecciones)

@app.route('/boletin')
@requiere_rol('Estudiante')
def boletin():
    correo = session.get('correo')
    rol = session.get('rol')
    estudiante_db = sistema.obtener_perfil_usuario(correo, rol)
    
    if not estudiante_db:
        flash('No se pudo cargar la información para el boletín.', 'error')
        return redirect(url_for('dashboard'))
        
    boletin_data = sistema.obtener_boletin_estudiante(estudiante_db['identificacion'])
    if not boletin_data:
        flash('No se pudo generar el boletín oficial.', 'error')
        return redirect(url_for('dashboard'))
        
    return render_template('boletin.html', boletin=boletin_data, fecha=datetime.now().strftime('%d/%m/%Y'))

# rutas de reportes 
@app.route('/reportes')
def reportes():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    promedios = sistema.obtener_promedios_todos_estudiantes()
    promedios_validos = [p for p in promedios if p['promedio'] > 0.0]
    return render_template('reportes.html', usuario=session.get('usuario'), promedios=promedios_validos)

@app.route('/exportar-notas')
def exportar_notas():
    if 'usuario' not in session or session.get('rol') == 'Estudiante':
        flash('No tienes permisos para realizar esta accion.', 'error')
        return redirect(url_for('login'))
        
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    calificaciones = conn.execute("""
        SELECT 
            c.estudiante_id, 
            e.nombre AS estudiante_nombre,
            c.codigo_asignatura, 
            a.nombre AS asignatura_nombre,
            c.corte, 
            c.nota
        FROM calificaciones c
        JOIN estudiantes e ON c.estudiante_id = e.id
        JOIN asignaturas a ON c.codigo_asignatura = a.codigo
        ORDER BY a.nombre, e.nombre, c.corte
    """).fetchall()
    conn.close()
    
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID Estudiante', 'Nombre Estudiante', 'Codigo Asignatura', 'Nombre Asignatura', 'Corte', 'Nota'])
    for c in calificaciones:
        cw.writerow([c['estudiante_id'], c['estudiante_nombre'], c['codigo_asignatura'], c['asignatura_nombre'], c['corte'], c['nota']])
        
    output = si.getvalue()
    bom = "\ufeff"
    response_data = bom + output
    
    return Response(
        response_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=reporte_notas.csv"}
    )

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

@app.route('/reportes/riesgo')
def reporte_riesgo():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    estudiantes_riesgo = sistema.obtener_estudiantes_en_riesgo()
    return render_template('reporte_riesgo.html', 
                         titulo='Estudiantes en Riesgo',
                         estudiantes=estudiantes_riesgo,
                         usuario=session.get('usuario'))

@app.route('/api/estadisticas')
def api_estadisticas():
    if 'usuario' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    return jsonify(gestor_reportes.obtener_estadisticas_generales())

if __name__ == '__main__':
    app.run(debug=True, port=5000)