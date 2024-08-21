import utils.constants as CONSTANTS
import numpy as np
import pandas as pd
import json
import statistics

import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots

import os
from dotenv import load_dotenv
load_dotenv()
data_folder = os.getcwd()+'/utils/tableros/data'


#################################### VARIABLES GLOBALES #############################################
# Data source
with open(data_folder+'/Colombia.geo.json') as file:
    counties = json.load(file)

df_nacional = pd.read_excel(data_folder+'/pais.xlsx', sheet_name='nacional')
df_dpto_mat = pd.read_excel(data_folder+'/pais.xlsx', sheet_name='dpto_mat')
df_dpto_cob = pd.read_excel(data_folder+'/pais.xlsx', sheet_name='dpto_cob')
df_dpto_des = pd.read_excel(data_folder+'/pais.xlsx', sheet_name='dpto_des')

########################################################################################## MAPA ###############################################################################################


def mapa(periodo):
    # Agregar las ubicaciones del geo json
    locs = []
    for loc in counties['features']:
        loc['id'] = loc['properties']['NOMBRE_DPT']
        locs.append(loc['properties']['NOMBRE_DPT'])

    periodo = str(periodo)

    # Crear el df para el pais en un periodo especifico
    df = pd.DataFrame({
        'departamento': df_dpto_mat['departamento'],
        'matricula': df_dpto_mat.loc[:, periodo],
        'cobertura': [round(cob*100, 2) for cob in df_dpto_cob.loc[:, periodo]],
        'desercion': [round(des*100, 2) for des in df_dpto_des.loc[:, periodo]],
    })
    df = df.fillna('')
    # Figure
    fig = go.Figure(
        px.choropleth_mapbox(
            data_frame=df,
            geojson=counties,
            locations=locs,
            zoom=4.0,
            center={"lat": 4.200000, "lon": -73.1000000},
            custom_data=['departamento', 'matricula',
                         'cobertura', 'desercion'],
            color='matricula',
            color_continuous_scale='Blues',
            range_color=[min(df['matricula']), max(df['matricula'])],
            mapbox_style="carto-positron",
        ))

    fig.update_traces(
        hovertemplate='<b>%{customdata[0]}</b><br>' +
        '<br>Matrícula:      <b>%{customdata[1]}</b>' +
        '<br>Cobertura:    <b>%{customdata[2]}%</b>' +
        '<br>Deserción:    <b>%{customdata[3]}%</b>',
        hoverlabel=dict(bgcolor='white'),
        marker=dict(
            line=dict(width=1, color='black'),
        ),
        showlegend=False,
    )
    fig.update_layout(
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=10,
            pad=0
        ),
    )
    return fig

########################################################################################## BARRAS Matricula años ###############################################################################################


def barras():
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Barras
    fig.add_trace(go.Bar(
        x=df_nacional['periodo'],
        y=df_nacional['matricula_total'],
        name='Matrícula Total',
        marker=dict(
            line=dict(color='#000000', width=0.5),
            color=CONSTANTS.colores[0],
            opacity=0.9
        )
    ),
        secondary_y=False)

    fig.add_trace(go.Bar(
        x=df_nacional['periodo'],
        y=df_nacional['poblacion_17_21'],
        name='Población 17-21',
        marker=dict(
            line=dict(color='#000000', width=0.5),
            color=CONSTANTS.colores[6],
            opacity=0.9
        )
    ),
        secondary_y=False)
    # Serie
    fig.add_trace(go.Scatter(
        x=df_nacional['periodo'],
        y=df_nacional['cobertura'],
        name='Cobertura',
        mode='markers+lines+text',
        text=[round(cob*100, 1) for cob in df_nacional['cobertura']],
        textposition='top center',
        texttemplate='%{text} %',
        textfont=dict(color=CONSTANTS.colores[5]),
        marker=dict(
            color=CONSTANTS.colores[5],
        )
    ),
        secondary_y=True)

    fig.update_layout(
        plot_bgcolor='#fff',
        paper_bgcolor='#fff',
        xaxis=dict(
            title='Año',
            showgrid=False,
            showline=True, linewidth=2, linecolor='black'
        ),
        yaxis=dict(
            title='Estudiantes',
            showgrid=False,
            showline=True, linewidth=2, linecolor='black',
            range=[0, max(df_nacional['poblacion_17_21'])*1.8],
        ),
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        barmode='group',
        bargap=0.3,
        bargroupgap=0,
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=10,
            pad=0
        ),
    )

    fig.update_yaxes(
        range=[min(df_nacional['cobertura'])*0.7,
               max(df_nacional['cobertura'])*1.2],
        showline=False,
        showgrid=False,
        showticklabels=False,
        title='',
        fixedrange=True, secondary_y=True)

    fig.update_traces(
        hovertemplate='<b>%{x}</b>' +
        '<br>%{y}<extra></extra>',
    )

    return fig


########################################################################################## TORTA sector ###############################################################################################
def pastel(periodo):

    df_filtrado = df_nacional[df_nacional['periodo'] == int(periodo)]

    privada = df_filtrado.loc[:, 'matricula_sector_privado'].values[0]
    oficial = df_filtrado.loc[:, 'matricula_sector_oficial'].values[0]
    total = df_filtrado.loc[:, 'matricula_total'].values[0]
    df = pd.DataFrame({
        'tipo': ['Privada', 'Pública'],
        'cantidad': [privada, oficial],
        'porcentaje': [round(privada/total*100, 1), round(oficial/total*100, 1)]
    })

    fig = px.pie(
        df,
        values='cantidad',
        names='tipo',
        custom_data=['tipo', 'porcentaje', 'cantidad',],
        hole=.1,
    )
    fig.update_traces(
        hovertext=df['cantidad'],
        hovertemplate='<b> %{text} </b> matriculados',
        texttemplate='<b> %{customdata[0]}<br></b> %{customdata[1]} % ',
        textposition='inside',
        textfont=dict(
            color="white",
            size=12,
        ),
        pull=[0.15, 0],
        marker=dict(
            line=dict(color='#000000', width=1),
            colors=[CONSTANTS.colores[0], CONSTANTS.colores[1]],
        ),
        showlegend=False,
    )
    fig.update_layout(
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0,
            pad=0
        ),
    )

    return fig

