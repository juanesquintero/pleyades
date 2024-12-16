import traceback
import pandas as pd
import os
import json
import logging
import utils.dashboards.data_ies as DataIES

from flask import request, session, Blueprint, render_template, redirect, send_file, url_for, jsonify, flash
from dotenv import load_dotenv
from ast import literal_eval
from deep_translator import GoogleTranslator

from utils.model import prepare_data, verify_data, execute_model
from views.auth import login_required
from services.API import get, post, put

from utils.mixins import actualizar_state, save_archivo, save_ejecucion, save_preparacion, get_now_date, obtener_archivo_excel, obtener_nombre_conjunto

model_logger = logging.getLogger('model_logger')
error_logger = logging.getLogger('error_logger')

load_dotenv()

Dataset = Blueprint('Dataset', __name__)

endopoint = 'sets/'

upload_folder = os.getcwd()+'/uploads'

translator = GoogleTranslator(source='en', target='es')


@Dataset.route('')
@Dataset.route('/')
@Dataset.route('/crudos')
@Dataset.route('/crudos/')
@login_required
def crudos():
    return get_list('crudos')


@Dataset.route('/procesados')
@Dataset.route('/procesados/')
@Dataset.route('/procesados/<conjunto>')
@login_required
def procesados(conjunto=None):
    if conjunto:
        return get_list('procesados', str(conjunto))
    return get_list('procesados')


def get_list(status, conjunto=None):
    user = session.get('user', {'correo': ''}).get('correo')
    status_p, body_p = get('programs')
    status_c, body_c = get(
        f'sets/manager/{user}?status={status}'
    )

    if status_c and status_p:
        if conjunto:
            body_c = [d for d in body_c if conjunto in d['nombre']]
        return render_template(
            endopoint+status.replace(' ', '_')+'.html',
            sets=body_c,
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
        sets=[],
        error=error
    )


@Dataset.route('/donwload/<status>/<nombre>')
def download(status, nombre):

    status_c, body_c = get('sets/'+nombre)
    if not status_c:
        return render_template('utils/message.html', message='No existe ese conjunto')

    if status.lower() == 'crudos':
        nombre = 'C '+nombre
    elif status.lower() == 'procesados':
        nombre = 'P '+nombre
    else:
        return render_template('utils/message.html', message='Estado del conjunto incorrecto')

    ruta = upload_folder+'/'+status.lower()+'/'+nombre

    if os.path.exists(ruta+'.xlsx'):
        return send_file(ruta+'.xlsx', as_attachment=True)
    elif os.path.exists(ruta+'.xls'):
        return send_file(ruta+'.xls', as_attachment=True)
    else:
        return render_template('utils/message.html', message='No se encontro el archivo a donwload')


@Dataset.route('/crear')
@Dataset.route('/crear/')
@login_required
def post_create():
    periods = DataIES.get_periods_origen()
    status_f, body_f = get('faculties')
    status_p, body_p = get('programs')

    if status_f and status_p and periods:
        return render_template(endopoint+'crear.html', faculties=body_f, programs=body_p)
    elif not status_f and not status_p:
        error = {**body_f, **body_p}
    elif not status_f:
        error = body_f
    else:
        error = body_p
    return render_template('utils/message.html', message='No se pudieron cargar las programs y las faculties', submensaje=error)


@Dataset.route('crear/periods/programa/<int:programa>')
@login_required
def get_periods_program(programa):
    status, body = get(
        'desertion/students/periods/programa/{}'.format(programa))
    if status:
        return jsonify(body)
    return jsonify([])


@Dataset.route('/detalle', methods=['POST'])
@login_required
def detalle():
    # Obtener Lo valores del form
    body = dict(request.values)
    conjunto = literal_eval(body['conjunto'])
    # Consultas para mostrar info
    status_f, body_f = get('faculties')
    status_p, body_p = get('programs')
    status_u, body_u = get('users')

    if status_p and status_f and status_u and conjunto:
        return render_template(endopoint+'detail.html', faculties=body_f, programs=body_p, users=body_u, c=conjunto)
    elif not status_f and not status_p and not status_u:
        error = {**body_f, **body_p, **body_u}
    elif not status_f:
        error = body_f
    elif not status_p:
        error = body_p
    elif not conjunto:
        return render_template('utils/message.html', message='No se encontro un conjunto para detallar')
    else:
        error = body_u
    return render_template('utils/message.html', message='No se pudieron cargar los datos para detallar el conjunto', submensaje=error)


