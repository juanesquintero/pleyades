import logging
import numpy as np
import pandas as pd

import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots

import utils.tableros.data_ies as Data

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

# Funcion para agregar un grafico por periodo


def barras_period(df, p, fig, i, azules):

    fig.append_trace(go.Bar(
        x=df['desertor'],
        y=df['semestre'],
        marker_color=azules,
        marker=dict(
            # color= azules[i-1],
            line=dict(color='black', width=2)
        ),
        orientation='h',
        texttemplate='%{x}',
        hovertemplate='<b>Periodo:</b> {}'.format(
            p)+'<br><b>Nivel:</b> %{y}<br><b>Desertor(es):</b> %{x}<extra></extra>',
        textposition='outside',

        textfont=dict(
            size=30,
            color='rgb(30, 75, 131)'
        )
    ), row=1, col=i)

    try:
        maximo = max(df['desertor']*1.3)
    except Exception as e:
        maximo = 0

    # if list(df['desertor']) == list(np.zeros(len(df['desertor']))):
    #     df = pd.DataFrame({
    #     'desertor': [],
    #     'semestre': []
    # })
    if list(df['desertor']) == list(np.zeros(len(df['desertor']))):
        maximo = 5

    if i == 1:
        fig.update_yaxes(dict(
            showgrid=False,
            showline=True, linewidth=1, linecolor='black',
            tickfont=dict(color='black', size=15),
            tickvals=df['semestre'],
            ticktext=[
                'Nivel <b>{}</b>               '.format(s) for s in df['semestre']],
        ), row=1, col=i)
    else:
        fig.update_yaxes(dict(
            showgrid=False,
            showline=True, linewidth=1, linecolor='black',
            showticklabels=False,
        ), row=1, col=i)

    fig.update_xaxes(dict(
        zeroline=False,
        showline=False,
        showticklabels=False,
        showgrid=False,
        range=[0, maximo]
    ), row=1, col=i)

    return fig

# CLASE DE GRAFICOS PARA PROGRAMA


