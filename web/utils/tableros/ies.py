import utils.tableros.data_ies as Data
import numpy as np
import pandas as pd
import json
import statistics
from itertools import chain

import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import utils.constants as CONSTANTS

import logging
error_logger = logging.getLogger('error_logger')

# Data source

#################################### FUNCIONES GLOBALES #############################################
# Funcion para agregar un indicador a la figura


def agregar_indicador(anterior, actual, fig, i, j, mode):
    if anterior == 0:
        anterior = actual/2
    fig.append_trace(go.Indicator(
        mode=mode,
        delta={'reference': anterior, 'relative': True, 'position': "bottom"},
        value=actual,
    ),
        row=i, col=j
    )
    return fig


def crear_indicador(data, variable, i, j, fig, tipo):
    # Indicador
    period_anterior = data.loc[len(
        data)-2, variable]*100 if len(data)-2 > 0 else None
    period_actual = data.loc[len(data)-1, variable] * \
        100 if len(data)-1 > 0 else None

    # if period_actual == period_anterior:
    #     period_actual = None
    #     period_anterior = None

    if period_anterior == 0:
        period_anterior = period_actual/2

    fig.append_trace(go.Indicator(
        mode=tipo,
        delta={'reference': period_anterior,
               'relative': True, 'position': "bottom"},
        value=period_actual,
    ),
        row=i, col=j
    )
    return fig

# Funcion para agregar un REGISTRO de programas a la lista de graficos


def miniserie_programa_row(data, fig, i, dict_periods):
    try:
        x_periods = []
        for p in data['periodo']:
            x_periods.append(dict_periods[str(p)])

        periods = [str(p) for p in data['periodo']]

        # Mini Serie de tiempo
        fig.append_trace(go.Scatter(
            x=x_periods,
            y=data['desercion'],
            mode='lines+markers',
            marker=dict(
                color=CONSTANTS.colores[1],
            ),
            text=periods,
            hovertemplate='<br>(%{text} , %{y:.1%}) <extra></extra>',
        ), row=i, col=1)
        fig.update_yaxes(
            showline=False,
            tickvals=[statistics.mean(data['desercion'])],
            ticktext=[
                '<b>{}</b>       '.format(data['programa_nombre_corto'][0])],
            tickfont=dict(
                color='black',
                # size=15
            ),
            fixedrange=True,
            row=i, col=1
        )
        fig.update_xaxes(
            showline=False,
            showticklabels=False,
            title="",
            fixedrange=True,
            range=[-1, 20],
            row=i, col=1
        )

        try:
            # Indicador
            period_anterior = data.loc[len(data)-2, 'desercion']
            period_actual = data.loc[len(data)-1, 'desercion']
        except Exception as e:
            period_actual = None
            period_anterior = None

        if period_actual == period_anterior:
            period_actual = None
            period_anterior = None

        if period_anterior == 0:
            period_anterior = 1
            period_actual = 2

        fig.append_trace(go.Indicator(
            mode="delta",
            delta={'reference': period_anterior,
                   'relative': True, 'position': "bottom"},
            value=period_actual,
        ),
            row=i, col=2
        )

        return fig
    except Exception as e:
        error_logger.error('EXCEPTION: '+str(e), exc_info=True)
        return None

# Funcion para agregar un REGISTRO de programas a la lista de graficos


def indicadores_programa_row(data, fig, i):
    x = [0]
    # Nombre Programa
    fig.append_trace(go.Scatter(
        x=x,
        y=x,
        hoverinfo='skip',
        marker=dict(
            color='#fff'
        ),
    ), row=i, col=1)
    fig.update_yaxes(
        showline=False,
        tickvals=x,
        ticktext=['<b>{}</b>       '.format(data['programa_nombre_corto'][0])],
        tickfont=dict(color='black'),
        fixedrange=True,
        row=i, col=1
    )
    fig.update_xaxes(
        showline=False,
        showticklabels=False,
        title="",
        fixedrange=True,
        row=i, col=1
    )

    fig = crear_indicador(data, 'mat_hombre', i, 2, fig, 'number+delta')
    fig = crear_indicador(data, 'mat_mujer', i, 3, fig, 'number+delta')
    fig = crear_indicador(data, 'mat_total', i, 4, fig, 'number+delta')
    fig = crear_indicador(data, 'desercion', i, 5, fig, 'number+delta')

    return fig


