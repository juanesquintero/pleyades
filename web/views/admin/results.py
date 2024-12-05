import os
import json
from ast import literal_eval
from dotenv import load_dotenv
from flask import request, Blueprint, render_template, redirect, url_for


from views.auth import only_admin
from services.API import get, put, delete

from utils.mixins import remove_file

load_dotenv()

endopoint = 'results/'

ResultAdmin = Blueprint('ResultAdmin', __name__)

upload_folder = os.getcwd()+'/uploads'


@ResultAdmin.route('/')
@ResultAdmin.route('/preparations')
@ResultAdmin.route('/preparations/<conjunto>')
@only_admin
def preparations(conjunto=None):
    if conjunto:
        return list_set('preparations', conjunto)
    return get_list('preparations')


@ResultAdmin.route('/executions')
@ResultAdmin.route('/executions/<conjunto>')
@only_admin
def executions(conjunto=None):
    if conjunto:
        return list_set('executions', conjunto)
    return get_list('executions')


def get_list(results):
    status, body = get(results)
    if status:
        return render_template('admin/'+endopoint+results+'.html', results=body)
    else:
        return render_template('admin/'+endopoint+results+'.html', results=[], error=body)


def list_set(results, conjunto):
    status, body = get(results+'/set/'+conjunto)
    if status:
        return render_template('admin/'+endopoint+results+'.html', results=body)
    else:
        return render_template('admin/'+endopoint+results+'.html', results=[], error=body)

########################################################### PREPARACIONES ###################################################################


@ResultAdmin.route('/preparations/editar', methods=['POST'])
@only_admin
def editar_preparacion():
    body = dict(request.values)
    preparacion = literal_eval(body['preparacion'])
    preparacion['observaciones'] = json.dumps(preparacion['observaciones'])
    return render_template('admin/'+endopoint+'preparacion_editar.html', p=preparacion)


@ResultAdmin.route('/preparations/actualizar', methods=['POST'])
@only_admin
def actualizar_preparacion():
    preparacion = dict(request.values)
    nombre = preparacion.pop('nombre')
    if preparacion['observaciones'].lower().strip() in ['none', 'nulo', 'null', '']:
        preparacion['observaciones'] = None
    else:
        try:
            preparacion['observaciones'] = json.loads(
                preparacion['observaciones'].replace("'", '"'))
            preparacion['observaciones'] = dict(preparacion['observaciones'])
        except:
            return render_template('utils/message.html', message='No se pudo actualizar la preparación', submensaje='Error con el campo observaciones no es un json o nulo')

    status, body = put('preparations/'+nombre, preparacion)
    if status:
        return redirect(url_for('ResultAdmin.preparations'))
    else:
        return render_template('utils/message.html', message='No se pudo actualizar la preparación', submensaje=body)


@ResultAdmin.route('/preparations/borrar', methods=['POST'])
@only_admin
def borrar_preparacion():
    body = dict(request.values)
    preparacion = literal_eval(body['preparacion'])
    return render_template('admin/'+endopoint+'preparacion_borrar.html', p=preparacion)


@ResultAdmin.route('/preparations/remove', methods=['POST'])
@only_admin
def delete_preparacion():
    preparacion = dict(request.values)
    nombre = preparacion.pop('nombre')
    status, body = delete('preparations/'+nombre)
    if status:
        return redirect(url_for('ResultAdmin.preparations'))

    return render_template('utils/message.html', message='No se pudo Eliminar la preparación', submensaje=body)

########################################################### EJECUCIONES ###################################################################


@ResultAdmin.route('/executions/editar', methods=['POST'])
@only_admin
def editar_ejecucion():
    body = dict(request.values)
    execution = literal_eval(body['execution'])
    execution['results'] = json.dumps(execution['results'])
    return render_template('admin/'+endopoint+'ejecucion_editar.html', e=execution)


@ResultAdmin.route('/executions/actualizar', methods=['POST'])
@only_admin
def actualizar_ejecucion():
    execution = dict(request.values)
    nombre = execution.pop('nombre')
    try:
        execution['results'] = json.loads(
            execution['results'].replace("'", '"'))
        execution['results'] = dict(execution['results'])
    except:
        return render_template(
            'utils/message.html',
            message='No se pudo actualizar la ejecución', submensaje='Error con el campo results no es un json'
        )

    status, body = put('executions/'+nombre, execution)
    if status:
        return redirect(url_for('ResultAdmin.executions'))

    return render_template(
        'utils/message.html',
        message='No se pudo actualizar la ejecución',
        submensaje=body
    )


@ResultAdmin.route('/executions/borrar', methods=['POST'])
@only_admin
def borrar_ejecucion():
    body = dict(request.values)
    execution = literal_eval(body['execution'])
    return render_template('admin/'+endopoint+'ejecucion_borrar.html', e=execution)


@ResultAdmin.route('/executions/remove', methods=['POST'])
@only_admin
def delete_ejecucion():
    execution = dict(request.values)
    nombre = execution.pop('nombre')
    status, body = delete('executions/'+nombre)
    if status:
        # Borrar archivo
        if execution['status'] == 'Exitosa':
            exito, pagina_error = remove_file(
                upload_folder+'/deserters/'+'D '+nombre+'.json')
            if not (exito):
                return pagina_error
            remove_file(upload_folder+'/deserters/'+'D '+nombre+'.xls')

        return redirect(url_for('ResultAdmin.executions'))

    return render_template('utils/message.html', message='No se pudo Eliminar la ejecución', submensaje=body)
