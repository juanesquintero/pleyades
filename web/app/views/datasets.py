import traceback
import pandas as pd
import os
import json
import logging
from web.app.utils.constants import Roles
import web.app.utils.dashboards.data_ies as DataIES

from flask import request, session, Blueprint, render_template, redirect, send_file, url_for, jsonify, flash
from dotenv import load_dotenv
from ast import literal_eval
from deep_translator import GoogleTranslator

from web.app.utils.model import prepare_data, verify_data, execute_model
from web.app.views.auth import login_required
from web.app.services.API import get, post, put

from web.app.utils.mixins import update_status, save_file, save_execution, save_preparation, get_now_date, get_excel_file, get_dataset_name

model_logger = logging.getLogger('model_logger')
error_logger = logging.getLogger('error_logger')

load_dotenv()

Dataset = Blueprint('Dataset', __name__)

endopoint = 'datasets/'

upload_folder = os.getcwd()+'/uploads'

translator = GoogleTranslator(source='en', target='es')


@Dataset.route('/')
@Dataset.route('/raw')
@Dataset.route('/raw/')
@login_required
def raw():
    return get_list('raw')


@Dataset.route('/processed')
@Dataset.route('/processed/')
@Dataset.route('/processed/<dataset>')
@login_required
def processed(dataset=None):
    if dataset:
        return get_list('processed', str(dataset))
    return get_list('processed')


def get_list(status, dataset=None):
    user = session.get('user', {'correo': ''}).get('correo')
    status_p, body_p = get('programs')
    status_c, body_c = get(
        f'datasets/manager/{user}?status={status}'
    )

    if status_c and status_p:
        if dataset:
            body_c = [d for d in body_c if dataset in d['name']]
        return render_template(
            endopoint+status.replace(' ', '_')+'.html',
            datasets=body_c,
            programs=body_p
        )

    if not status_c and not status_p:
        error = {**body_c, **body_p}
    elif not status_c:
        error = body_c
    else:
        error = body_p
    return render_template(
        endopoint+status.replace(' ', '_')+'.html',
        datasets=[],
        error=error
    )


@Dataset.route('/donwload/<status>/<name>')
def download(status, name):

    status_c, body_c = get('datasets/'+name)
    if not status_c:
        return render_template('utils/message.html', message='No existe ese dataset')

    if status.lower() == 'raw':
        name = 'C '+name
    elif status.lower() == 'processed':
        name = 'P '+name
    else:
        return render_template('utils/message.html', message='Estado del dataset incorrecto')

    ruta = upload_folder+'/'+status.lower()+'/'+name

    if os.path.exists(ruta+'.xlsx'):
        return send_file(ruta+'.xlsx', as_attachment=True)

    if os.path.exists(ruta+'.xls'):
        return send_file(ruta+'.xls', as_attachment=True)

    return render_template('utils/message.html', message='Can Not encontro el file a donwload')


@Dataset.route('/create')
@Dataset.route('/create/')
@login_required
def post_create():
    periods = DataIES.get_periods_origin()
    status_f, body_f = get('faculties')
    status_p, body_p = get('programs')

    if status_f and status_p and periods:
        return render_template(endopoint+'create.html', faculties=body_f, programs=body_p)

    if not status_f and not status_p:
        error = {**body_f, **body_p}
    elif not status_f:
        error = body_f
    else:
        error = body_p

    return render_template('utils/message.html', message='Could Not load the programs and the faculties', submensaje=error)


@Dataset.route('create/periods/program/<int:program>')
@login_required
def get_periods_program(program):
    status, body = get(
        'desertion/students/periods/program/{}'.format(program)
    )
    if status:
        return jsonify(body)
    return jsonify([])


