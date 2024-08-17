import os
import json
import plotly
import numpy as np
from flask import request, Blueprint, render_template, jsonify

from views.auth import login_required
from utils.mixins import obtener_ies_config

# Importar tableros de plotly para cada nivel
import utils.tableros.mundo as Mundo
import utils.tableros.pais as Pais
import utils.tableros.region as Region
import utils.tableros.data_ies as DataIES
from utils.tableros.ies import IES
from utils.tableros.programa import Programa
import utils.tableros.estudiante as Estudiante_file


endopoint = 'tableros/'

Tablero = Blueprint('Tablero', __name__)

niveles = [
    {'nombre': 'Nivel Mundo', 'ruta': 'Tablero.mundo_dashboard'},
    {'nombre': 'Nivel Pais', 'ruta': 'Tablero.pais_dashboard'},
    {'nombre': 'Nivel Region', 'ruta': 'Tablero.region_dashboard'},
    {'nombre': 'Nivel IES', 'ruta': 'Tablero.ies_dashboard'},
    {'nombre': 'Nivel Programa', 'ruta': 'Tablero.programa_dashboard'},
    {'nombre': 'Nivel Estudiante', 'ruta': 'Tablero.estudiante_dashboard'},
]
periodos = np.arange(2010, 2019, 1)


@Tablero.route('/')
def menu():
    return render_template(endopoint+'index.html', niveles=niveles)


def to_plotly_json(fig):
    plt = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return plt

############################################################## NIVEL MUNDO ################################################################


@Tablero.route('/mundo')
def mundo_dashboard():
    # Series Por pais
    pais = request.args.get('pais')

    if pais:
        gastos, inscripciones = Mundo.series_pais(pais)
        gastos, inscripciones = to_plotly_json(
            gastos), to_plotly_json(inscripciones)
        return jsonify([gastos, inscripciones])
    else:
        pais = 'COL'
        gastos, inscripciones = Mundo.series_pais(pais)

    clusters = to_plotly_json(Mundo.clusters())
    mapa = to_plotly_json(Mundo.mapa())
    gastos, inscripciones = to_plotly_json(
        gastos), to_plotly_json(inscripciones)

    return render_template(
        endopoint+'mundial.html',
        gastos_plot=gastos,
        inscrp_plot=inscripciones,
        mapa_plot=mapa,
        clusters_plot=clusters,
        pais=pais
    )

############################################################## NIVEL PAIS ################################################################


@Tablero.route('/pais')
def pais_dashboard():
    # Series Por pais
    periodo = request.args.get('periodo')
    if not periodo:
        periodo = '2018'

    mapa = to_plotly_json(Pais.mapa(periodo))
    barras = to_plotly_json(Pais.barras())
    pastel = to_plotly_json(Pais.pastel(periodo))
    genero = to_plotly_json(Pais.genero(periodo))
    indicadores = to_plotly_json(Pais.indicadores(periodo))
    indicadores2 = to_plotly_json(Pais.indicadores2(periodo))

    return render_template(
        endopoint+'nacional.html',
        mapa_plot=mapa,
        barras_plot=barras,
        pastel_plot=pastel,
        genero_plot=genero,
        indicadores_plot=indicadores,
        indicadores2_plot=indicadores2,
        periodos_list=periodos,
        periodo=int(periodo),
    )