########################################################################################## BARRAS genero ###############################################################################################


def genero(periodo):
    df_filtrado = df_nacional[df_nacional['periodo'] == int(periodo)]
    mujeres = df_filtrado.loc[:, 'matricula_mujeres'].values[0]
    hombres = df_filtrado.loc[:, 'matricula_hombres'].values[0]
    total = df_filtrado.loc[:, 'matricula_total'].values[0]

    df = pd.DataFrame({
        'sexo': ['Hombres', 'Mujeres'],
        'cantidad': [hombres, mujeres],
        'porcentaje': [round(hombres/total*100, 1), round(mujeres/total*100, 1)]
    })

    fig = px.bar(
        df,
        x='sexo',
        y='porcentaje',
        text='porcentaje',
        custom_data=['cantidad', 'sexo'],
    )
    fig.update_traces(
        hovertemplate='<b> %{customdata[0]}</b> %{customdata[1]}',
        marker=dict(
            line=dict(color='#000000', width=1),
            color=[CONSTANTS.colores[0], CONSTANTS.colores[1]],
        ),
        texttemplate='%{text} %',
        textposition='inside',
        textfont=dict(
            color="white",
            size=15,
        )
    )
    fig.update_layout(
        bargap=0.4,
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
            range=[0, 100],
            fixedrange=True,
        ),
        showlegend=False,
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0,
            pad=0
        ),
    )

    # fig.show(config={'displayModeBar': False})
    return fig


########################################################################################## INDICADORES ###############################################################################################
def agregar_indicador(anterior, actual, fig, i):
    fig.append_trace(go.Indicator(
        mode="number+delta",
        delta={'reference': anterior, 'relative': True, 'position': "bottom"},
        value=actual,
    ),
        row=1, col=i
    )
    return fig


def indicadores(periodo):

    periodo = int(periodo)
    df = df_nacional[['periodo', 'desercion', 'graduandos_total']]

    # Crear conetenedor de sub graficos
    fig = make_subplots(
        column_titles=['Deserción', 'Graduados'],
        rows=1, cols=2,
        column_widths=[0.5, 0.5],
        specs=[[{"type": "indicator"}, {"type": "indicator"}]],
        horizontal_spacing=0.2,
    )

    # Desercion
    periodo_actual = df[df['periodo'] == periodo]['desercion'].values[0]*100
    periodo_anterior = df[df['periodo'] == periodo-1]['desercion'].values[0] * \
        100 if not (periodo == min(df['periodo'])) else None

    fig = agregar_indicador(periodo_anterior, periodo_actual, fig, 1)

    # Graduados
    periodo_actual = df[df['periodo'] == periodo]['graduandos_total'].values[0]
    periodo_anterior = df[df['periodo'] == periodo -
                          1]['graduandos_total'].values[0] if not (periodo == min(df['periodo'])) else None

    fig = agregar_indicador(periodo_anterior, periodo_actual, fig, 2)

    # Personalizar la grafica
    fig.update_layout(
        paper_bgcolor='#fff',
        plot_bgcolor='#fff',
        showlegend=False,
        margin=dict(l=0, r=0, t=20, b=0, pad=0),
    )

    return fig


def indicadores2(periodo):
    periodo = int(periodo)

    df = df_nacional[['periodo', 'inscripcion', 'admicion', 'matricula_total']]

    # Crear conetenedor de sub graficos
    fig = make_subplots(
        column_titles=['Inscritos', 'Admitidos', 'Matriculados'],
        rows=1, cols=3,
        column_widths=[0.33, 0.33, 0.33],
        specs=[[{"type": "indicator"}, {
            "type": "indicator"}, {"type": "indicator"}]],
        horizontal_spacing=0.13,
    )

    # Inscritos
    periodo_actual = df[df['periodo'] == periodo]['inscripcion'].values[0]*100
    periodo_anterior = df[df['periodo'] == periodo-1]['inscripcion'].values[0] * \
        100 if not (periodo == min(df['periodo'])) else None
    fig = agregar_indicador(periodo_anterior, periodo_actual, fig, 1)

    # Admitidos
    periodo_actual = df[df['periodo'] == periodo]['admicion'].values[0]
    periodo_anterior = df[df['periodo'] == periodo -
                          1]['admicion'].values[0] if not (periodo == min(df['periodo'])) else None
    fig = agregar_indicador(periodo_anterior, periodo_actual, fig, 2)

    # Matriculados
    periodo_actual = df[df['periodo'] == periodo]['matricula_total'].values[0]
    periodo_anterior = df[df['periodo'] == periodo -
                          1]['matricula_total'].values[0] if not (periodo == min(df['periodo'])) else None
    fig = agregar_indicador(periodo_anterior, periodo_actual, fig, 3)

    # Personalizar la grafica
    fig.update_layout(
        paper_bgcolor='#fff',
        plot_bgcolor='#fff',
        showlegend=False,
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=20,
            pad=0
        ),
    )

    return fig