@Dataset.route('/detail', methods=['POST'])
@login_required
def detail():
    # Obtener Lo valores del form
    body = dict(request.values)
    dataset = literal_eval(body['dataset'])
    # Consultas para mostrar info
    status_f, body_f = get('faculties')
    status_p, body_p = get('programs')
    status_u, body_u = get('users')

    if status_p and status_f and status_u and dataset:
        return render_template(endopoint+'detail.html', faculties=body_f, programs=body_p, users=body_u, c=dataset)

    if not status_f and not status_p and not status_u:
        error = {**body_f, **body_p, **body_u}
    elif not status_f:
        error = body_f
    elif not status_p:
        error = body_p
    elif not dataset:
        return render_template(
            'utils/message.html',
            message='Can Not encontro un dataset para detallar'
        )
    else:
        error = body_u

    return render_template(
        'utils/message.html',
        message='Could Not load the datos para detallar el dataset',
        submensaje=error
    )


@Dataset.route('/create', methods=['POST'])
@Dataset.route('/create/', methods=['POST'])
@login_required
def post_save(dataset=None):
    if not dataset:
        # Obtener Lo valores del form
        dataset = dict(request.values)
    # Preparar dataset para the insercion
    del dataset['faculty']

    # TODO NEW! version 2 v2.0.0
    session['period_closed'] = dataset.get('period_closed') == 'on'
    if session.get('period_closed'):
        del dataset['period_closed']

    dataset['status'] = 'Raw'
    dataset['initialPeriod'] = int(dataset['initialPeriod'])
    dataset['finalPeriod'] = int(dataset['finalPeriod'])
    dataset['program'] = int(dataset['program'])
    dataset['manager'] = session.get('user', {}).get('email')

    tipo = dataset.get('tipo', 'consulta')
    file = request.files.get('file')
    ruta = upload_folder+'/raw'

    # Guardar file en Upload folder

    ############# ARCHIVO ##############
    if (file and file.filename and tipo == 'excel'):
        extension = '.'+file.filename.split('.')[1]
        # Guardar file de excel

        if extension not in ['.xls', '.xlsx']:
            return render_template(
                'utils/message.html',
                message='Extension de file incorrecta: '+str(extension),
                submensaje='Solo se permiten files excel .xls & xlsx'
            )

        # VERIFICACION de formato
        data = pd.read_excel(file)
        validacion, mensaje_error, data_verificada, initial_period = verify_data(
            data, dataset.get('initialPeriod'),
            dataset.get('finalPeriod'),
            dataset.get('program')
        )
        dataset['initialPeriod'] = initial_period

        # Obtener name del dataset desde el api
        name, number = get_dataset_name(dataset)
        if not name:
            return number
        file_save = 'C ' + name + '.xlsx'

        if validacion:
            try:
                data_verificada.to_excel(
                    ruta+'/'+file_save,
                    engine='openpyxl',
                    index=False
                )
            except Exception as e:
                error_logger.error(e)
                return render_template(
                    'utils/message.html',
                    message='Ocurrió un error guardando el dataset de datos'
                )
        else:
            return render_template(
                'utils/message.html',
                message='Incorrecto el formato de the fuente de datos',
                submensaje=mensaje_error
            )

    ############# CONSULTA ##############
    # elif tipo == 'consulta':
    else:
        # Obtener datos de the students en ese programs y periods
        endpoint_dataset = 'desertion/students/dataset/{}/{}/{}'
        endpoint_dataset_values = endpoint_dataset.format(
            dataset['program'], dataset['initialPeriod'], dataset['finalPeriod'])
        status, body = get(endpoint_dataset_values)
        if status:
            data = pd.DataFrame(body)
        else:
            return render_template(
                'utils/message.html',
                message='Consulta fallida a the base de datos'
            )

        # VERIFICACION de formato
        validacion, mensaje_error, data_verificada, initial_period = verify_data(
            data, dataset.get('initialPeriod'), dataset.get('finalPeriod'), dataset.get('program'))
        dataset['initialPeriod'] = initial_period

        # Obtener name del dataset desde el api
        name, number = get_dataset_name(dataset)
        if not name:
            return number
        file_save = 'C ' + name + '.xlsx'

        if validacion:
            # Guardar tabla sql como excel
            try:
                data_verificada.to_excel(
                    ruta+'/'+file_save,
                    engine='openpyxl',
                    index=False
                )
            except Exception as e:
                error_logger.error(e)
                return render_template(
                    'utils/message.html',
                    message='Ocurrió un error guardando el dataset de datos'
                )
        else:
            return render_template(
                'utils/message.html',
                message='Incorrecto el formato de the fuente de datos',
                submensaje=mensaje_error
            )
    # else:
    #     return render_template('utils/message.html', message='Formulario incorrecto', submensaje='Verifica el form de creacion o notifica al Administrador del sistema')

    # Guardar registro de dataset en the BD
    dataset['name'] = name
    dataset['number'] = number
    status, body = post('datasets', dataset)

    # TODO DEPRECATED! version 1 v1.5.0
    # if status:
    #     return redirect(url_for('Dataset.raw'))

    # TODO NEW! version 2 v2.0.0
    if status:
        # preparar() luego de post_save()
        return preparar(dataset)

    return render_template(
        'utils/message.html',
        message='Can Not pudo save el dataset',
        submensaje=body
    )


