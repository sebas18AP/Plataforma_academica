"""
database_setup.py
-----------------
Script de inicialización de la base de datos SQLite para la
Plataforma de Monitoreo Académico - UNITEC
Facultad de Ingeniería Eléctrica

Ejecutar UNA SOLA VEZ para crear y poblar la base de datos.

Uso:
    cd Proyecto
    python database_setup.py

Esto creará (o actualizará) el archivo: data_base/academico.db
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

# --- Ruta de la base de datos ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "academico.db")


# ================================================================
#  CREACIÓN DE TABLAS
# ================================================================

def crear_tablas(conn, cursor):
    """Crea todas las tablas del sistema académico."""
    print(f"[INFO] Creando base de datos en: {DB_PATH}")

    # Habilitar llaves foráneas (SQLite las trae desactivadas por defecto)
    cursor.execute("PRAGMA foreign_keys = ON")

    # --- 1. Tabla de usuarios (login / autenticación) ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre               TEXT    NOT NULL,
            correo_institucional TEXT    NOT NULL UNIQUE,
            contrasena           TEXT    NOT NULL,
            rol                  TEXT    NOT NULL DEFAULT 'Estudiante'
        )
    """)
    print("[OK] Tabla 'usuarios' creada correctamente.")

    # --- 2. Tabla de estudiantes ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estudiantes (
            id      TEXT PRIMARY KEY,
            nombre  TEXT NOT NULL,
            correo  TEXT NOT NULL UNIQUE
        )
    """)
    print("[OK] Tabla 'estudiantes' creada correctamente.")

    # --- 3. Tabla de profesores ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profesores (
            id            TEXT PRIMARY KEY,
            nombre        TEXT NOT NULL,
            correo        TEXT NOT NULL UNIQUE,
            departamento  TEXT DEFAULT ''
        )
    """)
    print("[OK] Tabla 'profesores' creada correctamente.")

    # --- 4. Tabla de asignaturas ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS asignaturas (
            codigo       TEXT    PRIMARY KEY,
            nombre       TEXT    NOT NULL,
            creditos     INTEGER NOT NULL,
            profesor_id  TEXT,
            FOREIGN KEY (profesor_id) REFERENCES profesores(id)
        )
    """)
    print("[OK] Tabla 'asignaturas' creada correctamente.")

    # --- 5. Tabla de matrículas ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matriculas (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            estudiante_id       TEXT    NOT NULL,
            codigo_asignatura   TEXT    NOT NULL,
            periodo             TEXT    NOT NULL,
            FOREIGN KEY (estudiante_id)     REFERENCES estudiantes(id),
            FOREIGN KEY (codigo_asignatura) REFERENCES asignaturas(codigo),
            UNIQUE(estudiante_id, codigo_asignatura, periodo)
        )
    """)
    print("[OK] Tabla 'matriculas' creada correctamente.")

    # --- 6. Tabla de calificaciones ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calificaciones (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            estudiante_id       TEXT    NOT NULL,
            codigo_asignatura   TEXT    NOT NULL,
            nota                REAL    NOT NULL,
            corte               TEXT    NOT NULL,
            FOREIGN KEY (estudiante_id)     REFERENCES estudiantes(id),
            FOREIGN KEY (codigo_asignatura) REFERENCES asignaturas(codigo),
            UNIQUE(estudiante_id, codigo_asignatura, corte)
        )
    """)
    print("[OK] Tabla 'calificaciones' creada correctamente.")

    conn.commit()


# ================================================================
#  INSERCIÓN DE DATOS DE PRUEBA
# ================================================================

def _insertar_lote(cursor, tabla, columnas, datos):
    """
    Inserta un lote de filas en una tabla, omitiendo duplicados.
    Retorna la cantidad de filas insertadas y omitidas.
    """
    placeholders = ", ".join(["?"] * len(columnas))
    sql = f"INSERT INTO {tabla} ({', '.join(columnas)}) VALUES ({placeholders})"

    insertados = 0
    omitidos = 0

    for fila in datos:
        try:
            cursor.execute(sql, fila)
            insertados += 1
        except sqlite3.IntegrityError:
            omitidos += 1

    return insertados, omitidos


def insertar_datos_prueba(conn, cursor):
    """Inserta todos los datos de demostración del sistema."""

    # --- Usuarios (credenciales de login) ---
    print("\n-- Usuarios --")
    usuarios_crudos = [
        ("Carlos Andrés Pérez",   "c.perez@unitec.edu.co",      "unitec2026", "Estudiante"),
        ("Valentina Gómez",       "v.gomez@unitec.edu.co",      "unitec2026", "Estudiante"),
        ("Jorge Luis Rodríguez",  "j.rodriguez@unitec.edu.co",  "unitec2026", "Estudiante"),
        ("Mariana Lucía Toro",    "m.toro@unitec.edu.co",       "unitec2026", "Estudiante"),
        ("Felipe Santiago Ruiz",  "f.ruiz@unitec.edu.co",       "unitec2026", "Estudiante"),
        ("Ana María Castro",      "a.castro@unitec.edu.co",     "unitec2026", "Estudiante"),
        ("Luis Miguel Ortiz",     "l.ortiz@unitec.edu.co",      "unitec2026", "Estudiante"),
        ("Sofía Isabel Vega",     "s.vega@unitec.edu.co",       "unitec2026", "Estudiante"),
        ("Diego Alejandro Silva", "d.silva@unitec.edu.co",      "unitec2026", "Estudiante"),
        ("Camila Andrea Rojas",   "c.rojas@unitec.edu.co",      "unitec2026", "Estudiante"),
        ("Mateo Sebastián Cruz",  "m.cruz@unitec.edu.co",       "unitec2026", "Estudiante"),
        ("Valeria Pineda",        "v.pineda@unitec.edu.co",     "unitec2026", "Estudiante"),
        ("Sebastián Mora",        "s.mora@unitec.edu.co",       "unitec2026", "Estudiante"),
        ("Daniela Ospina",        "d.ospina@unitec.edu.co",     "unitec2026", "Estudiante"),
        ("Andrés Felipe Ríos",    "a.rios@unitec.edu.co",       "unitec2026", "Estudiante"),

        ("Dr. Johan Martínez",    "johan@unitec.edu.co",        "prof2026",   "Profesor"),
        ("Dra. María Fernández",  "maria.prof@unitec.edu.co",   "prof2026",   "Profesor"),
        ("Dr. Carlos Ramírez",    "carlos.prof@unitec.edu.co",  "prof2026",   "Profesor"),
        ("Dra. Laura Gómez",      "laura.prof@unitec.edu.co",   "prof2026",   "Profesor"),
    ]
    
    # Aplicar hash a las contraseñas
    usuarios = []
    for u in usuarios_crudos:
        hash_pwd = generate_password_hash(u[2])
        usuarios.append((u[0], u[1], hash_pwd, u[3]))

    ins, omi = _insertar_lote(
        cursor, "usuarios",
        ("nombre", "correo_institucional", "contrasena", "rol"),
        usuarios,
    )
    print(f"  Insertados: {ins} | Omitidos: {omi}")

    # --- Estudiantes ---
    print("\n-- Estudiantes --")
    estudiantes = [
        (f"{1001+i}", u[0], u[1]) for i, u in enumerate(usuarios_crudos) if u[3] == "Estudiante"
    ]
    ins, omi = _insertar_lote(
        cursor, "estudiantes", ("id", "nombre", "correo"), estudiantes
    )
    print(f"  Insertados: {ins} | Omitidos: {omi}")

    # --- Profesores ---
    print("\n-- Profesores --")
    profesores_data = [u for u in usuarios_crudos if u[3] == "Profesor"]
    deptos = ["Ingeniería Eléctrica", "Física", "Matemáticas", "Sistemas"]
    profesores = [
        (f"P{i+1:03d}", p[0], p[1], deptos[i]) for i, p in enumerate(profesores_data)
    ]
    ins, omi = _insertar_lote(
        cursor, "profesores", ("id", "nombre", "correo", "departamento"), profesores
    )
    print(f"  Insertados: {ins} | Omitidos: {omi}")

    # --- Asignaturas ---
    print("\n-- Asignaturas --")
    asignaturas = [
        ("ING101", "Cálculo I",        4, "P001"),
        ("ING102", "Programación I",   3, "P002"),
        ("ING103", "Física I",         4, "P003"),
        ("ING104", "Álgebra Lineal",   3, "P004"),
    ]
    ins, omi = _insertar_lote(
        cursor, "asignaturas", ("codigo", "nombre", "creditos", "profesor_id"), asignaturas
    )
    print(f"  Insertados: {ins} | Omitidos: {omi}")

    # --- Matrículas (asociar estudiantes a materias, periodo 2026-1) ---
    print("\n-- Matrículas --")
    import random
    random.seed(42) # For reproducibility
    matriculas = []
    calificaciones = []
    
    for est in estudiantes:
        est_id = est[0]
        # Cada estudiante inscribe entre 2 y 4 asignaturas
        num_materias = random.randint(2, 4)
        materias_est = random.sample(asignaturas, num_materias)
        for asig in materias_est:
            asig_cod = asig[0]
            matriculas.append((est_id, asig_cod, "2026-1"))
            
            # Determinamos de forma aleatoria cuántos cortes ya se han calificado (entre 1 y 4)
            avance = random.choice([1, 2, 3, 4])
            cortes_disponibles = ["Corte 1", "Corte 2", "Corte 3", "Final"]
            for idx in range(avance):
                corte_nombre = cortes_disponibles[idx]
                # Generar calificaciones realistas variadas (desde 1.5 a 5.0)
                nota = round(random.uniform(1.5, 5.0), 1)
                calificaciones.append((est_id, asig_cod, nota, corte_nombre))

    ins, omi = _insertar_lote(
        cursor, "matriculas",
        ("estudiante_id", "codigo_asignatura", "periodo"),
        matriculas,
    )
    print(f"  Insertados: {ins} | Omitidos: {omi}")

    # --- Calificaciones ---
    print("\n-- Calificaciones --")
    ins, omi = _insertar_lote(
        cursor, "calificaciones",
        ("estudiante_id", "codigo_asignatura", "nota", "corte"),
        calificaciones,
    )
    print(f"  Insertados: {ins} | Omitidos: {omi}")

    conn.commit()


# ================================================================
#  VERIFICACIÓN
# ================================================================

def verificar_datos(cursor):
    """Muestra un resumen de todas las tablas para confirmar la inserción."""

    tablas = [
        ("usuarios",        "SELECT COUNT(*) FROM usuarios"),
        ("estudiantes",     "SELECT COUNT(*) FROM estudiantes"),
        ("profesores",      "SELECT COUNT(*) FROM profesores"),
        ("asignaturas",     "SELECT COUNT(*) FROM asignaturas"),
        ("matriculas",      "SELECT COUNT(*) FROM matriculas"),
        ("calificaciones",  "SELECT COUNT(*) FROM calificaciones"),
    ]

    print("\n" + "=" * 45)
    print("  RESUMEN DE TABLAS")
    print("=" * 45)
    print(f"  {'Tabla':<20} {'Registros':>10}")
    print("-" * 45)

    for nombre_tabla, sql in tablas:
        cursor.execute(sql)
        cantidad = cursor.fetchone()[0]
        print(f"  {nombre_tabla:<20} {cantidad:>10}")

    print("=" * 45)

    # Detalle de usuarios
    print("\n-- Detalle: Usuarios --")
    print(f"  {'ID':<4} {'Nombre':<25} {'Correo':<35} {'Rol'}")
    print("  " + "-" * 70)
    cursor.execute("SELECT id, nombre, correo_institucional, rol FROM usuarios")
    for fila in cursor.fetchall():
        print(f"  {fila[0]:<4} {fila[1]:<25} {fila[2]:<35} {fila[3]}")

    # Detalle de estudiantes
    print("\n-- Detalle: Estudiantes --")
    print(f"  {'ID':<8} {'Nombre':<25} {'Correo'}")
    print("  " + "-" * 55)
    cursor.execute("SELECT id, nombre, correo FROM estudiantes")
    for fila in cursor.fetchall():
        print(f"  {fila[0]:<8} {fila[1]:<25} {fila[2]}")

    # Detalle de profesores
    print("\n-- Detalle: Profesores --")
    print(f"  {'ID':<8} {'Nombre':<20} {'Departamento'}")
    print("  " + "-" * 45)
    cursor.execute("SELECT id, nombre, departamento FROM profesores")
    for fila in cursor.fetchall():
        print(f"  {fila[0]:<8} {fila[1]:<20} {fila[2]}")

    # Detalle de asignaturas
    print("\n-- Detalle: Asignaturas --")
    print(f"  {'Código':<10} {'Nombre':<20} {'Crd':>3} {'Profesor'}")
    print("  " + "-" * 50)
    cursor.execute("""
        SELECT a.codigo, a.nombre, a.creditos, COALESCE(p.nombre, 'Sin asignar')
        FROM asignaturas a
        LEFT JOIN profesores p ON a.profesor_id = p.id
    """)
    for fila in cursor.fetchall():
        print(f"  {fila[0]:<10} {fila[1]:<20} {fila[2]:>3} {fila[3]}")


# ================================================================
#  PUNTO DE ENTRADA
# ================================================================

def main():
    print("=" * 65)
    print("  PLATAFORMA DE MONITOREO ACADÉMICO - UNITEC")
    print("  Configuración de Base de Datos SQLite")
    print("=" * 65)

    # Crear la carpeta data_base si no existe
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    crear_tablas(conn, cursor)
    insertar_datos_prueba(conn, cursor)
    verificar_datos(cursor)

    conn.close()

    print(f"\n[LISTO] Base de datos configurada exitosamente.")
    print(f"        Archivo: {DB_PATH}")
    print(f"\n  Para ejecutar la app:  python app.py")


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    main()
