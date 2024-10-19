import os
import json
import plotly
import numpy as np
from flask import request, Blueprint, render_template, jsonify

from views.auth import login_required
from utils.mixins import obtener_ies_config

# Importar dashboards de plotly para cada nivel
import utils.dashboards.mundo as Mundo
import utils.dashboards.pais as Pais
import utils.dashboards.region as Region
import utils.dashboards.data_ies as DataIES
from utils.dashboards.ies import IES
from utils.dashboards.programa import Program
import utils.dashboards.estudiante as Estudiante_file


endopoint = 'dashboards/'

Tablero = Blueprint('Tablero', __name__)

niveles = [
    {'nombre': 'Nivel Mundo', 'ruta': 'Tablero.mundo_dashboard'},
    {'nombre': 'Nivel Pais', 'ruta': 'Tablero.pais_dashboard'},
    {'nombre': 'Nivel Region', 'ruta': 'Tablero.region_dashboard'},
    {'nombre': 'Nivel IES', 'ruta': 'Tablero.ies_dashboard'},
    {'nombre': 'Nivel Program', 'ruta': 'Tablero.program_dashboard'},
    {'nombre': 'Nivel Student', 'ruta': 'Tablero.student_dashboard'},
]
periods = np.arange(2010, 2019, 1)


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
        periodos_list=periods,
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

    # Barras horizontales desertion (Solo Antioquia)
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

        periodos_list=periods,
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


@Tablero.route('/institute')
@login_required
def ies_dashboard():

    periodo = request.args.get('periodo')
    periods = DataIES.get_periods()

    try:
        periodo = int(periodo)
    except Exception as e:
        periodo = max(periods)

    ies = IES(periodo)

    # Indicadores IES
    indicadores1 = ies.indicadores1()
    indicadores1 = to_plotly_json(indicadores1) if indicadores1 else None

    indicadores2 = ies.indicadores2()
    indicadores2 = to_plotly_json(indicadores2) if indicadores2 else None

    # Barras faculties
    barras = ies.barras()
    barras = to_plotly_json(barras) if barras else None

    # Pastel faculties
    pastel = ies.pastel()
    pastel = to_plotly_json(pastel) if pastel else None

    # Lista Indicadores Programas
    indicadores_programs, cant_prgms_1 = ies.indicadores_programs()
    indicadores_programs = to_plotly_json(
        indicadores_programs) if indicadores_programs else None
    if cant_prgms_1:
        if cant_prgms_1 < 10:
            prgms_size_1 = cant_prgms_1*8*10
        else:
            prgms_size_1 = cant_prgms_1*3*10
    else:
        prgms_size_1 = 0

    # Lista Mini serie Programas
    miniseries_programs, cant_prgms_2 = ies.miniseries_programs()
    miniseries_programs = to_plotly_json(
        miniseries_programs) if miniseries_programs else None
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

        periodos_list=periods,

        nombre_ies=obtener_ies_config().get('nombre'),

        indicadores_1_plot=indicadores1,
        indicadores_2_plot=indicadores2,

        barras_plot=barras,

        pastel_plot=pastel,

        indicadores_programs_plot=indicadores_programs,
        prgms_size_1=prgms_size_1,

        miniseries_programs_plot=miniseries_programs,
        prgms_size_2=prgms_size_2,

    )

############################################################## NIVEL PROGRAMA ################################################################


@Tablero.route('/programa')
@login_required
def program_dashboard():

    periods = DataIES.get_periods_origen()
    programs = DataIES.get_programs_origen()

    periodo = request.args.get('periodo')
    programa = request.args.get('programa')

    try:
        periodo = int(periodo)
    except Exception as e:
        periodo = max(periods)

    programs_id = [str(p['idprograma']) for p in programs]
    if not (programa in programs_id):
        programa = programs[0]
    else:
        for p in programs:
            if str(p['idprograma']) == programa:
                programa = p

    if not DataIES.check_IES_period_program(periodo, programa['idprograma']):
        return render_template(
            endopoint+'programa.html',
            notfound=True,
            periodo=int(periodo),
            programa=programa['idprograma'],
            nombre_program=programa['programa'],
            periodos_list=periods,
            programs_list=programs,
        )

    program_graph = Program(
        periodo=periodo, programa=programa['idprograma'], periods=periods)

    # Indicadores Program
    indicadores = program_graph.indicadores()
    indicadores = to_plotly_json(indicadores) if indicadores else None

    # Radial Matricula
    radial = program_graph.radial()
    radial = to_plotly_json(radial) if radial else None

    # Pastel Estratos
    pastel = program_graph.pastel()
    pastel = to_plotly_json(pastel) if pastel else None

    # Barras Desertores
    barras, cant_niveles, cant_periods = program_graph.barras()
    barras = to_plotly_json(barras) if barras else None
    if cant_periods:
        if cant_periods < 10:
            periodos_size = cant_periods*2.5*10
        else:
            periodos_size = cant_periods*1.3*10
    else:
        periodos_size = 0

    return render_template(
        endopoint+'programa.html',
        periodo=int(periodo),
        programa=programa['idprograma'],

        nombre_program=programa['programa'],
        nombre_ies=os.getenv('CLI_IES_NAME'),
        periodos_list=periods,
        programs_list=programs,

        indicadores_plot=indicadores,
        radial_plot=radial,
        pastel_plot=pastel,
        barras_plot=barras,

        periodos_size=periodos_size,
    )


############################################################## NIVEL ESTUDIANTE ################################################################
@Tablero.route('/estudiante')
@login_required
def student_dashboard():
    periods = DataIES.get_periods()
    programs = DataIES.get_programs()

    periodo = request.args.get('periodo')
    programa = request.args.get('programa')
    documento = request.args.get('documento')

    # Obtener la lista de students de un programa
    if programa and not documento:
        students_program = Estudiante_file.students_program(programa)
        return render_template(
            endopoint+'students_program.html',
            students_list=students_program,
            programa=programa,
            programs_list=programs,
        )

    # Buscar estudiante por programa o cedula
    if not documento:
        return render_template(
            endopoint+'buscar_estudiante.html',
            periodos_list=periods,
            programs_list=programs,
        )

    for p in programs:
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
        # Obtener los graficos del students por documento identificacion
        estudiante = Student(identificacion=documento,
                             programa=programa, periodo=periodo)

        info, periodos_estudiante, programs_estudiante = estudiante.get_estudiante()

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

    # Validar los periods y programs
    if info:
        if not programa:
            for p in programs:
                if str(p['idprograma']) == str(info['idprograma']):
                    programa = p
        if not periodo:
            periodo = int(info['REGISTRO'])

    return render_template(
        endopoint+'estudiante.html',

        periodos_list=sorted(periodos_estudiante),
        programs_list=programs_estudiante,

        estudiante=info,

        documento=documento,
        programa=programa,
        periodo=periodo,

        serie_promedio_plot=serie_promedio,
        creditos_a_plot=creditos_a,
        creditos_r_plot=creditos_r,
    )