@Dataset.route('/preparar', methods=['POST'])
@login_required
def preparar(dataset=None):
    if not dataset:
        # Obtener Lo valores del form
        body = dict(request.values)
        dataset = literal_eval(body['dataset'])

    name = dataset['name']

    # Actualizar dataset de datos de crudo a in progress
    act_status = update_status(name, 'In Progress')
    if act_status:
        return act_status

    # Crear prepraracion
    preparation = {}
    preparation['dataset'] = dataset['name']
    preparation['preparador'] = session.get('user', {}).get('email')
    preparation['startDate'] = get_now_date()
    # Obtener number de preparation para el dataset
    status_p, body_p = get('preparations/name/'+name)
    if status_p:
        preparation['number'] = body_p['number']
        preparation['name'] = body_p['name']
    else:
        return render_template(
            'utils/message.html',
            message='Can Not pudo get el consecutivo de the preparación para este dataset',
            submensaje=body_p
        )

    ########### PREPARAR ############

    # Obtener file crudo
    file_crudo = 'C '+name
    ruta = upload_folder+'/raw/'+file_crudo
    exito, data_cruda = get_excel_file(ruta)
    if not exito:
        return data_cruda

    # Algoritmo de preparation
    try:
        data_preparada = prepare_data(data_cruda)
    except Exception as e:
        model_logger.error(e)
        model_logger.error(traceback.format_exc())
        observaciones = {'error': str(e)}
        exito, pagina_error = save_preparation(
            preparation, observaciones, 'Failed')
        if not exito:
            return pagina_error
        return render_template('utils/message.html', message='the preparación falló')

    # Guardar file en Upload folder processed
    file_procesado = 'P '+name+'.xls'
    ruta = upload_folder+'/processed/'+file_procesado
    exito, pagina_error = save_file(data_preparada, ruta, 'excel')
    if not exito:
        return pagina_error

    # Guardar registro de preparation en the BD
    exito, pagina_error = save_preparation(preparation, None, 'Successful')
    if not exito:
        return pagina_error

    ########### FIN PREPARAR ############

    # Actualizar dataset de datos de crudo a processed
    act_status = update_status(name, 'Processed')
    if act_status:
        return act_status

    # TODO DEPRECATED! version 1 v1.5.0
    # return redirect(url_for('Dataset.processed', dataset=dataset['name']))

    # TODO NEW! version 2 v2.0.0
    # ejecutar() luego de preparar()
    return ejecutar(dataset)


