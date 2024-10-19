import os
import json
import statistics
import logging
import numpy as np
import pandas as pd

import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots

from dotenv import load_dotenv
import utils.constants as CONSTANTS

load_dotenv()
data_folder = os.getcwd()+'/utils/dashboards/data'

error_logger = logging.getLogger('error_logger')


#################################### VARIABLES GLOBALES #############################################
# Data source
with open(data_folder+'/Colombia.geo.json') as file:
    counties = json.load(file)

df_municipios = pd.read_excel(
    data_folder+'/region.xlsx', sheet_name='municipios_mat'
)
df_IES = pd.read_excel(data_folder+'/region.xlsx', sheet_name='IES_mat')
df_IES_des = pd.read_excel(data_folder+'/region.xlsx', sheet_name='IES_des')
df_dpto_IES = pd.read_excel(data_folder+'/region.xlsx', sheet_name='dpto_IES')
df_dpto_cob = pd.read_excel(data_folder+'/region.xlsx', sheet_name='dpto_cob')
df_dpto_des = pd.read_excel(data_folder+'/region.xlsx', sheet_name='dpto_des')
df_dpto_mat = pd.read_excel(data_folder+'/region.xlsx', sheet_name='dpto_mat')
df_dpto_mat_privado = pd.read_excel(
    data_folder+'/region.xlsx', sheet_name='dpto_mat_privado'
)
df_dpto_mat_oficial = pd.read_excel(
    data_folder+'/region.xlsx', sheet_name='dpto_mat_oficial'
)
df_dpto_mat_hombres = pd.read_excel(
    data_folder+'/region.xlsx', sheet_name='dpto_mat_hombres'
)
df_dpto_mat_mujeres = pd.read_excel(
    data_folder+'/region.xlsx', sheet_name='dpto_mat_mujeres'
)
df_dpto_grad = pd.read_excel(
    data_folder+'/region.xlsx', sheet_name='dpto_graduados'
)

dptos = []
for loc in counties['features']:
    dptos.append(str(loc['properties']['NOMBRE_DPT']))

############################################################### MAPA ####################################################################


def mapa(dpto, periodo):
    try:
        # Agregar las ubicaciones del geo json
        locs = []
        dptos = []
        for loc in counties['features']:
            if loc['properties']['NOMBRE_DPT'] == dpto:

                # Registrar el id del departamento
                loc['id'] = loc['properties']['NOMBRE_DPT']
                locs.append(loc['properties']['NOMBRE_DPT'])

                # Obtener las coordenadas de ese departamento
                coords = loc['geometry']['coordinates']

                while type(coords[0][0]) is list:
                    coords = coords[0]

                latitudes = []
                longitudes = []
                for c in coords:
                    try:
                        longitudes.append(c[0])
                        latitudes.append(c[1])
                    except Exception as e:
                        pass
                logitud, latitude = statistics.mean(
                    longitudes), statistics.mean(latitudes)

        # Dataframe del departamento
        df = pd.DataFrame({
            'dpto': [dpto],
            'IES': df_dpto_IES[df_dpto_IES['departamento'] == dpto]['cant_IES_2018'],
            'matricula': df_dpto_mat[df_dpto_mat['departamento'] == dpto][str(periodo)],
        })

        # Figure
        fig = go.Figure(
            px.choropleth_mapbox(
                data_frame=df,
                geojson=counties,
                locations=locs,
                custom_data=['dpto', 'IES', 'matricula'],
                color='dpto',
                color_discrete_map={
                    dpto: 'rgb(221, 239, 255)',
                },
                zoom=5.4,
                opacity=0.7,
                center={"lat": float(latitude), "lon": float(logitud)},
                mapbox_style="carto-positron",
            ))
        fig.update_traces(
            hovertemplate='<b>%{customdata[0]}</b><br>' +
            '<br>IES:         %{customdata[1]}' +
            '<br>Matricula:   %{customdata[2]}' +
            '<extra></extra> ',
            hoverlabel=dict(bgcolor='white'),
            marker=dict(
                line=dict(width=2, color='black'),
            ),
        )
        fig.update_layout(coloraxis_showscale=False, showlegend=False)

        # Añadir municipios
        municipios = df_municipios[df_municipios['departamento'] == dpto]
        municipios = municipios[['municipio',
                                 'latitud', 'longitud', str(periodo)]]

        # Generar tamaño de municipio dependiendo de su matricula para ese año
        municipios = municipios[municipios[str(periodo)] != 0]
        municipios = municipios.dropna()
        tercio = int(len(municipios[str(periodo)])/3)

        matriculas = list(municipios[str(periodo)])
        matriculas = sorted(matriculas, reverse=True)
        g1 = [matriculas.pop(matriculas.index(max(matriculas)))]
        g2 = matriculas[:tercio]
        g3 = matriculas[tercio:]

        sizes = np.zeros(len(municipios))
        for i, m in enumerate(municipios[str(periodo)]):
            if m in g3:
                sizes[i] = 4
            elif m in g2:
                sizes[i] = 8
            elif m in g1:
                sizes[i] = 22

        municipios['size'] = sizes
        municipios['text'] = ['<b>{}</b><br>{}'.format(nom, mat) for nom, mat in zip(
            municipios['municipio'], municipios[str(periodo)])]

        # Pintar municipios
        fig.add_trace(go.Scattermapbox(
            lat=municipios['latitud'],
            lon=municipios['longitud'],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=municipios['size'],
                color=CONSTANTS.colores[5],
                opacity=0.8,
            ),
            text=municipios['text'],
            hoverinfo='text',
        ))
        fig.update_layout(
            margin=dict(l=0, r=0, b=0, t=10, pad=0),
        )
        return fig
    except Exception as e:
        error_logger.error('EXCEPTION: '+str(e), exc_info=True)
        return None

