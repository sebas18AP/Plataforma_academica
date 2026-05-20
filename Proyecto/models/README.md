# Capa del Modelo - Lógica y Base de Datos (`models/`)

Esta carpeta contiene la definición de todas las entidades de dominio y la lógica de negocio central del sistema. Implementa el patrón **Model** (Modelo) dentro del patrón arquitectónico MVC.

## 📌 Propósito

Su propósito es encapsular la lógica de negocio, las reglas matemáticas, los cálculos y la persistencia de datos. Es el único componente del sistema autorizado para interactuar directamente con la base de datos SQLite a través de consultas SQL.

## 📂 Contenido del Directorio

- **`persona.py`**: Clase base abstracta `Persona` que encapsula los atributos comunes como identificación, nombre, correo y rol.
- **`estudiante.py`**: Clase `Estudiante` que hereda de `Persona`. Modela a los alumnos matriculados.
- **`profesor.py`**: Clase `Profesor` que hereda de `Persona`. Modela al personal docente.
- **`asignaturas.py`**: Estructura que modela las materias disponibles (código, nombre, créditos).
- **`matricula.py`**: Relación de vinculación entre los estudiantes y las asignaturas matriculadas.
- **`calificacion.py`**: Registro individual de notas por cortes y materia.
- **`reportes.py`**: Clase `GestorReportes` que consolida estadísticas globales y detecta estudiantes en situación de riesgo académico.
- **`sistema.py`**: Clase central `SistemaAcademico` que gestiona las conexiones SQLite, la autenticación, los historiales académicos, el boletín oficial de calificaciones y el simulador interactivo de notas.

## ⚠️ Reglas y Restricciones de `models/`

1. **Aislamiento de Interfaz (Prohibido HTML/JS)**: Está estrictamente prohibido incluir cualquier código de visualización HTML, bloques de JavaScript o variables específicas de Jinja en esta carpeta. Toda la información debe ser procesada y devuelta como estructuras nativas de Python (diccionarios, listas, booleanos, tuplas).
2. **Consultas SQL Centralizadas**: Todas las operaciones relacionales de lectura o escritura en SQLite (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) deben ejecutarse única y exclusivamente en los archivos de esta carpeta.
3. **Cálculos Matemáticos Rigurosos**: Cualquier fórmula o ponderación de notas (como los porcentajes de cortes del simulador de $30\%$, $20\%$, $20\%$ y $30\%$) debe programarse y validarse aquí.

---

*Garantizando un núcleo de software limpio, desacoplado y de alta mantenibilidad.*
