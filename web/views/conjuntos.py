import traceback
import pandas as pd
import os
import json
import logging
import utils.tableros.data_ies as DataIES

from flask import request, session, Blueprint, render_template, redirect, send_file, url_for, jsonify, flash
from dotenv import load_dotenv
from ast import literal_eval
from googletrans import Translator

from utils.modelo import prepare_data, verify_data, execute_model
from views.auth import login_required
from services.API import get, post, put

from utils.mixins import actualizar_state, guardar_archivo, guardar_ejecucion, guardar_preparacion, get_now_date, obtener_archivo_excel, obtener_nombre_conjunto

model_logger = logging.getLogger('model_logger')
error_logger = logging.getLogger('error_logger')

load_dotenv()

StudentSet = Blueprint('StudentSet', __name__)

endopoint = 'conjuntos/'

upload_folder = os.getcwd()+'/uploads'

translator = Translator()


@StudentSet.route('')
@StudentSet.route('/')
@StudentSet.route('/crudos')
@StudentSet.route('/crudos/')
@login_required
def crudos():
    return get_list('crudos')


@StudentSet.route('/procesados')
@StudentSet.route('/procesados/')
@StudentSet.route('/procesados/<conjunto>')
@login_required
def procesados(conjunto=None):
    if conjunto:
        return get_list('procesados', str(conjunto))
    return get_list('procesados')


def get_list(estado, conjunto=None):
    user = session.get('user', {'correo': ''}).get('correo')
    status_p, body_p = get('programas')
    status_c, body_c = get(
        f'conjuntos/encargado/{user}?estado={estado}'
    )

    if status_c and status_p:
        if conjunto:
            body_c = [d for d in body_c if conjunto in d['nombre']]
        return render_template(
            endopoint+estado.replace(' ', '_')+'.html',
            conjuntos=body_c,
            programas=body_p
        )

    if not status_c and not status_p:
        error = {**body_c, **body_p}
    elif not status_c:
        error = body_c
    else:
        error = body_p
    return render_template(
        endopoint+estado.replace(' ', '_')+'.html',
        conjuntos=[],
        error=error
    )


@StudentSet.route('/descargar/<estado>/<nombre>')
def download(estado, nombre):

    status_c, body_c = get('conjuntos/'+nombre)
    if not status_c:
        return render_template('utils/mensaje.html', mensaje='No existe ese conjunto')

    if estado.lower() == 'crudos':
        nombre = 'C '+nombre
    elif estado.lower() == 'procesados':
        nombre = 'P '+nombre
    else:
        return render_template('utils/mensaje.html', mensaje='Estado del conjunto incorrecto')

    ruta = upload_folder+'/'+estado.lower()+'/'+nombre

    if os.path.exists(ruta+'.xlsx'):
        return send_file(ruta+'.xlsx', as_attachment=True)
    elif os.path.exists(ruta+'.xls'):
        return send_file(ruta+'.xls', as_attachment=True)
    else:
        return render_template('utils/mensaje.html', mensaje='No se encontro el archivo a descargar')


@StudentSet.route('/crear')
@StudentSet.route('/crear/')
@login_required
def post_create():
    periods = DataIES.get_periods_origen()
    status_f, body_f = get('facultades')
    status_p, body_p = get('programas')

    if status_f and status_p and periods:
        return render_template(endopoint+'crear.html', facultades=body_f, programas=body_p)
    elif not status_f and not status_p:
        error = {**body_f, **body_p}
    elif not status_f:
        error = body_f
    else:
        error = body_p
    return render_template('utils/mensaje.html', mensaje='No se pudieron cargar las programas y las facultades', submensaje=error)


@StudentSet.route('crear/periods/programa/<int:programa>')
@login_required
def get_periods_programa(programa):
    status, body = get(
        'desercion/estudiantes/periods/programa/{}'.format(programa))
    if status:
        return jsonify(body)
    return jsonify([])


