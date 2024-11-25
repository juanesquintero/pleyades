import os
import json
import logging
import pandas as pd
from ast import literal_eval
from dotenv import load_dotenv
from flask import request, session, Blueprint, render_template, send_file, redirect, url_for, jsonify, flash

import utils.model as Modelo
from services.API import get, post
import views.sets as sets
from views.auth import login_required
import utils.dashboards.data_ies as DataIES
from utils.mixins import save_archivo, save_ejecucion, get_now_date, obtener_nombre_ejecucion

load_dotenv()

error_logger = logging.getLogger('error_logger')

endopoint = 'analist/models/'

Analista = Blueprint('Analista', __name__)

upload_folder = os.getcwd()+'/uploads'
models_folder = f'{upload_folder}/models'


@Analista.route('/models', methods=['GET'])
@Analista.route('/models/', methods=['GET'])
@login_required
def models():
    model = request.args.get('model')
    success, body = get_models(model)

    if not success:
        flash('User aún no tiene models de deserción', 'warning')
        body = []

    return render_template(
        'analist/models/list.html',
        models=body,
    )


@Analista.route('/models/train', methods=['GET', 'POST'])
@login_required
def train():
    if request.method == 'GET':
        return form_train()
    conjunto = dict(request.values)
    return sets.post_save(conjunto)


@Analista.route('/models/predict', methods=['POST'])
def predict():
    model = dict(request.values).get('model')
    return render_template(
        endopoint+'predict.html',
        model=literal_eval(model)
    )


@Analista.route('/trainings', methods=['GET'])
@Analista.route('/trainings/', methods=['GET'])
@login_required
def trainings():
    model = request.args.get('model')
    success, body = get_models(model)

    if not success:
        flash('User aún no tiene trainings', 'info')
        body = []

    return render_template(
        'analist/trainings.html',
        trainings=body,
    )


@Analista.route('/predictions', methods=['GET'])
@Analista.route('/predictions/', methods=['GET'])
@login_required
def predictions():
    model = request.args.get('model')
    success, body = get_models(model)

    if not success:
        flash('User aún no tiene predictions', 'info')
        body = []

    return render_template(
        'analist/predictions.html',
        predictions=body,
    )


@Analista.route('/predictions/predict', methods=['POST'])
def predict_model():
    form = dict(request.values)
    ejecucion = literal_eval(form.get('ejecucion'))
    ejecucion['fechaInicial'] = get_now_date()

    periodo = form.get('periodo')
    results = ejecucion.pop('results')
    model = ejecucion.get('conjunto')
    idprograma = results.get('idprograma')

    basic_info = {
        'idprograma': idprograma,
        'programa': results.get('programa'),
        'idfacultad': results.get('idfacultad'),
        'faculty': results.get('faculty'),
        'model': model
    }

    # Obtener students a predict
    data_a_predict = DataIES.get_students_period_program(
        periodo, idprograma
    )

    # Preparar data
    df_data_a_predict = pd.DataFrame(data_a_predict)
    data_preparada = Modelo.prepare_data(df_data_a_predict)

    # Predecir results
    resultados_model, resultados_desertores = Modelo.predict(
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
        return redirect(url_for('Analista.models'))

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

    ejecucion['nombre'], ejecucion['numero'] = obtener_nombre_ejecucion(model)

    # Guardar desertotres
    archivo_desertores = f"D {ejecucion.get('nombre')}.json"
    ruta = upload_folder+'/desertores/'+archivo_desertores
    save_archivo(
        resultados_model.pop('desertores'), ruta, 'json'
    )

    # Guardar ejecución
    resultados_model['duracion'] = ejecucion.pop('duracion')
    save_ejecucion(ejecucion, resultados_model, 'Exitosa')
    flash('Predicción exitosa!!', 'success')

    return redirect(url_for('Analista.predictions'))


@Analista.route('/models/donwload', methods=['POST'])
@login_required
def download():
    model = dict(request.values).get('model')
    ruta = f'{models_folder}/{model}.pkl'

    if os.path.exists(ruta):
        return send_file(ruta, as_attachment=True)

    success, body = get_models()

    flash('No se encontro el archivo a donwload', 'warning')

    if not success:
        flash(f"{body.get('error')}", 'danger')

    return render_template(
        'analist/models/list.html',
        models=body,
    )


@Analista.route('/models/periods/<int:programa>')
@login_required
def get_periods_program(programa):
    status, body = get(f'desertion/students/periods/programa/{programa}')
    if status:
        return jsonify(body)
    return jsonify([])


def get_models(nombre=None, conjunto=None):
    user = session.get('user', {'correo': ''}).get('correo')
    endopoint = f'executions/ejecutor/{user}'
    if nombre:
        endopoint += f'?nombre={nombre}'
    elif conjunto:
        endopoint += f'?conjunto={conjunto}'
    return get(endopoint)


def form_train():
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
        'utils/message.html',
        mensaje='No se pudieron cargar las programs y las faculties',
        submensaje=error
    )