############################################################## NIVEL REGION ################################################################
@Tablero.route('/region')
def region_dashboard():

    periodo = request.args.get('periodo')
    dpto = request.args.get('dpto')

    if not periodo:
        periodo = '2018'
    if not dpto:
        dpto = 'ANTIOQUIA'

    dptos = Region.dptos

    # Mapa dpto
    mapa = Region.mapa(dpto, periodo)
    mapa = to_plotly_json(mapa) if mapa else None

    # Barras verticales retencion
    barras = Region.barras(dpto)
    barras = to_plotly_json(barras)if barras else None

    # Pastel sector IES matricula
    pastel = Region.pastel(dpto, periodo)
    pastel = to_plotly_json(pastel) if pastel else None

    # Barras genero matricula
    genero = Region.genero(dpto, periodo)
    genero = to_plotly_json(genero) if genero else None

    # Indicadores departamento
    indicadores_dpto = Region.indicadores_dpto(dpto, periodo)
    indicadores_dpto = to_plotly_json(
        indicadores_dpto) if indicadores_dpto else None

    # Indicadores y miniserie matricula
    indicadores_ies, cant_ies = Region.indicadores_ies(dpto)
    indicadores_ies = to_plotly_json(
        indicadores_ies) if indicadores_ies else None

    # Barras horizontales desercion (Solo Antioquia)
    barras_ies = Region.barras_ies(dpto, periodo)
    barras_ies = to_plotly_json(barras_ies) if barras_ies else None

    if cant_ies:
        if cant_ies < 10:
            ies_size = cant_ies*7*10
        else:
            ies_size = cant_ies*3*10
    else:
        ies_size = 0

    return render_template(
        endopoint+'regional.html',
        periodo=int(periodo),
        dpto=str(dpto),

        periodos_list=periodos,
        dptos_list=dptos,
        ies_size=ies_size,

        mapa_plot=mapa,
        barras_plot=barras,
        pastel_plot=pastel,
        genero_plot=genero,

        indicadores_dpto_plot=indicadores_dpto,
        indicadores_ies_plot=indicadores_ies,

        barras_ies_plot=barras_ies,
    )
############################################################## NIVEL IES ################################################################


@Tablero.route('/institucion')
@login_required
def ies_dashboard():

    periodo = request.args.get('periodo')
    periodos = DataIES.get_periodos()

    try:
        periodo = int(periodo)
    except Exception as e:
        periodo = max(periodos)

    ies = IES(periodo)

    # Indicadores IES
    indicadores1 = ies.indicadores1()
    indicadores1 = to_plotly_json(indicadores1) if indicadores1 else None

    indicadores2 = ies.indicadores2()
    indicadores2 = to_plotly_json(indicadores2) if indicadores2 else None

    # Barras facultades
    barras = ies.barras()
    barras = to_plotly_json(barras) if barras else None

    # Pastel facultades
    pastel = ies.pastel()
    pastel = to_plotly_json(pastel) if pastel else None

    # Lista Indicadores Programas
    indicadores_programas, cant_prgms_1 = ies.indicadores_programas()
    indicadores_programas = to_plotly_json(
        indicadores_programas) if indicadores_programas else None
    if cant_prgms_1:
        if cant_prgms_1 < 10:
            prgms_size_1 = cant_prgms_1*8*10
        else:
            prgms_size_1 = cant_prgms_1*3*10
    else:
        prgms_size_1 = 0

    # Lista Mini serie Programas
    miniseries_programas, cant_prgms_2 = ies.miniseries_programas()
    miniseries_programas = to_plotly_json(
        miniseries_programas) if miniseries_programas else None
    if cant_prgms_2:
        if cant_prgms_2 < 10:
            prgms_size_2 = cant_prgms_2*7*10
        else:
            prgms_size_2 = cant_prgms_2*2.5*10
    else:
        prgms_size_2 = 0

    return render_template(
        endopoint+'institucional.html',
        periodo=int(periodo),

        periodos_list=periodos,

        nombre_ies=obtener_ies_config().get('nombre'),

        indicadores_1_plot=indicadores1,
        indicadores_2_plot=indicadores2,

        barras_plot=barras,

        pastel_plot=pastel,

        indicadores_programas_plot=indicadores_programas,
        prgms_size_1=prgms_size_1,

        miniseries_programas_plot=miniseries_programas,
        prgms_size_2=prgms_size_2,

    )

############################################################## NIVEL PROGRAMA ################################################################