@Dataset.route('/crear', methods=['POST'])
@Dataset.route('/crear/', methods=['POST'])
@login_required
def post_save(conjunto=None):
    if not conjunto:
        # Obtener Lo valores del form
        conjunto = dict(request.values)
    # Preparar conjunto para la insercion
    del conjunto['faculty']

    # TODO NEW! version 2 v2.0.0
    session['period_closed'] = (conjunto.get('period_closed') == 'on')
    if session.get('period_closed'):
        del conjunto['period_closed']

    conjunto['status'] = 'Crudos'
    conjunto['initialPeriod'] = int(conjunto['initialPeriod'])
    conjunto['finalPeriod'] = int(conjunto['finalPeriod'])
    conjunto['programa'] = int(conjunto['programa'])
    conjunto['manager'] = session.get('user', {}).get('email')

    tipo = conjunto.get('tipo', 'consulta')
    archivo = request.files.get('archivo')
    ruta = upload_folder+'/crudos'

    # Guardar archivo en Upload folder

    ############# ARCHIVO ##############
    if (archivo and archivo.filename and tipo == 'excel'):
        extension = '.'+archivo.filename.split('.')[1]
        # Guardar archivo de excel

        if extension not in ['.xls', '.xlsx']:
            return render_template('utils/message.html', message='Extension de archivo incorrecta: '+str(extension), submensaje='Solo se permiten archivos excel .xls & xlsx')

        # VERIFICACION de formato
        data = pd.read_excel(archivo)
        validacion, mensaje_error, data_verificada, initialPeriod = verify_data(
            data, conjunto.get('initialPeriod'), conjunto.get('finalPeriod'), conjunto.get('programa'))
        conjunto['initialPeriod'] = initialPeriod

        # Obtener nombre del conjunto desde el api
        nombre, numero = obtener_nombre_conjunto(conjunto)
        if not nombre:
            return numero
        archivo_save = 'C ' + nombre + '.xlsx'

        if validacion:
            try:
                data_verificada.to_excel(
                    ruta+'/'+archivo_save,
                    engine='openpyxl',
                    index=False
                )
            except Exception as e:
                error_logger.error(e)
                return render_template('utils/message.html', message='Ocurrió un error guardando el conjunto de datos')
        else:
            return render_template('utils/message.html', message='Incorrecto el formato de la fuente de datos', submensaje=mensaje_error)

    ############# CONSULTA ##############
    # elif tipo == 'consulta':
    else:
        # Obtener datos de los students en ese programs y periods
        endpoint_conjunto = 'desertion/students/set/{}/{}/{}'
        endpoint_conjunto_values = endpoint_conjunto.format(
            conjunto['programa'], conjunto['initialPeriod'], conjunto['finalPeriod'])
        status, body = get(endpoint_conjunto_values)
        if status:
            data = pd.DataFrame(body)
        else:
            return render_template('utils/message.html', message='Consulta fallida a la base de datos')

        # VERIFICACION de formato
        validacion, mensaje_error, data_verificada, initialPeriod = verify_data(
            data, conjunto.get('initialPeriod'), conjunto.get('finalPeriod'), conjunto.get('programa'))
        conjunto['initialPeriod'] = initialPeriod

        # Obtener nombre del conjunto desde el api
        nombre, numero = obtener_nombre_conjunto(conjunto)
        if not nombre:
            return numero
        archivo_save = 'C ' + nombre + '.xlsx'

        if validacion:
            # Guardar tabla sql como excel
            try:
                data_verificada.to_excel(
                    ruta+'/'+archivo_save,
                    engine='openpyxl',
                    index=False
                )
            except Exception as e:
                error_logger.error(e)
                return render_template('utils/message.html', message='Ocurrió un error guardando el conjunto de datos')
        else:
            return render_template('utils/message.html', message='Incorrecto el formato de la fuente de datos', submensaje=mensaje_error)
    # else:
    #     return render_template('utils/message.html', message='Formulario incorrecto', submensaje='Verifica el form de creacion o notifica al Administrador del sistema')

    # Guardar registro de conjunto en la BD
    conjunto['nombre'] = nombre
    conjunto['numero'] = numero
    status, body = post('sets', conjunto)

    # TODO DEPRECATED! version 1 v1.5.0
    # if status:
    #     return redirect(url_for('Dataset.crudos'))

    # TODO NEW! version 2 v2.0.0
    if status:
        # preparar() luego de post_save()
        return preparar(conjunto)

    return render_template('utils/message.html', message='No se pudo save el conjunto', submensaje=body)