############################################################### BARRAS ####################################################################


def barras(dpto):
    try:
        df = df_dpto_des[df_dpto_des['departamento']
                         == dpto].drop(['departamento'], axis=1)

        periods = list(df.columns)
        desertion = df[0:].values[0]
        retencion = [(1-d)*100 for d in desertion]

        minimo = min(retencion)*0.9 if min(retencion)*0.9 > 0 else 0
        maximo = max(retencion)*1.05 if max(retencion)*1.05 < 110 else 100

        fig = go.Figure(
            # Barras
            go.Scatter(
                x=periods,
                y=retencion,
                mode='lines+markers',
                name='Poblacion 17-21',
                marker=dict(
                    color='rgb(26, 118, 255)',
                    line=dict(color='#000000', width=2)
                ),
                text=retencion,
            ))
        fig.update_traces(
            hovertemplate='<b>%{y}%</b><br>Retencion<extra></extra> ',
            texttemplate='%{y} <b>%</b> ',
            textposition='top center',
            textfont=dict(
                color='rgb(186, 41, 41)'
            ),
        )
        fig.update_layout(
            plot_bgcolor='#fff',
            paper_bgcolor='#fff',
            xaxis=dict(
                showgrid=False,
                showline=True, linewidth=2, linecolor='black'
            ),
            yaxis=dict(
                title='% Retención',
                showgrid=False,
                showline=True, linewidth=2, linecolor='black',
                range=[minimo, maximo],
            ),
            legend=dict(
                x=0,
                y=1.0,
                bgcolor='rgba(255, 255, 255, 0)',
                bordercolor='rgba(255, 255, 255, 0)'
            ),
            barmode='group',
            bargap=0.5,
            bargroupgap=0.1,
            margin=dict(l=0, r=0, b=0, t=30, pad=0),
        )

        return fig
    except Exception as e:
        error_logger.error('EXCEPTION: '+str(e), exc_info=True)
        return None

############################################################### PASTEL ####################################################################


