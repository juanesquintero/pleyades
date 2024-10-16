import utils.constants as CONSTANTS
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

import plotly.graph_objs as go
import plotly.express as px

import os
from dotenv import load_dotenv
load_dotenv()
data_folder = os.getcwd()+'/utils/tableros/data'


#################################### VARIABLES GLOBALES #############################################
inscripciones = pd.read_excel(
    data_folder+'/mundo.xlsx', sheet_name='inscripciones')
gastos = pd.read_excel(data_folder+'/mundo.xlsx', sheet_name='gastos')

periods = list(inscripciones.columns)
periods.pop(0)
periods.pop(0)

color_cluster_map = {
    'G Inf/I Alta':  CONSTANTS.colores[7],
    'G Sup/I Alta': '#adc4d1',
    'G Inf/I Baja': '#6ca4d3',
    'G Sup/I Baja': '#4c6c93'
}

# {
#     'G Inf/I Alta': CONSTANTS.colores[6],
#     'G Sup/I Alta': CONSTANTS.colores[7],
#     'G Inf/I Baja': CONSTANTS.colores[0],
#     'G Sup/I Baja': CONSTANTS.colores[1]
# }

# {
#     'G Inf/I Alta': '#fff',
#     'G Sup/I Alta': '#adc4d1',
#     'G Inf/I Baja': '#6ca4d3',
#     'G Sup/I Baja': '#4c6c93'
# }

########################################################################################## SERIES ###############################################################################################


def data_series(codigo):
    nombre = gastos[gastos['codigo_pais'] == codigo]['nombre_pais'].values[0]
    gastos_pais = gastos[gastos['codigo_pais'] == codigo].loc[:, '2008':'2018']
    inscrp_pais = inscripciones[inscripciones['codigo_pais']
                                == codigo].loc[:, '2008':'2018']
    data = pd.DataFrame({
        'codigo_pais': codigo,
        'nombre_pais': nombre,
        'periods': periods,
        'gastos': gastos_pais.values[0],
        'inscripciones': inscrp_pais.values[0],
    })
    return data


def series(df, y_variable, y_titulo, color):
    fig = px.line(
        df,
        x="periods",
        y=y_variable,
        color='codigo_pais',
        custom_data=['nombre_pais'],
        color_discrete_map={
          df['codigo_pais'][0]: color,
        },
    )

    for trace in fig.data:
        # trace.name = trace.name.split('_')[1]
        trace.mode = 'lines+markers'

    fig.update_traces(
        hovertemplate='<b>%{customdata[0]}</b><br>' +
        '<br>Gastos:   %{y:.2f}' +
        '<br>Año:      %{x} <extra></extra>',
        hoverlabel=dict(bgcolor='white'),
        marker=dict(
            size=5,
            line=dict(width=0.5, color='DarkSlateGrey'),
        ),
    )
    fig.update_layout(
        xaxis_title="Año",
        yaxis_title=y_titulo,
        font=dict(
            size=10
        ),
        margin=dict(l=0, r=0, b=0, t=10, pad=0),
        showlegend=False
    )
    fig.layout.plot_bgcolor = '#fff'
    fig.layout.paper_bgcolor = '#fff'

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#cccccc')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#cccccc')

    fig.update_xaxes(showline=True, linewidth=2, linecolor='black')
    fig.update_yaxes(showline=True, linewidth=2, linecolor='black')

    return fig


def series_pais(codigo_pais):
    df = data_series(codigo_pais)
    gastos = series(
        df, "gastos", "Gasto público <br>en Educación", CONSTANTS.colores[1])
    inscripciones = series(
        df, "inscripciones", "Inscripciones en<br>Educación Terciaria", CONSTANTS.colores[0])
    return gastos, inscripciones

########################################################################################## CLUSTERS ###############################################################################################


def grupos_clusters(data):
    # Escalar valores en ambos ejes de 0-1 para que ambos ejes influyan en la descision de clusters
    data['gastos'] = data['gastos'] / np.max(data['gastos'])
    data['inscripciones'] = data['inscripciones'] / \
        np.max(data['inscripciones'])

    # Algoritmo de clusters
    X = data[['gastos', 'inscripciones']]

    kmeans = KMeans(n_clusters=4)
    kmeans.fit(X)

    grupos = kmeans.predict(X)
    centros = kmeans.cluster_centers_

    return grupos


