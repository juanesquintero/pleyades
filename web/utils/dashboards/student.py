import json
import logging
import pandas as pd

import plotly.graph_objs as go
from plotly.subplots import make_subplots
import utils.constants as CONSTANTS

# Data source
import utils.dashboards.data_ies as Data

error_logger = logging.getLogger('error_logger')

#################################### VARIABLES GLOBALES #############################################
colores = CONSTANTS.colores

#################################### FUNCIONES GLOBALES #############################################


def students_program(program: str):
    try:
        data = Data.get_students_program(program)
        data = data[['documento', 'name_completo']]
        students = data.drop_duplicates()
        return students.to_dict(orient='records')
    except Exception as e:
        error_logger.error('EXCEPTION: '+str(e), exc_info=True)
        return None


class Student:

    def __init__(self, identificacion, program=None,  period=None, ):
        self.df_ESTUDIANTE = Data.get_students_documento(identificacion)
        self.identificacion = identificacion
        self.period = period
        self.program = program
        self.info = None
        self.periods_estudiante = None
        self.programs_estudiante = None
        self.promedios_estudiante = None

    # Funcion para agregar un indicador a la figura
    def get_estudiante(self,):
        try:
            # Dataframe del program
            data = self.df_ESTUDIANTE
            programs_student_filter = json.loads(data.drop_duplicates(
                subset=['idprograma']).to_json(orient='records'))
            self.programs_estudiante = [
                {'idprograma': p['idprograma'], 'program': p['program']} for p in programs_student_filter]
            self.periods_student_todos = list(data['REGISTRO'].unique())
            self.periods_estudiante = list(data['REGISTRO'].unique())

            # Filtrar Program
            if self.program:
                data = data.query("idprograma == '{}'".format(
                    self.program['idprograma']))
                self.periods_estudiante = list(data['REGISTRO'].unique())

            # Filtrar Periodo
            if self.period:
                data = data.query("REGISTRO == '{}'".format(self.period))

            # Si hay Registro repetido
            if len(data) > 1:
                data = data[0:1]

            self.info = data.to_dict(orient='records')[0]

            # Setear perioodo y program si no lo hay
            if not self.period:
                self.period = self.info['REGISTRO']
            if not self.program:
                self.program = {
                    'idprograma': self.info['idprograma'],
                    'program': self.info['program']
                }

            self.info['fecha_nacimiento'] = str(
                self.info['fecha_nacimiento'][:-8])

            return self.info, self.periods_estudiante, self.programs_estudiante

        except Exception as e:
            error_logger.error('EXCEPTION: '+str(e), exc_info=True)
            return None, [], []

    def progreso_creditos_reprobados(self,):
        try:
            creditos_totals = self.info['creditos_program']
            creditos_reprobados = self.info['creditos_reprobados_acum']
            creditos_reprobados_porcentaje = float(
                creditos_reprobados/creditos_totals)
            fig = go.Figure(go.Bar(
                y=[''],
                x=[creditos_reprobados],
                name='Asignaturas   ',
                marker_color=colores[2],
                marker=dict(
                    line=dict(color='black', width=2)
                ),
                orientation='h',
                texttemplate='   <b>{:.0%}</b>'.format(
                    creditos_reprobados_porcentaje),
                hovertemplate='<b>{}</b> reprobados<br><b>{}</b> totals<extra></extra>'.format(
                    creditos_reprobados, creditos_totals),
                textposition='outside',
                textfont=dict(
                    size=20,
                    color='black'
                ),
            ))

            if creditos_reprobados_porcentaje > 0.9:
                maximo = creditos_totals*1.2
            else:
                maximo = creditos_totals

            fig.update_xaxes(dict(
                showline=True, linewidth=1, linecolor='black',
                showgrid=False,
                range=[0, maximo]
            ))

            fig.update_layout(
                plot_bgcolor='#f5f5f5',
                paper_bgcolor='#fff',
                showlegend=False,
                margin=dict(l=0, r=0, b=15, t=10),
                font=dict(
                    size=8
                ),
            )
            return fig
        except Exception as e:
            error_logger.error('EXCEPTION: '+str(e), exc_info=True)

    def progreso_creditos_aprobados(self,):
        try:
            creditos_totals = self.info['creditos_program']
            creditos_aprobados = self.info['creditos_aprobados_acum']
            creditos_aprobados_porcentaje = creditos_aprobados/creditos_totals
            fig = go.Figure(go.Bar(
                y=[''],
                x=[creditos_aprobados],
                name='Créditos    ',
                marker_color=colores[1],
                marker=dict(
                    line=dict(color='black', width=2)
                ),
                orientation='h',
                texttemplate='   <b>{:.0%}</b>'.format(
                    creditos_aprobados_porcentaje),
                hovertemplate='<b>{}</b> aprobados<br><b>{}</b> totals<extra></extra>'.format(
                    creditos_aprobados, creditos_totals),
                textposition='outside',
                textfont=dict(
                    size=20,
                    color='black'
                )
            ))

            if creditos_aprobados_porcentaje > 0.9:
                maximo = creditos_totals*1.2
            else:
                maximo = creditos_totals

            fig.update_xaxes(dict(
                showline=True, linewidth=1, linecolor='black',
                showgrid=False,
                range=[0, maximo]
            ))

            fig.update_layout(
                plot_bgcolor='#f5f5f5',
                paper_bgcolor='#fff',
                showlegend=False,
                margin=dict(l=0, r=0, b=15, t=10),
                font=dict(
                    size=8
                ),
            )

            return fig
        except Exception as e:
            error_logger.error('EXCEPTION: '+str(e), exc_info=True)

    def set_promedios(self,):
        try:
            # Dataframe del program
            data = self.df_ESTUDIANTE
            promedios = {}
            # Para get los promeios de los diferentes programs
            # for p in self.programs_estudiante:
            #     estu = data.query("program == '{}'".format(p))
            #     estu = estu.sort_values(by=['REGISTRO'], ascending=[True])
            #     promedios[p] = {
            #         # 'REGISTRO': [str(e) for e in estu['REGISTRO']],
            #         'REGISTRO': list(estu['REGISTRO']),
            #         'promedio': list(estu['promedio_semestre'])
            #     }
            estu = data.query("idprograma == '{}'".format(
                self.program['idprograma']))
            estu = estu.sort_values(by=['REGISTRO'], ascending=[True])
            promedios[self.program['idprograma']] = {
                'program': self.program['program'],
                'REGISTRO': list(estu['REGISTRO']),
                'promedio': list(estu['promedio_semestre'])
            }
            self.promedios_estudiante = promedios
        except Exception as e:
            error_logger.error('EXCEPTION: '+str(e), exc_info=True)
            self.promedios_estudiante = {}
            self.promedio_acumulado_total = None

    def serie_promedio(self,):
        try:
            self.set_promedios()

            fig = make_subplots(specs=[[{"secondary_y": False}]])

            # Serie por promedios de un program
            for i, program in enumerate(self.promedios_estudiante.keys()):
                name_program = self.promedios_estudiante[program]['program']
                del self.promedios_estudiante[program]['program']
                df = pd.DataFrame(self.promedios_estudiante[program])

                fig.add_trace(go.Scatter(
                    x=df['REGISTRO'],
                    y=df['promedio'],
                    name=name_program,
                    mode='markers+lines+text',
                    text=list(df['promedio']),
                    textposition='top center',
                    texttemplate='%{text}',
                    textfont=dict(color=colores[i]),
                    marker=dict(
                        color=colores[i],
                    )
                ))

            fig.update_traces(
                hovertemplate='Promedio:   %{y:.2f}' +
                '<br>Período:      %{x} <extra></extra>',
                marker=dict(
                    size=10,
                    line=dict(width=1, color='white'),
                ),
            )
            fig.update_layout(
                font=dict(
                    size=10
                ),
                margin=dict(l=0, r=0, b=0, t=15, pad=0),
                showlegend=True,
                legend=dict(
                    x=0,
                    y=0,
                    bgcolor='rgba(255, 255, 255, 0)',
                    bordercolor='rgba(255, 255, 255, 0)'
                ),
                xaxis=dict(
                    title='Período',
                    showline=True, linewidth=2, linecolor='black', showgrid=True, gridwidth=1, gridcolor='#cccccc',
                    type='category', categoryorder='array', categoryarray=sorted(self.periods_student_todos)
                ),
                yaxis=dict(
                    title='Promedio',
                    showline=True, linewidth=2, linecolor='black',
                    showgrid=True, gridwidth=1, gridcolor='#cccccc', range=[-1.5, 6]

                )
            )
            fig.layout.plot_bgcolor = '#fff'
            fig.layout.paper_bgcolor = '#fff'

            return fig
        except Exception as e:
            error_logger.error('EXCEPTION: '+str(e), exc_info=True)
            return None