def pastel(dpto, periodo):
    try:
        matricula_total = df_dpto_mat[df_dpto_mat['departamento'] == dpto][str(
            periodo)].values[0]
        oficial = df_dpto_mat_oficial[df_dpto_mat_oficial['departamento'] == dpto][str(
            periodo)].values[0]
        privado = df_dpto_mat_privado[df_dpto_mat_privado['departamento'] == dpto][str(
            periodo)].values[0]

        df = pd.DataFrame({
            'tipo': ['Privada', 'Publica'],
            'porcentaje': [round((oficial/matricula_total)*100, 1), round((privado/matricula_total)*100, 1)],
            'cantidad': [oficial, privado],
        })

        fig = px.pie(
            df,
            values='cantidad',
            names='tipo',
            custom_data=['tipo', 'porcentaje', 'cantidad'],
            hole=.1,
        )
        fig.update_traces(
            hovertext=[
                '<b>{}:</b> <br>{}'.format(t, c) for t, c in zip(df['tipo'], df['cantidad'])],
            hovertemplate='%{text} matriculados <extra></extra> ',
            texttemplate='<b> %{customdata[1]} % </b>',
            textposition='inside',
            textfont=dict(
                color="white"
            ),
            pull=[0.15, 0],
            marker=dict(
                line=dict(color='#000000', width=2),
                colors=[CONSTANTS.colores[0], CONSTANTS.colores[1]],
            ),
            showlegend=False
        )
        fig.update_layout(
            margin=dict(l=0, r=0, b=0, t=0, pad=0),
        )

        return fig
    except Exception as e:
        error_logger.error('EXCEPTION: '+str(e), exc_info=True)
        return None

############################################################### BARRAS GENERO ####################################################################


def genero(dpto, periodo):
    try:
        matricula_total = df_dpto_mat[df_dpto_mat['departamento'] == dpto][str(
            periodo)].values[0]
        hombres = df_dpto_mat_hombres[df_dpto_mat_hombres['departamento'] == dpto][str(
            periodo)].values[0]
        mujeres = df_dpto_mat_mujeres[df_dpto_mat_mujeres['departamento'] == dpto][str(
            periodo)].values[0]

        df = pd.DataFrame({
            'sexo': ['Hombres', 'Mujeres'],
            'cantidad': [hombres, mujeres],
            'porcentaje': [round((hombres/matricula_total)*100, 1), round((mujeres/matricula_total)*100, 1)],
        })
        fig = px.bar(
            df,
            x='sexo',
            y='porcentaje',
            text='porcentaje',
            custom_data=['cantidad', 'sexo'],
        )
        fig.update_traces(
            hovertemplate='<b>%{customdata[0]}</b><br>matriculados <extra></extra> ',
            marker=dict(
                line=dict(color='#000000', width=2),
                color=[CONSTANTS.colores[0], CONSTANTS.colores[1]],
            ),
            texttemplate='<b>%{text} %</b>',
            textposition='inside',
            textfont=dict(
                color="white"
            )
        )

        fig.update_layout(
            plot_bgcolor='#fff',
            paper_bgcolor='#fff',
            xaxis=dict(
                showline=True,
                linewidth=2,
                linecolor='black',
                showgrid=False,
                showticklabels=True,
                title='',
                fixedrange=True,
            ),
            yaxis=dict(
                showline=False,
                showgrid=False,
                showticklabels=False,
                title='',
                range=[0, max(df['porcentaje']*1.5)],
                fixedrange=True,
            ),
            showlegend=False,
            bargap=0.4,
            margin=dict(l=0, r=0, b=0, t=0, pad=0),
        )
        return fig
    except Exception as e:
        error_logger.error('EXCEPTION: '+str(e), exc_info=True)
        return None

############################################################### INDICADORES DPTO ####################################################################


def agregar_indicador(anterior, actual, fig, i):
    fig.append_trace(go.Indicator(
        mode="number+delta",
        delta={'reference': anterior, 'relative': True, 'position': "bottom"},
        value=actual,
    ),
        row=1, col=i
    )
    return fig


