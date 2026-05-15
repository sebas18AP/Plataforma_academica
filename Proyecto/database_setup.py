"""
database_setup.py
-----------------
Script de inicialización de la base de datos SQLite para la
Plataforma de Monitoreo Académico - UNITEC
Facultad de Ingeniería Eléctrica

Ejecutar UNA SOLA VEZ para crear y poblar la base de datos.
"""

import sqlite3
import os

# --- Ruta de la base de datos ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data_base", "academico.db")


def crear_base_de_datos():
    """Crea la base de datos y todas las tablas necesarias."""
    print(f"[INFO] Creando base de datos en: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # --- Tabla de usuarios ---
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
    conn.commit()
    return conn, cursor


def insertar_datos_prueba(conn, cursor):
    """Inserta los 5 estudiantes de prueba de Ingeniería Eléctrica."""

    estudiantes = [
        (
            "Carlos Andrés Pérez",
            "c.perez@unitec.edu.co",
            "unitec2026",
            "Estudiante",
        ),
        (
            "Valentina Gómez",
            "v.gomez@unitec.edu.co",
            "unitec2026",
            "Estudiante",
        ),
        (
            "Jorge Luis Rodríguez",
            "j.rodriguez@unitec.edu.co",
            "unitec2026",
            "Estudiante",
        ),
        (
            "Mariana Lucía Toro",
            "m.toro@unitec.edu.co",
            "unitec2026",
            "Estudiante",
        ),
        (
            "Felipe Santiago Ruiz",
            "f.ruiz@unitec.edu.co",
            "unitec2026",
            "Estudiante",
        ),
    ]

    insertados = 0
    omitidos = 0

    for nombre, correo, contrasena, rol in estudiantes:
        try:
            cursor.execute(
                """
                INSERT INTO usuarios (nombre, correo_institucional, contrasena, rol)
                VALUES (?, ?, ?, ?)
                """,
                (nombre, correo, contrasena, rol),
            )
            insertados += 1
            print(f"  [+] Insertado: {nombre} ({correo})")
        except sqlite3.IntegrityError:
            # El correo ya existe (UNIQUE constraint), se omite
            omitidos += 1
            print(f"  [!] Omitido (ya existe): {correo}")

    conn.commit()
    print(f"\n[RESUMEN] Insertados: {insertados} | Omitidos: {omitidos}")


def verificar_datos(cursor):
    """Muestra todos los usuarios registrados para confirmar la inserción."""
    print("\n[VERIFICACIÓN] Usuarios en la base de datos:")
    print("-" * 65)
    print(f"{'ID':<4} {'Nombre':<25} {'Correo':<35} {'Rol'}")
    print("-" * 65)

    cursor.execute("SELECT id, nombre, correo_institucional, rol FROM usuarios")
    filas = cursor.fetchall()

    for fila in filas:
        print(f"{fila[0]:<4} {fila[1]:<25} {fila[2]:<35} {fila[3]}")

    print("-" * 65)
    print(f"Total de usuarios: {len(filas)}")


def main():
    print("=" * 65)
    print("  PLATAFORMA DE MONITOREO ACADÉMICO - UNITEC")
    print("  Configuración de Base de Datos SQLite")
    print("=" * 65)

    conn, cursor = crear_base_de_datos()
    insertar_datos_prueba(conn, cursor)
    verificar_datos(cursor)
    conn.close()

    print("\n[LISTO] Base de datos configurada exitosamente.")
    print(f"        Archivo: {DB_PATH}")


if __name__ == "__main__":
    main()