@StudentSet.route('/detalle', methods=['POST'])
@login_required
def detalle():
    # Obtener Lo valores del formulario
    body = dict(request.values)
    conjunto = literal_eval(body['conjunto'])
    # Consultas para mostrar info
    status_f, body_f = get('facultades')
    status_p, body_p = get('programas')
    status_u, body_u = get('usuarios')

    if status_p and status_f and status_u and conjunto:
        return render_template(endopoint+'detalle.html', facultades=body_f, programas=body_p, usuarios=body_u, c=conjunto)
    elif not status_f and not status_p and not status_u:
        error = {**body_f, **body_p, **body_u}
    elif not status_f:
        error = body_f
    elif not status_p:
        error = body_p
    elif not conjunto:
        return render_template('utils/mensaje.html', mensaje='No se encontro un conjunto para detallar')
    else:
        error = body_u
    return render_template('utils/mensaje.html', mensaje='No se pudieron cargar los datos para detallar el conjunto', submensaje=error)


@StudentSet.route('/crear', methods=['POST'])
@StudentSet.route('/crear/', methods=['POST'])
@login_required
def post_save(conjunto=None):
    if not conjunto:
        # Obtener Lo valores del formulario
        conjunto = dict(request.values)
    # Preparar conjunto para la insercion
    del conjunto['facultad']

    # TODO NEW! version 2 v2.0.0
    session['period_closed'] = (conjunto.get('period_closed') == 'on')
    if session.get('period_closed'):
        del conjunto['period_closed']

    conjunto['estado'] = 'Crudos'
    conjunto['periodoInicial'] = int(conjunto['periodoInicial'])
    conjunto['periodoFinal'] = int(conjunto['periodoFinal'])
    conjunto['programa'] = int(conjunto['programa'])
    conjunto['encargado'] = session['user']['correo']

    tipo = conjunto.get('tipo', 'consulta')
    archivo = request.files.get('archivo')
    ruta = upload_folder+'/crudos'

    # Guardar archivo en Upload folder

    ############# ARCHIVO ##############
    if (archivo and archivo.filename and tipo == 'excel'):
        extension = '.'+archivo.filename.split('.')[1]
        # Guardar archivo de excel

        if extension not in ['.xls', '.xlsx']:
            return render_template('utils/mensaje.html', mensaje='Extension de archivo incorrecta: '+str(extension), submensaje='Solo se permiten archivos excel .xls & xlsx')

        # VERIFICACION de formato
        data = pd.read_excel(archivo)
        validacion, mensaje_error, data_verificada, periodoInicial = verify_data(
            data, conjunto.get('periodoInicial'), conjunto.get('periodoFinal'), conjunto.get('programa'))
        conjunto['periodoInicial'] = periodoInicial

        # Obtener nombre del conjunto desde el api
        nombre, numero = obtener_nombre_conjunto(conjunto)
        if not nombre:
            return numero
        archivo_guardar = 'C ' + nombre + '.xlsx'

        if validacion:
            try:
                data_verificada.to_excel(
                    ruta+'/'+archivo_guardar,
                    engine='openpyxl',
                    index=False
                )
            except Exception as e:
                error_logger.error(e)
                return render_template('utils/mensaje.html', mensaje='Ocurrió un error guardando el conjunto de datos')
        else:
            return render_template('utils/mensaje.html', mensaje='Incorrecto el formato de la fuente de datos', submensaje=mensaje_error)

    ############# CONSULTA ##############
    # elif tipo == 'consulta':
    else:
        # Obtener datos de los estudiantes en ese programas y periods
        endpoint_conjunto = 'desercion/estudiantes/student-set/{}/{}/{}'
        endpoint_conjunto_values = endpoint_conjunto.format(
            conjunto['programa'], conjunto['periodoInicial'], conjunto['periodoFinal'])
        status, body = get(endpoint_conjunto_values)
        if status:
            data = pd.DataFrame(body)
        else:
            return render_template('utils/mensaje.html', mensaje='Consulta fallida a la base de datos')

        # VERIFICACION de formato
        validacion, mensaje_error, data_verificada, periodoInicial = verify_data(
            data, conjunto.get('periodoInicial'), conjunto.get('periodoFinal'), conjunto.get('programa'))
        conjunto['periodoInicial'] = periodoInicial

        # Obtener nombre del conjunto desde el api
        nombre, numero = obtener_nombre_conjunto(conjunto)
        if not nombre:
            return numero
        archivo_guardar = 'C ' + nombre + '.xlsx'

        if validacion:
            # Guardar tabla sql como excel
            try:
                data_verificada.to_excel(
                    ruta+'/'+archivo_guardar,
                    engine='openpyxl',
                    index=False
                )
            except Exception as e:
                error_logger.error(e)
                return render_template('utils/mensaje.html', mensaje='Ocurrió un error guardando el conjunto de datos')
        else:
            return render_template('utils/mensaje.html', mensaje='Incorrecto el formato de la fuente de datos', submensaje=mensaje_error)
    # else:
    #     return render_template('utils/mensaje.html', mensaje='Formulario incorrecto', submensaje='Verifica el formulario de creacion o notifica al Administrador del sistema')

    # Guardar registro de conjunto en la BD
    conjunto['nombre'] = nombre
    conjunto['numero'] = numero
    status, body = post('conjuntos', conjunto)

    # TODO DEPRECATED! version 1 v1.5.0
    # if status:
    #     return redirect(url_for('StudentSet.crudos'))

    # TODO NEW! version 2 v2.0.0
    if status:
        # preparar() luego de post_save()
        return preparar(conjunto)

    return render_template('utils/mensaje.html', mensaje='No se pudo guardar el conjunto', submensaje=body)