@Dataset.route('/ejecutar', methods=['POST'])
@login_required
def ejecutar(dataset=None):
    execution_saved = False

    if not dataset:
        # Obtener Lo valores del form
        body = dict(request.values)
        dataset = literal_eval(body['dataset'])

    name = dataset['name']

    # Actualizar dataset de datos de crudo a processed
    act_status = update_status(name, 'In Progress')
    if act_status:
        return act_status

    # Crear prepraracion
    execution = {}
    execution['dataset'] = dataset['name']
    execution[Roles.EXECUTOR] = session.get('user', {}).get('email')
    execution['startDate'] = get_now_date()

    # Obtener number de ejecución para el dataset
    status_p, body_p = get('executions/name/'+name)
    if status_p:
        execution['name'] = body_p['name']
        execution['number'] = body_p['number']
    else:
        return render_template('utils/message.html', message='Can Not pudo get el consecutivo de the preparación para este dataset', submensaje=body_p)

    ########### EJECUTAR ############

    # Obtener file processed
    file_procesado = 'P '+name
    ruta = upload_folder+'/processed/'+file_procesado
    exito, data_preparada = get_excel_file(ruta)
    if not exito:
        return data_preparada

    # Algoritmo de ejecución
    # try:
    #     resultados_model,resultados_desertores = clasificador(data_preparada)
    # except Exception as e:
    #   pass
    try:
        resultados_model, resultados_desertores = execute_model(
            data_preparada,
            name
        )
    except Exception as e:
        error_logger.error(e)
        try:
            error_spa = translator.translate(str(e), src='en', dest='es').text
        except:
            error_spa = str(e)
        model_logger.error(error_spa)
        model_logger.error(traceback.format_exc())

        results = {'error': error_spa}
        exito, pagina_error = save_execution(
            execution, results, 'Failed')
        execution_saved = True
        if not exito:
            return pagina_error
        act_status = update_status(name, 'Processed')
        if act_status:
            return act_status
        return render_template('utils/message.html', message='La ejecución falló', submensaje=error_spa)

    if not resultados_model:
        # Actualizar dataset de datos de crudo a processed
        act_status = update_status(name, 'Processed')
        if act_status:
            return act_status
        return render_template('utils/message.html', message='La ejecución falló', submensaje=resultados_desertores)

    # Guardar registro de the desertores en the BD del ies

    # Actualizar the results a ultimo
    endpoint_ultimo = 'desertion/results/ultimo/{}/{}'
    endpoint_ultimo_values = endpoint_ultimo.format(
        dataset['program'], dataset['finalPeriod']
    )
    status_update, body_update = put(endpoint_ultimo_values, {})

    # Insertar the results
    if resultados_desertores.any().any():
        resultados_insert = json.loads(
            resultados_desertores.to_json(orient='records')
        )
        status_insert, body_insert = post(
            'desertion/results', resultados_insert
        )
        if not status_update or not status_insert:
            act_status = update_status(name, 'Processed')
            if act_status:
                return act_status

            if not status_insert:
                error_logger.error(
                    'Error insertando the nuevos desertores'.format(json.dumps(body_insert)))

            if not status_update:
                error_logger.error('Error actualizando the desertores del program'.format(
                    json.dumps(body_update)))

            return render_template('utils/message.html', message='Ocurrió un error insertando y/o actualizando the results'), 500

        status_execution = 'Successful'
        # Guardar results de desertotres en Upload folder desertores
        file_desertores = 'D '+execution['name']+'.json'
        ruta = upload_folder+'/deserters/'+file_desertores
        exito, pagina_error = save_file(
            resultados_model.pop('deserters'), ruta, 'json'
        )
        if not exito:
            return pagina_error

    else:
        # TODO data
        flash('<b>El model detectó 0 desertores, Deserción 0%</b>', 'danger')
        flash(
            'Revise si hay students ó desertores suficientes en el program', 'warning'
        )
        resultados_model.pop('deserters')
        status_execution = 'Failed'
    # Guardar registro de ejecución en the BD
    if not execution_saved:
        exito, pagina_error = save_execution(
            execution=execution, results=resultados_model, status=status_execution)
        if not exito:
            act_status = update_status(name, 'Processed')
            if act_status:
                return act_status
            return pagina_error

    ########### FIN EJECUTAR ############
    # Actualizar dataset de datos de crudo a processed
    act_status = update_status(name, 'Processed')
    if act_status:
        return act_status

    # TODO DEPRECATED! version 1 v1.5.0
    # return redirect(url_for('Result.executions', dataset=name))

    # TODO NEW! version 2 v2.0.0
    return redirect(url_for('Analyst.models', model=name))
