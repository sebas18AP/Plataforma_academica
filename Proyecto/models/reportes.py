# pyrefly: ignore [missing-import]
import plotly.graph_objects as go
from collections import defaultdict

class GestorReportes:
    """Genera reportes estadísticos y gráficos interactivos para la plataforma académica"""
    
    def __init__(self, sistema_academico):
        self.sistema = sistema_academico
    
    #  GRÁFICO 1: Distribución de Notas 
    def grafico_distribucion_notas(self):
        """Histograma con distribución de todas las calificaciones"""
        if not self.sistema.calificaciones:
            return self._grafico_vacio("No hay calificaciones registradas")
        
        notas = [c.nota_obtenida for c in self.sistema.calificaciones]
        
        fig = go.Figure(data=[
            go.Histogram(
                x=notas,
                nbinsx=10,
                marker_color='rgba(0, 123, 255, 0.7)',
                hovertemplate='<b>Rango:</b> %{x:.1f}<br><b>Cantidad:</b> %{y}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title='<b>Distribución de Calificaciones</b>',
            xaxis_title='Nota Obtenida',
            yaxis_title='Cantidad de Estudiantes',
            template='plotly_white',
            hovermode='x unified',
            height=400
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id='grafico_distribucion')
    
    #  GRÁFICO 2: Promedios por Estudiante 
    def grafico_promedios_estudiantes(self):
        """Gráfico de barras con promedios de cada estudiante"""
        if not self.sistema.estudiantes or not self.sistema.calificaciones:
            return self._grafico_vacio("No hay datos de estudiantes o calificaciones")
        
        datos = []
        for est in self.sistema.estudiantes:
            promedio = self.sistema.calcular_promedio_estudiante(est.identificacion)
            datos.append({
                'Estudiante': f"{est.nombre}",
                'ID': est.identificacion,
                'Promedio': promedio
            })
        
        # Ordenar por promedio descendente
        datos.sort(key=lambda x: x['Promedio'], reverse=True)
        
        nombres = [f"{d['Estudiante']}\n(ID: {d['ID']})" for d in datos]
        promedios = [d['Promedio'] for d in datos]
        
        # Colorear según aprobación
        colores = ['rgba(40, 167, 69, 0.8)' if p >= 3.0 else 'rgba(220, 53, 69, 0.8)' 
                   for p in promedios]
        
        fig = go.Figure(data=[
            go.Bar(
                x=nombres,
                y=promedios,
                marker_color=colores,
                hovertemplate='<b>%{x}</b><br>Promedio: %{y:.2f}<extra></extra>'
            )
        ])
        
        fig.add_hline(y=3.0, line_dash="dash", line_color="orange", 
                      annotation_text="Nota mínima (3.0)", annotation_position="right")
        
        fig.update_layout(
            title='<b>Promedio Académico por Estudiante</b>',
            yaxis_title='Promedio',
            template='plotly_white',
            hovermode='x unified',
            height=400,
            xaxis_tickangle=-45
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id='grafico_promedios_est')
    
    #  GRÁFICO 3: Promedios por Asignatura
    def grafico_promedios_asignaturas(self):
        """Gráfico de barras con promedios de cada asignatura"""
        if not self.sistema.asignaturas or not self.sistema.calificaciones:
            return self._grafico_vacio("No hay datos de asignaturas o calificaciones")
        
        datos = []
        for asig in self.sistema.asignaturas:
            promedio = self.sistema.calcular_promedio_asignatura(asig.codigo)
            datos.append({
                'Asignatura': asig.nombre,
                'Codigo': asig.codigo,
                'Promedio': promedio
            })
        
        # Ordenar por promedio descendente
        datos.sort(key=lambda x: x['Promedio'], reverse=True)
        
        nombres = [f"{d['Asignatura']}\n({d['Codigo']})" for d in datos]
        promedios = [d['Promedio'] for d in datos]
        
        fig = go.Figure(data=[
            go.Bar(
                x=nombres,
                y=promedios,
                marker_color='rgba(102, 51, 153, 0.7)',
                hovertemplate='<b>%{x}</b><br>Promedio: %{y:.2f}<extra></extra>'
            )
        ])
        
        fig.add_hline(y=3.0, line_dash="dash", line_color="orange",
                      annotation_text="Nota mínima (3.0)", annotation_position="right")
        
        fig.update_layout(
            title='<b>Promedio Académico por Asignatura</b>',
            yaxis_title='Promedio',
            template='plotly_white',
            hovermode='x unified',
            height=400,
            xaxis_tickangle=-45
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id='grafico_promedios_asig')
    
    #  GRÁFICO 4: Estado Aprobación 
    def grafico_aprobacion(self):
        """Gráfico de pastel: Aprobados vs Reprobados"""
        distribucion = self.sistema.obtener_distribucion_notas()
        
        if distribucion['Total_Calificaciones'] == 0:
            return self._grafico_vacio("No hay calificaciones registradas")
        
        labels = ['Aprobados', 'Reprobados']
        valores = [distribucion['Aprobados'], distribucion['Reprobados']]
        colores = ['rgba(40, 167, 69, 0.8)', 'rgba(220, 53, 69, 0.8)']
        
        fig = go.Figure(data=[
            go.Pie(
                labels=labels,
                values=valores,
                marker=dict(colors=colores),
                hovertemplate='<b>%{label}</b><br>Cantidad: %{value}<br>Porcentaje: %{percent}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title='<b>Distribución: Aprobados vs Reprobados</b>',
            template='plotly_white',
            height=400
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id='grafico_aprobacion')
    
    #  GRÁFICO 5: Comparación por Rango de Notas 
    def grafico_comparacion_rangos(self):
        """Gráfico con distribución por rangos de calificaciones"""
        if not self.sistema.calificaciones:
            return self._grafico_vacio("No hay calificaciones registradas")
        
        # Rangos: Deficiente (0-2), Regular (2-3), Bueno (3-4), Excelente (4-5)
        rangos = {
            'Deficiente (0-2)': 0,
            'Regular (2-3)': 0,
            'Bueno (3-4)': 0,
            'Excelente (4-5)': 0
        }
        
        for cal in self.sistema.calificaciones:
            nota = cal.nota_obtenida
            if nota < 2:
                rangos['Deficiente (0-2)'] += 1
            elif nota < 3:
                rangos['Regular (2-3)'] += 1
            elif nota < 4:
                rangos['Bueno (3-4)'] += 1
            else:
                rangos['Excelente (4-5)'] += 1
        
        colores = ['#dc3545', '#ffc107', '#17a2b8', '#28a745']
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(rangos.keys()),
                y=list(rangos.values()),
                marker_color=colores,
                hovertemplate='<b>%{x}</b><br>Cantidad: %{y}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title='<b>Distribución por Rangos de Calificaciones</b>',
            yaxis_title='Cantidad de Estudiantes',
            template='plotly_white',
            height=400
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id='grafico_rangos')
    
    #  Estadisticas resumen de esta:
    def obtener_estadisticas_generales(self):
        """Retorna estadísticas generales del sistema"""
        if not self.sistema.calificaciones:
            return {
                'total_estudiantes': len(self.sistema.estudiantes),
                'total_asignaturas': len(self.sistema.asignaturas),
                'total_calificaciones': 0,
                'promedio_general': 0,
                'nota_maxima': 0,
                'nota_minima': 0,
                'tasa_aprobacion': 0
            }
        
        notas = [c.nota_obtenida for c in self.sistema.calificaciones]
        distribucion = self.sistema.obtener_distribucion_notas()
        
        promedio_general = round(sum(notas) / len(notas), 2)
        tasa_aprobacion = round((distribucion['Aprobados'] / len(notas) * 100), 1) if notas else 0
        
        return {
            'total_estudiantes': len(self.sistema.estudiantes),
            'total_asignaturas': len(self.sistema.asignaturas),
            'total_calificaciones': len(self.sistema.calificaciones),
            'promedio_general': promedio_general,
            'nota_maxima': max(notas) if notas else 0,
            'nota_minima': min(notas) if notas else 0,
            'tasa_aprobacion': tasa_aprobacion,
            'aprobados': distribucion['Aprobados'],
            'reprobados': distribucion['Reprobados']
        }
    
    # UTILIDADES 
    def _grafico_vacio(self, mensaje):
        """Retorna un gráfico con mensaje vacío"""
        fig = go.Figure()
        fig.add_annotation(
            text=mensaje,
            showarrow=False,
            font=dict(size=16, color='gray')
        )
        fig.update_layout(
            title='',
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            height=300
        )
        return fig.to_html(include_plotlyjs='cdn')