@StudentSet.route('/preparar', methods=['POST'])
@login_required
def preparar(conjunto=None):
    if not conjunto:
        # Obtener Lo valores del formulario
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
    preparacion['preparador'] = session['user']['correo']
    preparacion['fechaInicial'] = get_now_date()
    # Obtener numero de preparacion para el conjunto
    status_p, body_p = get('preparaciones/nombre/'+nombre)
    if status_p:
        preparacion['numero'] = body_p['numero']
        preparacion['nombre'] = body_p['nombre']
    else:
        return render_template('utils/mensaje.html', mensaje='No se pudo obtener el consecutivo de la preparación para este conjunto', submensaje=body_p)

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
        exito, pagina_error = guardar_preparacion(
            preparacion, observaciones, 'Fallida')
        if not exito:
            return pagina_error
        return render_template('utils/mensaje.html', mensaje='la preparación falló')

    # Guardar archivo en Upload folder procesados
    archivo_procesado = 'P '+nombre+'.xls'
    ruta = upload_folder+'/procesados/'+archivo_procesado
    exito, pagina_error = guardar_archivo(data_preparada, ruta, 'excel')
    if not exito:
        return pagina_error

    # Guardar registro de preparacion en la BD
    exito, pagina_error = guardar_preparacion(preparacion, None, 'Exitosa')
    if not exito:
        return pagina_error

    ########### FIN PREPARAR ############

    # Actualizar conjunto de datos de crudo a procesado
    act_state = actualizar_state(nombre, 'Procesados')
    if act_state:
        return act_state

    # TODO DEPRECATED! version 1 v1.5.0
    # return redirect(url_for('StudentSet.procesados', conjunto=conjunto['nombre']))

    # TODO NEW! version 2 v2.0.0
    # ejecutar() luego de preparar()
    return ejecutar(conjunto)