@Dataset.route('/preparar', methods=['POST'])
@login_required
def preparar(conjunto=None):
    if not conjunto:
        # Obtener Lo valores del form
        body = dict(request.values)
        conjunto = literal_eval(body['conjunto'])

    nombre = conjunto['nombre']

    # Actualizar conjunto de datos de crudo a en proceso
    act_state = actualizar_state(nombre, 'En Proceso')
    if act_state:
        return act_state

    # Crear prepraracion
    preparacion = {}
    preparacion['conjunto'] = conjunto['nombre']
    preparacion['preparador'] = session.get('user', {}).get('email')
    preparacion['fechaInicial'] = get_now_date()
    # Obtener numero de preparacion para el conjunto
    status_p, body_p = get('preparations/nombre/'+nombre)
    if status_p:
        preparacion['numero'] = body_p['numero']
        preparacion['nombre'] = body_p['nombre']
    else:
        return render_template('utils/message.html', message='No se pudo obtener el consecutivo de la preparación para este conjunto', submensaje=body_p)

    ########### PREPARAR ############

    # Obtener archivo crudo
    archivo_crudo = 'C '+nombre
    ruta = upload_folder+'/crudos/'+archivo_crudo
    exito, data_cruda = obtener_archivo_excel(ruta)
    if not exito:
        return data_cruda

    # Algoritmo de preparacion
    try:
        data_preparada = prepare_data(data_cruda)
    except Exception as e:
        model_logger.error(e)
        model_logger.error(traceback.format_exc())
        observaciones = {'error': str(e)}
        exito, pagina_error = save_preparacion(
            preparacion, observaciones, 'Fallida')
        if not exito:
            return pagina_error
        return render_template('utils/message.html', message='la preparación falló')

    # Guardar archivo en Upload folder procesados
    archivo_procesado = 'P '+nombre+'.xls'
    ruta = upload_folder+'/procesados/'+archivo_procesado
    exito, pagina_error = save_archivo(data_preparada, ruta, 'excel')
    if not exito:
        return pagina_error

    # Guardar registro de preparacion en la BD
    exito, pagina_error = save_preparacion(preparacion, None, 'Exitosa')
    if not exito:
        return pagina_error

    ########### FIN PREPARAR ############

    # Actualizar conjunto de datos de crudo a procesado
    act_state = actualizar_state(nombre, 'Procesados')
    if act_state:
        return act_state

    # TODO DEPRECATED! version 1 v1.5.0
    # return redirect(url_for('Dataset.procesados', conjunto=conjunto['nombre']))

    # TODO NEW! version 2 v2.0.0
    # ejecutar() luego de preparar()
    return ejecutar(conjunto)