def indicadores_dpto(dpto, periodo):
    try:

        periodo = int(periodo)

        df_des = df_dpto_des[df_dpto_des['departamento'] == dpto]
        df_cob = df_dpto_cob[df_dpto_cob['departamento'] == dpto]
        df_mat = df_dpto_mat[df_dpto_mat['departamento'] == dpto]
        df_grad = df_dpto_grad[df_dpto_grad['departamento'] == dpto]
        periods = list(df_cob.columns)

        variables_indicadores = [df_des, df_cob, df_mat, df_grad]

        # Crear conetenedor de sub graficos
        fig = make_subplots(
            column_titles=['Deserción', 'Cobertura',
                           'Matriculados', 'Graduados'],
            rows=1, cols=len(variables_indicadores),
            column_widths=[0.25, 0.25, 0.25, 0.25],
            specs=[[{"type": "indicator"}]*len(variables_indicadores)],
            horizontal_spacing=0.2,
        )

        # Funcion para agregar un indicador a la figura
        def agregar_indicador(anterior, actual, fig, i):
            fig.append_trace(go.Indicator(
                mode="number+delta",
                delta={'reference': anterior,
                       'relative': True, 'position': "bottom"},
                value=actual,
            ),
                row=1, col=i
            )
            return fig

        # TODO Arreglar esta funcion para Bogota
        # EXCEPTION: index 0 is out of bounds for axis 0 with size 0
        # Traceback (most recent call last):
        # File "D:\juaneschrome\UDEM\9no Semestre\Trabajo de Grado\Segundo Entregable\Aplicacion\web\utils\dashboards\region.py", line 367, in indicadores_dpto
        #     period_actual = df_var_ind[str(periodo)].values[0]*100
        # IndexError: index 0 is out of bounds for axis 0 with size 0

        # Agregar cada indicador por variable
        for i, df_var_ind in enumerate(variables_indicadores):
            period_actual = df_var_ind[str(periodo)].values[0]*100
            period_anterior = df_var_ind[str(
                periodo-1)].values[0]*100 if str(periodo-1) in periods else None
            fig = agregar_indicador(period_anterior, period_actual, fig, i+1)

        # Personalizar la grafica
        fig.update_layout(
            paper_bgcolor='#fff',
            plot_bgcolor='#fff',
            showlegend=False,
            margin=dict(l=0, r=0, t=30, b=0),
        )
        return fig
    except Exception as e:
        error_logger.error('EXCEPTION: '+str(e), exc_info=True)
        return None


############################################################### INDICADORES IES ####################################################################
# Funcion para agregar un REGISTRO de IES a la lista
def IES_row(data, fig, i, periods):

    # Mini Serie de tiempo
    fig.append_trace(go.Scatter(
        x=periods,
        y=data['matricula'],
        mode='markers+lines',
        marker=dict(
            color=CONSTANTS.colores[1],
        ),

    ), row=i, col=1)
    fig.update_traces(
        hovertemplate='%{x}<br><b>%{y}</b> matriculados<extra></extra>',
        row=i, col=1)
    fig.update_yaxes(
        showline=False,
        tickvals=[statistics.mean(data['matricula'])],
        ticktext=[data['IES'][0]+'   '],
        tickfont=dict(color='black'),
        # range=[ min(data['matricula'])*0.9 ,max(data['matricula'])*1.1 ],
        fixedrange=True,
        row=i, col=1,
    )
    fig.update_xaxes(
        showline=False,
        showticklabels=False,
        title="",
        fixedrange=True,
        row=i, col=1
    )

    # Indicador
    period_anterior = data.loc[len(data)-2, 'matricula']
    period_actual = data.loc[len(data)-1, 'matricula']
    fig.append_trace(go.Indicator(
        mode="delta",
        delta={'reference': period_anterior,
               'relative': True, 'position': "bottom"},
        value=period_actual,
    ),
        row=i, col=2
    )

    return fig