@StudentSet.route('/ejecutar', methods=['POST'])
@login_required
def ejecutar(conjunto=None):
    ejecucion_guardada = False

    if not conjunto:
        # Obtener Lo valores del formulario
        body = dict(request.values)
        conjunto = literal_eval(body['conjunto'])

    nombre = conjunto['nombre']

    # Actualizar conjunto de datos de crudo a procesado
    act_state = actualizar_state(nombre, 'En Proceso')
    if act_state:
        return act_state

    # Crear prepraracion
    ejecucion = {}
    ejecucion['conjunto'] = conjunto['nombre']
    ejecucion['ejecutor'] = session['user']['correo']
    ejecucion['fechaInicial'] = get_now_date()

    # Obtener numero de ejecución para el conjunto
    status_p, body_p = get('ejecuciones/nombre/'+nombre)
    if status_p:
        ejecucion['nombre'] = body_p['nombre']
        ejecucion['numero'] = body_p['numero']
    else:
        return render_template('utils/mensaje.html', mensaje='No se pudo obtener el consecutivo de la preparación para este conjunto', submensaje=body_p)

    ########### EJECUTAR ############

    # Obtener archivo procesado
    archivo_procesado = 'P '+nombre
    ruta = upload_folder+'/procesados/'+archivo_procesado
    exito, data_preparada = obtener_archivo_excel(ruta)
    if not exito:
        return data_preparada

    # Algoritmo de ejecución
    # try:
    #     resultados_modelo,resultados_desertores = clasificador(data_preparada)
    # except Exception as e:
    #   pass
    try:
        resultados_modelo, resultados_desertores = execute_model(
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

        resultados = {'error': error_spa}
        exito, pagina_error = guardar_ejecucion(
            ejecucion, resultados, 'Fallida')
        ejecucion_guardada = True
        if not exito:
            return pagina_error
        act_state = actualizar_state(nombre, 'Procesados')
        if act_state:
            return act_state
        return render_template('utils/mensaje.html', mensaje='La ejecución falló', submensaje=error_spa)

    if not resultados_modelo:
        # Actualizar conjunto de datos de crudo a procesado
        act_state = actualizar_state(nombre, 'Procesados')
        if act_state:
            return act_state
        return render_template('utils/mensaje.html', mensaje='La ejecución falló', submensaje=resultados_desertores)

    # Guardar registro de los desertores en la BD del ies

    # Actualizar los resultados a ultimo
    endpoint_ultimo = 'desercion/resultados/ultimo/{}/{}'
    endpoint_ultimo_values = endpoint_ultimo.format(
        conjunto['programa'], conjunto['periodoFinal']
    )
    status_update, body_update = put(endpoint_ultimo_values, {})

    # Insertar los resultados
    if resultados_desertores.any().any():
        resultados_insert = json.loads(
            resultados_desertores.to_json(orient='records')
        )
        status_insert, body_insert = post(
            'desercion/resultados', resultados_insert
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

            return render_template('utils/mensaje.html', mensaje='Ocurrió un error insertando y/o actualizando los resultados'), 500

        state_ejecucion = 'Exitosa'
        # Guardar resultados de desertotres en Upload folder desertores
        archivo_desertores = 'D '+ejecucion['nombre']+'.json'
        ruta = upload_folder+'/desertores/'+archivo_desertores
        exito, pagina_error = guardar_archivo(
            resultados_modelo.pop('desertores'), ruta, 'json'
        )
        if not exito:
            return pagina_error

    else:
        # TODO data
        flash('<b>El modelo detectó 0 desertores, Deserción 0%</b>', 'danger')
        flash(
            'Revise si hay estudiantes ó desertores suficientes en el programa', 'warning'
        )
        resultados_modelo.pop('desertores')
        state_ejecucion = 'Fallida'
    # Guardar registro de ejecución en la BD
    if not ejecucion_guardada:
        exito, pagina_error = guardar_ejecucion(
            ejecucion=ejecucion, resultados=resultados_modelo, estado=state_ejecucion)
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
    # return redirect(url_for('Resultado.ejecuciones', conjunto=nombre))

    # TODO NEW! version 2 v2.0.0
    return redirect(url_for('Analista.modelos', modelo=nombre))