@Dataset.route('/ejecutar', methods=['POST'])
@login_required
def ejecutar(conjunto=None):
    execution_saved = False

    if not conjunto:
        # Obtener Lo valores del form
        body = dict(request.values)
        conjunto = literal_eval(body['conjunto'])

    nombre = conjunto['nombre']

    # Actualizar conjunto de datos de crudo a procesado
    act_state = actualizar_state(nombre, 'En Proceso')
    if act_state:
        return act_state

    # Crear prepraracion
    execution = {}
    execution['conjunto'] = conjunto['nombre']
    execution['ejecutor'] = session.get('user', {}).get('email')
    execution['fechaInicial'] = get_now_date()

    # Obtener numero de ejecución para el conjunto
    status_p, body_p = get('executions/nombre/'+nombre)
    if status_p:
        execution['nombre'] = body_p['nombre']
        execution['numero'] = body_p['numero']
    else:
        return render_template('utils/message.html', message='No se pudo obtener el consecutivo de la preparación para este conjunto', submensaje=body_p)

    ########### EJECUTAR ############

    # Obtener archivo procesado
    archivo_procesado = 'P '+nombre
    ruta = upload_folder+'/procesados/'+archivo_procesado
    exito, data_preparada = obtener_archivo_excel(ruta)
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
            nombre
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
        exito, pagina_error = save_ejecucion(
            execution, results, 'Fallida')
        execution_saved = True
        if not exito:
            return pagina_error
        act_state = actualizar_state(nombre, 'Procesados')
        if act_state:
            return act_state
        return render_template('utils/message.html', message='La ejecución falló', submensaje=error_spa)

    if not resultados_model:
        # Actualizar conjunto de datos de crudo a procesado
        act_state = actualizar_state(nombre, 'Procesados')
        if act_state:
            return act_state
        return render_template('utils/message.html', message='La ejecución falló', submensaje=resultados_desertores)

    # Guardar registro de los desertores en la BD del ies

    # Actualizar los results a ultimo
    endpoint_ultimo = 'desertion/results/ultimo/{}/{}'
    endpoint_ultimo_values = endpoint_ultimo.format(
        conjunto['programa'], conjunto['finalPeriod']
    )
    status_update, body_update = put(endpoint_ultimo_values, {})

    # Insertar los results
    if resultados_desertores.any().any():
        resultados_insert = json.loads(
            resultados_desertores.to_json(orient='records')
        )
        status_insert, body_insert = post(
            'desertion/results', resultados_insert
        )
        if not status_update or not status_insert:
            act_state = actualizar_state(nombre, 'Procesados')
            if act_state:
                return act_state

            if not status_insert:
                error_logger.error(
                    'Error insertando los nuevos desertores'.format(json.dumps(body_insert)))

            if not status_update:
                error_logger.error('Error actualizando los desertores del programa'.format(
                    json.dumps(body_update)))

            return render_template('utils/message.html', message='Ocurrió un error insertando y/o actualizando los results'), 500

        state_ejecucion = 'Exitosa'
        # Guardar results de desertotres en Upload folder desertores
        archivo_desertores = 'D '+execution['nombre']+'.json'
        ruta = upload_folder+'/deserters/'+archivo_desertores
        exito, pagina_error = save_archivo(
            resultados_model.pop('deserters'), ruta, 'json'
        )
        if not exito:
            return pagina_error

    else:
        # TODO data
        flash('<b>El model detectó 0 desertores, Deserción 0%</b>', 'danger')
        flash(
            'Revise si hay students ó desertores suficientes en el programa', 'warning'
        )
        resultados_model.pop('deserters')
        state_ejecucion = 'Fallida'
    # Guardar registro de ejecución en la BD
    if not execution_saved:
        exito, pagina_error = save_ejecucion(
            execution=execution, results=resultados_model, status=state_ejecucion)
        if not exito:
            act_state = actualizar_state(nombre, 'Procesados')
            if act_state:
                return act_state
            return pagina_error

    ########### FIN EJECUTAR ############
    # Actualizar conjunto de datos de crudo a procesado
    act_state = actualizar_state(nombre, 'Procesados')
    if act_state:
        return act_state

    # TODO DEPRECATED! version 1 v1.5.0
    # return redirect(url_for('Result.executions', conjunto=nombre))

    # TODO NEW! version 2 v2.0.0
    return redirect(url_for('Analista.models', model=nombre))