def indicadores_ies(dpto):
    try:
        df = df_IES[df_IES['departamento'] == dpto]

        periods = list(df.loc[:, '2010':'2018'].columns)
        IES = df['nombre']
        IES_sigla = ['<b>'+sigla+'</b>' for sigla in df['nombre_corto']]
        cant_ies = len(IES)

        matriculas = []
        for ies in IES:
            matricula_ies = df[df['nombre'] == ies].loc[:, '2010':'2018']
            matriculas.append(matricula_ies.values[0])

        # Arreglo con los datos de cada IES
        dfs = []
        for ies, m in zip(IES_sigla, matriculas):
            dfs.append(pd.DataFrame({
                'IES': [ies]*len(periods),
                'matricula': m,
            }))

        # Crear conetenedor de sub graficos
        fig = make_subplots(
            start_cell='top-left',
            column_titles=['', ''],
            rows=cant_ies, cols=2,
            column_widths=[0.87, 0.13],
            horizontal_spacing=0.0,
            vertical_spacing=0.0,
            specs=[[{"type": "scatter", 'l': 0, 'r': 0, 't': 0, 'b': 0}, {
                "type": "indicator", 'l': 0, 'r': 0, 't': 0, 'b': 0}]]*cant_ies,
        )

        # Recorrer arreglo de IES y agregar cada fila con graficos
        for i in range(cant_ies):
            fig = IES_row(dfs[i], fig, i+1, periods)

        # # Personalizar la grafica
        fig.update_layout(
            paper_bgcolor='#fff',
            plot_bgcolor='#fff',
            showlegend=False,
            margin=dict(l=0, r=0, t=30, b=0),
        )
        for annotation in fig['layout']['annotations']:
            annotation['font'] = dict(color='black')

        return fig, cant_ies
    except Exception as e:
        error_logger.error('EXCEPTION: '+str(e), exc_info=True)
        return None, None

############################################################################ BARRAS HORIZONTALES IES ##############################################################


def barras_ies(dpto, periodo):

    try:

        df = df_IES_des[df_IES_des['departamento'] == dpto]

        if len(df) < 1:
            return None

        df = df[['nombre_corto', str(periodo)]]
        cant_ies = len(df)

        df[str(periodo)] = df[str(periodo)].values*100
        retencion = [(100-d) for d in df[str(periodo)]]

        desertion = df[str(periodo)]

        minimo = min(desertion)*0.1 if min(desertion)*0.1 > 0 else 0
        maximo = max(desertion)*1.2 if max(desertion)*1.2 < 100 else 100

        df = df.sort_values(by=str(periodo))

        fig = go.Figure(go.Bar(
            x=df[str(periodo)],
            y=df['nombre_corto'],
            marker=dict(
                color=CONSTANTS.colores[0],
                line=dict(color='black', width=0.5)
            ),
            name='IES Departamento',
            orientation='h',
        ))

        fig.update_traces(
            texttemplate='<b>  %{x:0.0f}%</b>',
            hovertemplate='%{y}<br><b>%{x:.2f}%</b>  deserción<extra></extra>',
            textposition='outside',
            textfont=dict(
                size=25,
                color=CONSTANTS.colores[5]
            ),
        )

        fig.update_layout(
            plot_bgcolor='#fff',
            paper_bgcolor='#fff',
            bargap=0.5,
            bargroupgap=0.1,
            title='IES Departamento',
            yaxis=dict(
                showgrid=False,
                showline=False, linewidth=2, linecolor='black',
                tickfont=dict(color='black'),
                ticktext=[' <b>'+ies+'</b>  ' for ies in df['nombre_corto']],
                tickvals=df['nombre_corto'],
                fixedrange=True
            ),
            xaxis=dict(
                zeroline=False,
                showline=False,
                showticklabels=False,
                showgrid=False,
                fixedrange=True,
                range=[minimo, maximo]
            ),

            showlegend=False,
            margin=dict(l=0, r=0, t=0, b=0),
        )
        return fig
    except Exception as e:
        error_logger.error('EXCEPTION: '+str(e), exc_info=True)
        return None
