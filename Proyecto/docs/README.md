# Centro de Documentación y Guías del Proyecto (`docs/`)

Este directorio funciona como el repositorio centralizado de manuales, diagramas, esquemas y recursos de documentación técnica del sistema académico SIGMA de UNITEC.

## 📌 Propósito

Su propósito es guiar al equipo de desarrollo y administración en la instalación, arranque, mantenimiento y flujo operativo de la aplicación. Almacena instructivos de infraestructura y guías rápidas del desarrollador.

## 📂 Contenido del Directorio

- **`README.md`**: El presente manual de inicio rápido de Windows e instructivo de despliegue.

## 🚀 Inicio Rápido en Windows

Para desplegar localmente la plataforma en un entorno Windows de manera automatizada:

1. Abre la consola de comandos de tu sistema en la carpeta principal `Proyecto`.
2. Ejecuta el comando o haz doble clic en `start_app.bat`.
3. El script creará un entorno virtual de Python en el directorio `.venv` (si no existe previamente).
4. Instalará las herramientas necesarias (`pip`, `setuptools`, `wheel`) y actualizará las librerías a partir de `requirements.txt`.
5. Ejecutará el inicializador de la base de datos `database_setup.py` para asegurar que las tablas y semillas de prueba estén cargadas.
6. Iniciará la aplicación Flask localmente en el puerto `5000` con `py app.py`.

> [!NOTE]
> La primera ejecución puede tardar unos momentos mientras se descargan las librerías de internet. Las ejecuciones posteriores iniciarán el servidor en cuestión de segundos de manera transparente.

## ⚠️ Reglas y Restricciones de `docs/`

1. **Exclusividad Documental**: Esta carpeta está reservada única y exclusivamente para archivos de texto enriquecido, markdown (`.md`), imágenes de flujos, diagramas de arquitectura y manuales de usuario. Está prohibido almacenar scripts funcionales o archivos ejecutables aquí.
2. **Formato Estándar**: Todos los documentos que se agreguen a esta carpeta deben redactarse en formato GitHub Flavored Markdown (GFM) y utilizar una estructura jerárquica clara con títulos (`#`, `##`, `###`).

---

*Facilitando la inducción y el entendimiento técnico del sistema.*
