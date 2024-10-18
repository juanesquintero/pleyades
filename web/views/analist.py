import os
import json
import logging
import pandas as pd
from ast import literal_eval
from dotenv import load_dotenv
from flask import request, session, Blueprint, render_template, send_file, redirect, url_for, jsonify, flash

import utils.modelo as Modelo
from services.API import get, post
import web.views.sets as sets
from views.auth import login_required
import utils.tableros.data_ies as DataIES
from utils.mixins import guardar_archivo, guardar_ejecucion, get_now_date, obtener_nombre_ejecucion

load_dotenv()

error_logger = logging.getLogger('error_logger')

endopoint = 'analist/modelos/'

Analista = Blueprint('Analista', __name__)

upload_folder = os.getcwd()+'/uploads'
modelos_folder = f'{upload_folder}/modelos'


@Analista.route('/modelos', methods=['GET'])
@Analista.route('/modelos/', methods=['GET'])
@login_required
def modelos():
    modelo = request.args.get('modelo')
    success, body = get_modelos(modelo)

    if not success:
        flash('Usuario aún no tiene modelos de deserción', 'warning')
        body = []

    return render_template(
        'analist/modelos/listar.html',
        modelos=body,
    )


@Analista.route('/modelos/entrenar', methods=['GET', 'POST'])
@login_required
def entrenar():
    if request.method == 'GET':
        return formulario_entrenar()
    conjunto = dict(request.values)
    return sets.post_save(conjunto)


@Analista.route('/modelos/predecir', methods=['POST'])
def predecir():
    modelo = dict(request.values).get('modelo')
    return render_template(
        endopoint+'predecir.html',
        modelo=literal_eval(modelo)
    )


@Analista.route('/entrenamientos', methods=['GET'])
@Analista.route('/entrenamientos/', methods=['GET'])
@login_required
def entrenamientos():
    modelo = request.args.get('modelo')
    success, body = get_modelos(modelo)

    if not success:
        flash('Usuario aún no tiene entrenamientos', 'info')
        body = []

    return render_template(
        'analist/entrenamientos.html',
        entrenamientos=body,
    )


@Analista.route('/predicciones', methods=['GET'])
@Analista.route('/predicciones/', methods=['GET'])
@login_required
def predicciones():
    modelo = request.args.get('modelo')
    success, body = get_modelos(modelo)

    if not success:
        flash('Usuario aún no tiene predicciones', 'info')
        body = []

    return render_template(
        'analist/predicciones.html',
        predicciones=body,
    )


@Analista.route('/predicciones/predecir', methods=['POST'])
def predecir_modelo():
    form = dict(request.values)
    ejecucion = literal_eval(form.get('ejecucion'))
    ejecucion['fechaInicial'] = get_now_date()

    periodo = form.get('periodo')
    results = ejecucion.pop('results')
    modelo = ejecucion.get('conjunto')
    idprograma = results.get('idprograma')

    basic_info = {
        'idprograma': idprograma,
        'programa': results.get('programa'),
        'idfacultad': results.get('idfacultad'),
        'facultad': results.get('facultad'),
        'modelo': modelo
    }

    # Obtener estudiantes a predecir
    data_a_predecir = DataIES.get_students_period_programa(
        periodo, idprograma
    )

    # Preparar data
    df_data_a_predecir = pd.DataFrame(data_a_predecir)
    data_preparada = Modelo.prepare_data(df_data_a_predecir)

    # Predecir results
    resultados_modelo, resultados_desertores = Modelo.predict(
        data_preparada, periodo, basic_info
    )
    resultados_desertores['idprograma'] = resultados_desertores['idprograma'].astype(
        int
    )
    resultados_desertores['semestre_prediccion'] = resultados_desertores['semestre_prediccion'].astype(
        int
    )

    # Insertar los results
    if resultados_desertores.empty:
        flash('No hay desertores para esta predicción', 'warning')
        return redirect(url_for('Analista.modelos'))

    resultados_insert = json.loads(
        resultados_desertores.to_json(orient='records')
    )

    status_insert, body_insert = post(
        'desertion/results',
        resultados_insert
    )

    if not status_insert:
        error_logger.error(
            'Error insertando los nuevos desertores'.format(
                json.dumps(body_insert))
        )
        raise Exception(
            'Ocurrió un error insertando y/o actualizando los results'
        )

    ejecucion['nombre'], ejecucion['numero'] = obtener_nombre_ejecucion(modelo)

    # Guardar desertotres
    archivo_desertores = f"D {ejecucion.get('nombre')}.json"
    ruta = upload_folder+'/desertores/'+archivo_desertores
    guardar_archivo(
        resultados_modelo.pop('desertores'), ruta, 'json'
    )

    # Guardar ejecución
    resultados_modelo['duracion'] = ejecucion.pop('duracion')
    guardar_ejecucion(ejecucion, resultados_modelo, 'Exitosa')
    flash('Predicción exitosa!!', 'success')

    return redirect(url_for('Analista.predicciones'))


@Analista.route('/modelos/descargar', methods=['POST'])
@login_required
def download():
    modelo = dict(request.values).get('modelo')
    ruta = f'{modelos_folder}/{modelo}.pkl'

    if os.path.exists(ruta):
        return send_file(ruta, as_attachment=True)

    success, body = get_modelos()

    flash('No se encontro el archivo a descargar', 'warning')

    if not success:
        flash(f"{body.get('error')}", 'danger')

    return render_template(
        'analist/modelos/listar.html',
        modelos=body,
    )


@Analista.route('/modelos/periods/<int:programa>')
@login_required
def get_periods_programa(programa):
    status, body = get(f'desertion/estudiantes/periods/programa/{programa}')
    if status:
        return jsonify(body)
    return jsonify([])


def get_modelos(nombre=None, conjunto=None):
    user = session.get('user', {'correo': ''}).get('correo')
    endopoint = f'executions/ejecutor/{user}'
    if nombre:
        endopoint += f'?nombre={nombre}'
    elif conjunto:
        endopoint += f'?conjunto={conjunto}'
    return get(endopoint)


def formulario_entrenar():
    periods = DataIES.get_periods_origen()
    status_f, body_f = get('faculties')
    status_p, body_p = get('programs')

    if status_f and status_p and periods:
        return render_template(endopoint+'crear.html', faculties=body_f, programs=body_p)

    if not status_f and not status_p:
        error = {**body_f, **body_p}
    elif not status_f:
        error = body_f
    else:
        error = body_p
    return render_template(
        'utils/mensaje.html',
        mensaje='No se pudieron cargar las programs y las faculties',
        submensaje=error
    )