# CLASE DE GRAFICOS PARA IES
class IES:
    def __init__(self, periodo: int):
        self.df_IES = Data.get_IES_period(periodo)
        self.periodos_list = Data.get_periods()
        self.periodo = periodo

        # Obtener data anterior
        index_period_actual = self.periodos_list.index(self.periodo)
        self.data_actual = Data.get_IES_total_data(int(self.periodo))

        if 0 <= index_period_actual <= len(self.periodos_list):
            period_anterior = self.periodos_list[index_period_actual-1]
        else:
            period_anterior = periodo

        self.data_anterior = Data.get_IES_total_data(int(period_anterior))

        self.programas_period_actual = Data.get_programas_by_period(periodo)
        self.programas_period_anterior = Data.get_programas_by_period(
            period_anterior)

    ############################################################### INDICADORES IES ####################################################################

    def indicadores1(self,):
        try:
            period_actual = self.periodo

            data_anterior = self.data_anterior
            data_actual = self.data_actual

            variables_nombre = ['insc_total', 'admi_total', 'mat_total']
            variables_indicadores = []
            for v in variables_nombre:
                variables_indicadores.append(
                    [data_anterior[v][0], data_actual[v][0]])

            cant_indicadores = len(variables_indicadores)
            # Crear conetenedor de sub graficos
            fig = make_subplots(
                column_titles=['Inscritos', 'Admitidos', 'Matriculados'],
                rows=1, cols=cant_indicadores,
                column_widths=[1/cant_indicadores*0.5]*cant_indicadores,
                specs=[[{"type": "indicator"}]*cant_indicadores],
            )

            # Agregar cada indicador por variable
            for j, var in enumerate(variables_indicadores):
                period_anterior = var[0]
                period_actual = var[1]
                fig = agregar_indicador(
                    period_anterior, period_actual, fig, 1, j+1, 'number+delta')

            # Personalizar la grafica
            fig.update_layout(
                paper_bgcolor='#fff',
                plot_bgcolor='#fff',
                showlegend=False,
                margin=dict(l=0, t=30, r=10, b=0),
            )
            return fig
        except Exception as e:
            error_logger.error('EXCEPTION: '+str(e), exc_info=True)
            return None

    def indicadores2(self,):
        try:
            # Crear conetenedor de sub graficos
            fig = make_subplots(
                start_cell='top-left',
                column_titles=['Programas', 'Egresados'],
                rows=1, cols=2,
                column_widths=[0.5, 0.5],
                specs=[[{"type": "indicator"}, {"type": "indicator"}]],
            )

            programas_period_actual, egresados_period_actual = len(
                self.programas_period_actual), self.data_actual['egresados'][0]
            programas_period_anterior, egresados_period_anterior = len(
                self.programas_period_anterior), self.data_anterior['egresados'][0]

            fig = agregar_indicador(
                programas_period_anterior, programas_period_actual, fig, 1, 1, 'number')
            fig = agregar_indicador(
                egresados_period_anterior, egresados_period_actual, fig, 1, 2, 'number')

            # Personalizar la grafica
            fig.update_layout(
                paper_bgcolor='#fff',
                plot_bgcolor='#fff',
                showlegend=False,
                margin=dict(l=0, t=30, r=0, b=0),
            )
            return fig
        except Exception as e:
            error_logger.error('EXCEPTION: '+str(e), exc_info=True)
            return None

    ############################################################### BARRAS ####################################################################
    def barras(self):
        try:
            # Agrupar por Facultades
            data_facultades = self.df_IES.dropna(subset=['facultad'], axis=0)

            data_facultades = data_facultades[[
                'facultad', 'programa', 'programa_nombre_corto', 'mat_total', 'admi_total', 'insc_total', 'mat_nuevos_total']]
            data_facultades = data_facultades.groupby(
                ['facultad'], as_index=False).sum()
            data_facultades = data_facultades.sort_values(
                by=['admi_total', 'insc_total', 'mat_nuevos_total'], ascending=[True, True, True])

            # Create figure with secondary y-axis
            fig = make_subplots(specs=[[{"secondary_y": True}]])

            # BARRAS
            # Inscritos
            fig.add_trace(go.Bar(
                x=data_facultades['facultad'],
                y=data_facultades['insc_total'],
                name='Inscritos',
                marker=dict(
                    line=dict(color='#000000', width=2),
                    color=CONSTANTS.colores[0],
                    opacity=0.9
                )
            ),
                secondary_y=False)
            # Admitidos
            fig.add_trace(go.Bar(
                x=data_facultades['facultad'],
                y=data_facultades['admi_total'],
                name='Admitidos',
                marker=dict(
                    line=dict(color='#000000', width=2),
                    color=CONSTANTS.colores[1],
                    opacity=0.9
                )
            ),
                secondary_y=False)
            # Matriculados
            fig.add_trace(go.Bar(
                x=data_facultades['facultad'],
                y=data_facultades['mat_nuevos_total'],
                name='Matriculados',
                marker=dict(
                    line=dict(color='#000000', width=2),
                    color=CONSTANTS.colores[6],
                    opacity=0.9
                )
            ),
                secondary_y=False)
            # SERIES
            # Tasa Admitidos/Matriculados
            tasa = []
            for a, m in zip(data_facultades['admi_total'], data_facultades['mat_nuevos_total']):
                try:
                    tasa.append(round(a/m*100, 1))
                except Exception as e:
                    tasa.append(0)

            fig.add_trace(go.Scatter(
                x=data_facultades['facultad'],
                y=tasa,
                name='Tasa de absorción',
                mode='markers+lines+text',
                text=tasa,
                textposition='top center',
                texttemplate='%{text} %',
                textfont=dict(color=CONSTANTS.colores[5]),
                marker=dict(
                    color=CONSTANTS.colores[5],
                ),
            ),
                secondary_y=True)

            # Personalizar figura
            fig.update_layout(
                plot_bgcolor='#fff',
                paper_bgcolor='#fff',
                xaxis=dict(
                    title='Facultades',
                    # tickfont_size=14,
                    showticklabels=False,
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='#fff',
                    showline=True, linewidth=2, linecolor='black'
                ),
                yaxis=dict(
                    title='Estudiantes',
                    # titlefont_size=16,
                    # tickfont_size=14,
                    showgrid=True, gridwidth=1, gridcolor='#fff',
                    showline=True, linewidth=2, linecolor='black',
                    range=[0, max(chain(data_facultades['mat_nuevos_total'],
                                  data_facultades['insc_total'], data_facultades['admi_total']))*1.4],
                ),
                legend=dict(
                    # x=0,
                    # y=1,
                    bgcolor='rgba(255, 255, 255, 0)',
                    bordercolor='rgba(255, 255, 255, 0)'
                ),
                barmode='group',
                # gap between bars of adjacent location coordinates.
                bargap=0.25,
                # gap between bars of the same location coordinate.
                bargroupgap=0,
                margin=dict(l=0, t=0, r=0, b=0),
                font=dict(size=10)
            )

            fig.update_yaxes(
                showline=False,
                showgrid=False,
                showticklabels=False,
                title='',
                fixedrange=True,
                range=[max(tasa)*2*-1, max(tasa)*2.5],
                secondary_y=True)

            fig.update_traces(
                hovertemplate='<b>%{x}</b>' +
                '<br>%{y} <extra></extra>',
                # hoverlabel = dict(bgcolor='white'),
            )
            return fig
        except Exception as e:
            error_logger.error('EXCEPTION: '+str(e), exc_info=True)
            return None

    ############################################################### PASTEL ####################################################################
    def pastel(self,):
        try:
            # Agrupar por Facultades
            data_facultades = self.df_IES
            data_facultades = data_facultades.dropna(
                subset=['facultad'], axis=0)

            data_facultades = data_facultades[[
                'facultad', 'programa', 'programa_nombre_corto', 'mat_total', 'admi_total', 'insc_total', 'mat_nuevos_total']]
            data_facultades = data_facultades.groupby(
                ['facultad'], as_index=False).sum()
            data_facultades = data_facultades.sort_values(
                by=['admi_total', 'insc_total', 'mat_nuevos_total'], ascending=[True, True, True])

            fig = px.pie(
                values=data_facultades['mat_total'],
                names=data_facultades['facultad'],
                color_discrete_sequence=px.colors.sequential.ice[3:],
                hole=.3
            )
            # Personalizar la grafica
            fig.update_layout(
                paper_bgcolor='#fff',
                plot_bgcolor='#fff',
                # showlegend=True,
                showlegend=False,
                margin=dict(l=0, r=0, t=5, b=5, pad=0),
            )
            fig.update_traces(
                hovertemplate='<b>%{label}</b>' +
                '<br>%{value} <extra></extra>',
                marker=dict(line=dict(color='black', width=2))
            )
            for annotation in fig['layout']['annotations']:
                annotation['font'] = dict(color='black')
            return fig
        except Exception as e:
            error_logger.error('EXCEPTION: '+str(e), exc_info=True)
            return None

    ############################################################### LISTA INDICADORES PROGRAMAS ####################################################################
    def indicadores_programas(self):
        try:

            period_actual = self.periodo

            # Programas
            data = self.df_IES.dropna(subset=['facultad'], axis=0)
            data = data.sort_values(
                by=['periodo', 'mat_total'], ascending=[False, False])
            list_programas = self.programas_period_actual
            cant_programas = len(list_programas)

            # Crear conetenedor de sub graficos
            fig = make_subplots(
                start_cell='top-left',
                column_titles=['', 'Hombres', 'Mujeres', 'Total', 'Desercion'],
                rows=cant_programas, cols=5,
                column_widths=[0, 0.25, 0.25, 0.25, 0.25],
                specs=[[{"type": "scatter"}, {"type": "indicator"}, {"type": "indicator"}, {
                    "type": "indicator"}, {"type": "indicator"}]]*cant_programas,
            )

            # Recorrer arreglo de programas y agregar cada fila con graficos
            cont = 0
            for i, p in enumerate(list_programas):
                # Filtrar por programa
                data = Data.get_programa(p['idprograma']).reset_index()

                # Filtrar por periodo actual
                data = data.sort_values(by=['periodo']).reset_index()
                data_period_index = data.query(
                    "periodo == '{}'".format(period_actual))

                # Verificar si existe REGISTRO para ese periodo
                if len(data_period_index) > 0:
                    period_index = data_period_index.index[0]

                    # Verificar si existe dato en el periodo anterior
                    if period_index-1 in data['index']:
                        period_anterior = data.loc[period_index-1, 'periodo']
                        # Obtener registros de los dos ultimos periods a partir del indicado
                        data_period_index = data.query(
                            "periodo == '{}' | periodo == '{}'".format(period_actual, period_anterior))
                        fig = indicadores_programa_row(data, fig, cont+1)
                        cont += 1

            # Personalizar la grafica
            fig.update_layout(
                paper_bgcolor='#fff',
                plot_bgcolor='#fff',
                showlegend=False,
                margin=dict(l=0, r=0, t=30, b=0, pad=0),
            )
            for annotation in fig['layout']['annotations']:
                annotation['font'] = dict(color='black')

            if cant_programas <= 0:
                return None, None

            return fig, cant_programas

        except Exception as e:
            error_logger.error('EXCEPTION: '+str(e), exc_info=True)
            return None

    ############################################################### LISTA MINI SERIES PROGRAMAS ####################################################################
    def miniseries_programas(self):
        try:
            # Programas
            data = self.df_IES.dropna(subset=['facultad'], axis=0)
            list_programas = self.programas_period_actual
            cant_programas = len(list_programas)

            # Periodos
            list_periods = self.periodos_list

            dict_periods = {}
            for i, p in enumerate(list_periods):
                dict_periods[str(p)] = i

            # Retencion

            # Crear conetenedor de sub graficos
            fig = make_subplots(
                start_cell='top-left',
                column_titles=['', ''],
                rows=cant_programas, cols=2,
                column_widths=[0.5, 0.1],
                specs=[[{"type": "scatter"}, {"type": "indicator"}]] *
                cant_programas,
            )

            # Recorrer arreglo de programas y agregar cada fila con graficos
            for i, p in enumerate(list_programas):
                data = Data.get_programa(p['idprograma'])
                data = data[['periodo', 'programa',
                             'programa_nombre_corto', 'idprograma', 'desercion']]
                data = data.dropna().reset_index()
                # data['periodo'] = data['periodo'].astype(str)
                fig = miniserie_programa_row(data, fig, i+1, dict_periods)

            # Personalizar la grafica
            fig.update_layout(
                paper_bgcolor='#fff',
                plot_bgcolor='#fff',
                showlegend=False,
                margin=dict(l=0, r=0, t=30, b=0, pad=0),
            )
            for annotation in fig['layout']['annotations']:
                annotation['font'] = dict(color='black')

            if cant_programas <= 0:
                return None, None

            return fig, cant_programas

        except Exception as e:
            error_logger.error('EXCEPTION: '+str(e), exc_info=True)
            return None, None