class Programa:

    def __init__(self, periodo: int, programa: int, periods: list):
        self.df_IES = Data.get_IES_programa(programa)
        self.df_ESTUDIANTES_total = Data.get_students_programa(programa)
        self.df_ESTUDIANTES = self.df_ESTUDIANTES_total.query(
            "REGISTRO == '{}'".format(periodo))
        self.periodos_list = periods
        self.periodo = periodo
        self.programa = programa

        # Obtener data anterior
        index_period_actual = self.periodos_list.index(self.periodo)
        self.data_actual = Data.get_IES_period_programa(periodo, programa)

        if 0 <= index_period_actual <= len(self.periodos_list):
            period_anterior = self.periodos_list[index_period_actual-1]
            if Data.check_IES_period_programa(period_anterior, programa):
                self.data_anterior = Data.get_IES_period_programa(
                    period_anterior, programa)
            else:
                self.data_anterior = self.data_actual
        else:
            self.data_anterior = self.data_actual

    ############################################################### INDICADORES PROGRAMA ####################################################################
    def indicadores(self):
        try:
            # Dataframe del programa
            data_anterior = self.data_anterior
            data_actual = self.data_actual

            variables_nombre = ['insc_total',
                                'admi_total', 'mat_total', 'desercion']
            variables_indicadores = []
            for v in variables_nombre:
                variables_indicadores.append(
                    [data_anterior[v][0], data_actual[v][0]])
            cant_indicadores = len(variables_indicadores)

            # Crear conetenedor de sub graficos
            fig = make_subplots(
                column_titles=['Inscritos', 'Admitidos',
                               'Matriculados', 'Deserción'],
                rows=1, cols=cant_indicadores,
                column_widths=[1/cant_indicadores]*cant_indicadores,
                specs=[[{"type": "indicator"}]*cant_indicadores],
                horizontal_spacing=0.2,
            )

            # Agregar cada indicador por variable
            for i, var in enumerate(variables_indicadores):
                period_anterior = var[0]
                period_actual = var[1]
                fig = agregar_indicador(
                    period_anterior, period_actual, fig, 1, i+1, 'number+delta')

            # Personalizar la grafica
            fig.update_layout(
                paper_bgcolor='#fff',
                plot_bgcolor='#fff',
                showlegend=False,
                margin=dict(l=10, r=15, b=0, t=30, pad=0),
            )

            return fig
        except Exception as e:
            error_logger.error('EXCEPTION: '+str(e), exc_info=True)
            return None

    ############################################################### RADIAL MATRICULA ####################################################################
    def radial(self):
        try:
            # Dataframe del programa
            data_ies = self.df_IES

            data = data_ies.dropna(subset=['periodo', 'mat_total'], axis=0)
            periodos_list = sorted(
                data['periodo'].unique(),  reverse=True)[:12]
            periods = [int(p) for p in periodos_list]
            matriculas = []
            for i, p in enumerate(periods):
                mat = data.query("periodo == '{}'".format(p))[
                    'mat_total'].values[0]
                matriculas.append(mat)

            df_matricula_radial = pd.DataFrame({
                'periodo': periods,
                'matricula': matriculas,
                'teta': np.linspace(10, 350, num=len(periods))
            })
            azules = []
            i = 0
            for _ in periods:
                if i == len(px.colors.sequential.Blues):
                    i = 0
                azules.append(px.colors.sequential.Blues[i])
                i += 1

            fig = go.Figure(go.Barpolar(
                r=df_matricula_radial['matricula'],
                theta=df_matricula_radial['teta'],
                text=df_matricula_radial['periodo'],
                hovertext=df_matricula_radial['matricula'],
                hovertemplate='<b>%{text}</b><br>Matricula: %{hovertext}<extra></extra>',
                width=[10]*len(periods),
                marker_color=azules,
                marker_line_color="black",
                marker_line_width=2,
                opacity=0.8
            ))

            fig.update_layout(
                template=None,
                polar=dict(
                    radialaxis=dict(
                        range=[0, max(matriculas)*1.03],
                        showticklabels=False,
                        ticks=''
                    ),
                    angularaxis=dict(
                        showticklabels=True,
                        ticktext=periods,
                        tickvals=df_matricula_radial['teta'],
                        ticks='inside',
                    )
                ),
                margin=dict(l=0, r=0, b=30, t=30, pad=0),
            )
            return fig
        except Exception as e:
            error_logger.error('EXCEPTION: '+str(e), exc_info=True)
            return None

    ############################################################### PASTEL ESTRATOS ####################################################################
    def pastel(self):
        try:
            if len(self.df_ESTUDIANTES) <= 0:
                raise Exception('No hay estudiantes')
            data = self.df_ESTUDIANTES.dropna(
                subset=['estrato_residencia'], axis=0)
            data = data['estrato_residencia']
            data = pd.DataFrame(data)
            data = data.sort_values(by='estrato_residencia', ascending=False)
            estratos_str = sorted(data['estrato_residencia'].unique())

            # Quitar el ESTRATO de la columna
            estratos = []
            for e in estratos_str:
                if any(char.isdigit() for char in e):
                    estratos.append(int(e.replace('ESTRATO ', '')))

            estudiantes = [len(data.query(
                "estrato_residencia == 'ESTRATO {}'".format(e))) for e in estratos]
            # TODO organizar el orden de los estratos
            estratos_str = ['Estrato {}'.format(e) for e in estratos]
            if len(estratos) <= 0:
                raise Exception('No hay estratos')

            fig = px.pie(
                values=estudiantes,
                names=estratos_str,
                opacity=1,
                hole=.25,
                color_discrete_sequence=px.colors.sequential.ice[3:],
            )
            # Personalizar la grafica
            fig.update_layout(
                paper_bgcolor='#fff',
                plot_bgcolor='#fff',
                showlegend=True,
                margin=dict(l=0, r=0, t=10, b=5, pad=0),
                legend={'traceorder': 'grouped'}
            )
            fig.update_traces(
                hovertemplate='<b>%{label}</b>' +
                '<br>%{value} <extra></extra>',
                marker=dict(line=dict(color='black', width=2)),
                pull=[0.05]*len(estratos_str)
            )
            return fig
        except Exception as e:
            error_logger.error('EXCEPTION: '+str(e), exc_info=True)
            return None

    ############################################################### BARRAS DESERTORES ####################################################################
    def barras(self):
        try:
            # Dataframe del programa
            # TODO hacer el filtro por codigo o nombre de programa en la tabla VWDATADESERCION
            data = pd.DataFrame(self.df_ESTUDIANTES_total.loc[:, [
                                'semestre', 'REGISTRO', 'desertor']])
            data[['desertor']] = data[['desertor']
                                      ].replace(['NO', 'SI'], [0, 1])
            data = data.groupby(['REGISTRO', 'semestre'], as_index=False).sum()

            periods = list(data['REGISTRO'].unique())

            azules = []
            i = 0
            for _ in periods:
                if i == len(px.colors.sequential.Blues):
                    i = 0
                azules.append(px.colors.sequential.Blues[i])
                i += 1
            azules = list(reversed(azules))

            # Crear conetenedor de sub graficos
            fig = make_subplots(
                start_cell='top-left',
                column_titles=list(map(str, periods)),
                rows=1, cols=len(periods),
                # horizontal_spacing = 0.3,
            )

            # Definir el mayor numeto de niveles-semestres para ese programa en todos los periods
            niveles = []
            for p in periods:
                data_period = data.query("REGISTRO == '{}'".format(p))
                niveles.append(len(data_period))
            cant_niveles = max(niveles)

            if cant_niveles <= 0:
                raise Exception('No hay niveles')

            # Recorrer los periods y reliazar las graficas
            for i, p in enumerate(periods):
                data_period = data.query("REGISTRO == '{}'".format(p))
                data_period = data_period.sort_values(
                    by='semestre', ascending=True)
                data_period = data_period.head(cant_niveles)

                # llenar los demas semestres para que queden con el maximo de todos
                if len(data_period) < cant_niveles:

                    for j in range(1, cant_niveles+1):
                        # Semestre-Nivel existe en el data frame
                        if not (j <= len(data_period) and j in list(data_period['semestre'])):
                            data_period = data_period.append(pd.DataFrame(
                                [[j, p, 0]], columns=['semestre', 'REGISTRO', 'desertor']))

                    data_period = data_period.sort_values(
                        by='semestre', ascending=True)

                fig = barras_period(data_period, p, fig, i+1, azules)

            espaciado = float('0.'+str(abs(10-cant_niveles)))
            if (espaciado < 0.1 or cant_niveles > 10):
                espaciado = 0.1
            if (espaciado > 0.9):
                espaciado = 0.9

            fig.update_layout(
                plot_bgcolor='#fff',
                paper_bgcolor='#fff',
                bargap=espaciado,
                # bargroupgap=0.1,
                # title='<b>Desercion Niveles</b>',
                showlegend=False,
                margin=dict(l=0, r=0, b=15, t=30)
            )

            return fig, cant_niveles, len(periods)

        except Exception as e:
            error_logger.error('EXCEPTION: '+str(e), exc_info=True)
            return None, None, None