@Tablero.route('/programa')
@login_required
def programa_dashboard():

    periodos = DataIES.get_periodos_origen()
    programas = DataIES.get_programas_origen()

    periodo = request.args.get('periodo')
    programa = request.args.get('programa')

    try:
        periodo = int(periodo)
    except Exception as e:
        periodo = max(periodos)

    programas_id = [str(p['idprograma']) for p in programas]
    if not (programa in programas_id):
        programa = programas[0]
    else:
        for p in programas:
            if str(p['idprograma']) == programa:
                programa = p

    if not DataIES.check_IES_periodo_programa(periodo, programa['idprograma']):
        return render_template(
            endopoint+'programa.html',
            notfound=True,
            periodo=int(periodo),
            programa=programa['idprograma'],
            nombre_programa=programa['programa'],
            periodos_list=periodos,
            programas_list=programas,
        )

    programa_graph = Programa(
        periodo=periodo, programa=programa['idprograma'], periodos=periodos)

    # Indicadores Programa
    indicadores = programa_graph.indicadores()
    indicadores = to_plotly_json(indicadores) if indicadores else None

    # Radial Matricula
    radial = programa_graph.radial()
    radial = to_plotly_json(radial) if radial else None

    # Pastel Estratos
    pastel = programa_graph.pastel()
    pastel = to_plotly_json(pastel) if pastel else None

    # Barras Desertores
    barras, cant_niveles, cant_periodos = programa_graph.barras()
    barras = to_plotly_json(barras) if barras else None
    if cant_periodos:
        if cant_periodos < 10:
            periodos_size = cant_periodos*2.5*10
        else:
            periodos_size = cant_periodos*1.3*10
    else:
        periodos_size = 0

    return render_template(
        endopoint+'programa.html',
        periodo=int(periodo),
        programa=programa['idprograma'],

        nombre_programa=programa['programa'],
        nombre_ies=os.getenv('CLI_IES_NAME'),
        periodos_list=periodos,
        programas_list=programas,

        indicadores_plot=indicadores,
        radial_plot=radial,
        pastel_plot=pastel,
        barras_plot=barras,

        periodos_size=periodos_size,
    )


############################################################## NIVEL ESTUDIANTE ################################################################
@Tablero.route('/estudiante')
@login_required
def estudiante_dashboard():
    periodos = DataIES.get_periodos()
    programas = DataIES.get_programas()

    periodo = request.args.get('periodo')
    programa = request.args.get('programa')
    documento = request.args.get('documento')

    # Obtener la lista de estudiantes de un programa
    if programa and not documento:
        estudiantes_programa = Estudiante_file.estudiantes_programa(programa)
        return render_template(
            endopoint+'estudiantes_programa.html',
            estudiantes_list=estudiantes_programa,
            programa=programa,
            programas_list=programas,
        )

    # Buscar estudiante por programa o cedula
    if not documento:
        return render_template(
            endopoint+'buscar_estudiante.html',
            periodos_list=periodos,
            programas_list=programas,
        )

    for p in programas:
        if str(p['idprograma']) == str(programa):
            programa = p

    if programa and not (isinstance(programa, dict)):
        return render_template(
            endopoint+'estudiante.html',
            estudiante=None,
            documento=documento,
            periodo=periodo,
            programa=programa,
        )

    try:
        # Obtener los graficos del estudiantes por documento identificacion
        estudiante = Estudiante(identificacion=documento,
                                programa=programa, periodo=periodo)

        info, periodos_estudiante, programas_estudiante = estudiante.get_estudiante()

        # Serie promedio acumulado
        serie_promedio = estudiante.serie_promedio()
        serie_promedio = to_plotly_json(
            serie_promedio) if serie_promedio else None

        # Progreso creditos
        creditos_a = estudiante.progreso_creditos_aprobados()
        creditos_a = to_plotly_json(creditos_a) if creditos_a else None

        creditos_r = estudiante.progreso_creditos_reprobados()
        creditos_r = to_plotly_json(creditos_r) if creditos_r else None

    except Exception as e:
        return render_template(
            endopoint+'estudiante.html',
            estudiante=None,
            documento=documento,
            programa=programa,
            periodo=periodo,
        )

    # Validar los periodos y programas
    if info:
        if not programa:
            for p in programas:
                if str(p['idprograma']) == str(info['idprograma']):
                    programa = p
        if not periodo:
            periodo = int(info['REGISTRO'])

    return render_template(
        endopoint+'estudiante.html',

        periodos_list=sorted(periodos_estudiante),
        programas_list=programas_estudiante,

        estudiante=info,

        documento=documento,
        programa=programa,
        periodo=periodo,

        serie_promedio_plot=serie_promedio,
        creditos_a_plot=creditos_a,
        creditos_r_plot=creditos_r,
    )
