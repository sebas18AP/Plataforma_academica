# Capa de la Vista - Plantillas y Frontend (`templates/`)

Esta carpeta alberga la interfaz de usuario (UI) y la experiencia de usuario (UX) de la plataforma académica. Representa la **Vista** (View) en el patrón de diseño MVC.

## 📌 Propósito

Su función es presentar la información académica a los estudiantes y profesores de manera clara, visualmente atractiva y responsiva. Utiliza plantillas de HTML5 renderizadas dinámicamente en el servidor a través del motor Jinja2 de Flask, complementado con estilos visuales modernos mediante Tailwind CSS.

## 📂 Contenido del Directorio

- **`login.html`**: Formulario de acceso unificado con validación de credenciales.
- **`dashboard.html`**: Panel principal adaptativo. Muestra estadísticas y notas con Consejero Virtual para estudiantes, y acceso a herramientas administrativas para profesores.
- **`simulador.html`**: Interfaz interactiva de proyección de notas. Contiene los deslizadores dinámicos que recalculan calificaciones definitivas simuladas en tiempo real.
- **`boletin.html`**: Plantilla oficial de calificaciones diseñada para su impresión física o guardado en formato PDF.
- **`calificar.html`**: Formulario interactivo con buscador en vivo para que los docentes registren notas de los cortes correspondientes.
- **`matricular.html`**: Formulario de asociación de asignaturas a estudiantes con buscador integrado en vivo.
- **`reportes.html`**, **`reporte_riesgo.html`**, **`reporte_individual.html`**: Paneles e informes estadísticos que detallan la situación de alumnos en riesgo académico.
- **`editar_perfil.html`**: Formulario de actualización de datos de usuario.
- **`registro.html`**: Formulario de creación de cuentas de acceso.

## ⚠️ Reglas y Restricciones de `templates/`

1. **Uso Exclusivo del Español**: Todos los textos visibles para el usuario (títulos, etiquetas, placeholders, botones y mensajes de alerta) deben estar estrictamente redactados en un español natural, profesional e institucional.
2. **Prohibición de Lógica SQL y Lógica de Negocio Pesada**: Las plantillas no deben contener sentencias SQL ni realizar cálculos lógicos complejos. Solo pueden utilizar condicionales (`if`) o bucles (`for`) provistos por Jinja2 para pintar la información que el controlador le inyecta previamente.
3. **Mantenimiento CSS y Clases**: Para asegurar la consistencia del diseño y evitar la sobrecarga visual, se debe hacer uso de las clases utilitarias de Tailwind CSS y mantener las reglas de diseño fluido (Mobile-First).

---

*Ofreciendo una experiencia interactiva fluida, accesible y moderna.*