def data_clusters():
    # Sacar promedios de la ultima decada
    inscripciones['promedio'] = inscripciones.loc[:,
                                                  '2008':'2018'].mean(axis=1)
    gastos['promedio'] = gastos.loc[:, '2008':'2018'].mean(axis=1)

    # Conjunto para graficar
    data = pd.DataFrame({
        'nombre_pais': gastos['nombre_pais'],
        'codigo_pais': gastos['codigo_pais'],
        'gastos': gastos['promedio'],
        'inscripciones': inscripciones['promedio'],
    })
    # Eliminar nulos
    data.dropna(subset=['gastos', 'inscripciones'], how='any', inplace=True)

    # Eliminar valores atipicos
    q1 = data['gastos'].quantile(0.98)
    data = data[data['gastos'] < q1]

    q2 = data['inscripciones'].quantile(0.98)
    data = data[data['inscripciones'] < q2]

    grupos = grupos_clusters(data)

    colores = []

    for i in range(len(grupos)):
        c = grupos[i]
        if c == 0:
            colores.append('G Inf/I Alta')
        elif c == 1:
            colores.append('G Sup/I Alta')
        elif c == 2:
            colores.append('G Inf/I Baja')
        else:
            colores.append('G Sup/I Baja')

    data['categoria'] = colores

    return data


global df_clusters
df_clusters = data_clusters()


def clusters(data=df_clusters):

    fig = px.scatter(
        data,
        x="gastos",
        y="inscripciones",
        text="codigo_pais",
        custom_data=['codigo_pais', 'nombre_pais', 'gastos', 'inscripciones'],
        color='categoria',
        color_discrete_map=color_cluster_map,
    )

    fig.update_traces(
        # textposition='top center',
        textposition='middle center',
        textfont_size=7,
        texttemplate="<b>%{text}</b>",

        hovertemplate='<b>%{customdata[1]} (%{customdata[0]})</b><br>' +
        '<br>Gastos:           %{x:.2f}' +
        '<br>Inscripciones:  %{y:.2f} <extra></extra>',
        marker=dict(
            size=17,
            line=dict(width=1, color='DarkSlateGrey'),
            opacity=0.8,
        ),
    )

    fig.update_layout(
        xaxis_title="Gasto público  en Educación",
        yaxis_title="Inscripciones en<br>Educación Terciaria",
        font=dict(
            size=10,
        ),
        margin=dict(l=0, r=0, b=0, t=10, pad=0),
        showlegend=False,
    )

    fig.update_xaxes(showline=True, linewidth=2, linecolor='black')
    fig.update_yaxes(showline=True, linewidth=2, linecolor='black')

    fig.layout.plot_bgcolor = '#fff'
    fig.layout.paper_bgcolor = '#fff'

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#cccccc')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#cccccc')

    return fig


########################################################################################## MAPA MUNDIAL ###############################################################################################

def mapa(data=df_clusters):
    grupos = grupos_clusters(data)

    fig = px.choropleth(
        data_frame=data,
        locations='codigo_pais',
        scope="world",
        custom_data=['codigo_pais', 'nombre_pais', 'gastos', 'inscripciones'],
        color='categoria',
        color_discrete_map=color_cluster_map,
    )

    fig.update_traces(
        hovertemplate='<b>%{customdata[1]} (%{customdata[0]})</b><br>' +
        '<br>Gastos:           %{customdata[2]:.2f}' +
        '<br>Inscripciones:  %{customdata[3]:.2f}<extra></extra>',
        hoverlabel=dict(bgcolor='white'),
    )

    fig.update_geos(projection_type="natural earth")

    fig.layout.coloraxis.showscale = False

    fig.update_layout(
        geo=dict(
            showframe=False,
            projection_type='equirectangular'
        ),
        font=dict(
            size=10,
        ),
        margin=dict(l=0, r=0, b=0, t=0, pad=0),
        showlegend=False,
    )

    return fig
