# Sistema de Gestión Académica (SIGMA) - UNITEC

Este directorio es la raíz de la plataforma académica **SIGMA** (Sistema Integrado de Gestión y Monitoreo Académico) de UNITEC. Centraliza el arranque del servidor web de Flask, la base de datos SQLite persistente y la configuración de inicialización del sistema.

## 📌 Propósito

La raíz del proyecto sirve como punto de orquestación principal para la aplicación web. Aquí se definen los puntos de entrada, los scripts de arranque rápido, los archivos de requerimientos y se mantiene el archivo central de la base de datos relacional.

## 📂 Contenido del Directorio

- **`app.py`**: El enrutador y controlador principal (Controller) del patrón MVC. Maneja las sesiones de usuario, controla la protección de rutas por roles mediante decoradores y renderiza las vistas.
- **`database_setup.py`**: Script encargado de inicializar la estructura relacional de la base de datos.
- **`academico.db`**: Base de datos SQLite persistente del sistema. Contiene las tablas de estudiantes, profesores, asignaturas, matrículas y calificaciones.
- **`requirements.txt`**: Listado de dependencias necesarias de Python.
- **`start_app.bat`**: Script de arranque automatizado para sistemas operativos Windows.
- **`Procfile`**: Configuración de despliegue para servidores en la nube (como Heroku).

## ⚠️ Reglas y Restricciones de la Raíz

1. **Código Fuente Limpio**: Este espacio debe contener únicamente archivos de configuración global y controladores principales. Toda la lógica de negocio debe delegarse al directorio `models/`.
2. **Ubicación de Base de Datos**: El archivo `academico.db` debe residir estrictamente en este directorio raíz para evitar conflictos de rutas relativas durante la ejecución de los módulos.
3. **Control de Modificaciones**: Cualquier cambio en las dependencias de Python debe quedar documentado y actualizado en `requirements.txt`.

---

*Desarrollado para la Facultad de Ingeniería Eléctrica de UNITEC.*
