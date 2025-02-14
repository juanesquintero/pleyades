import os
import json
from ast import literal_eval
from dotenv import load_dotenv
from flask import request, Blueprint, render_template, redirect, url_for


from web.views.auth import only_admin
from web.services.API import get, put, delete

from web.utils.mixins import remove_file

load_dotenv()

endopoint = 'results/'

ResultAdmin = Blueprint('ResultAdmin', __name__)

upload_folder = os.getcwd()+'/uploads'


@ResultAdmin.route('/')
@ResultAdmin.route('/preparations')
@ResultAdmin.route('/preparations/<dataset>')
@only_admin
def preparations(dataset=None):
    if dataset:
        return list_set('preparations', dataset)
    return get_list('preparations')


@ResultAdmin.route('/executions')
@ResultAdmin.route('/executions/<dataset>')
@only_admin
def executions(dataset=None):
    if dataset:
        return list_set('executions', dataset)
    return get_list('executions')


def get_list(results):
    status, body = get(results)
    if status:
        return render_template('admin/'+endopoint+results+'.html', results=body)
    else:
        return render_template('admin/'+endopoint+results+'.html', results=[], error=body)


def list_set(results, dataset):
    status, body = get(results+'/dataset/'+dataset)
    if status:
        return render_template('admin/'+endopoint+results+'.html', results=body)
    else:
        return render_template('admin/'+endopoint+results+'.html', results=[], error=body)

########################################################### PREPARACIONES ###################################################################


@ResultAdmin.route('/preparations/editar', methods=['POST'])
@only_admin
def editar_preparation():
    body = dict(request.values)
    preparation = literal_eval(body['preparation'])
    preparation['observaciones'] = json.dumps(preparation['observaciones'])
    return render_template('admin/'+endopoint+'preparation_editar.html', p=preparation)


@ResultAdmin.route('/preparations/update', methods=['POST'])
@only_admin
def update_preparation():
    preparation = dict(request.values)
    name = preparation.pop('name')
    if preparation['observaciones'].lower().strip() in ['none', 'nulo', 'null', '']:
        preparation['observaciones'] = None
    else:
        try:
            preparation['observaciones'] = json.loads(
                preparation['observaciones'].replace("'", '"'))
            preparation['observaciones'] = dict(preparation['observaciones'])
        except:
            return render_template('utils/message.html', message='No se pudo update la preparación', submensaje='Error con el campo observaciones no es un json o nulo')

    status, body = put('preparations/'+name, preparation)
    if status:
        return redirect(url_for('ResultAdmin.preparations'))
    else:
        return render_template('utils/message.html', message='No se pudo update la preparación', submensaje=body)


@ResultAdmin.route('/preparations/delete', methods=['POST'])
@only_admin
def delete_preparation():
    body = dict(request.values)
    preparation = literal_eval(body['preparation'])
    return render_template('admin/'+endopoint+'preparation_borrar.html', p=preparation)


@ResultAdmin.route('/preparations/remove', methods=['POST'])
@only_admin
def remove_preparation():
    preparation = dict(request.values)
    name = preparation.pop('name')
    status, body = delete('preparations/'+name)
    if status:
        return redirect(url_for('ResultAdmin.preparations'))

    return render_template('utils/message.html', message='No se pudo Eliminar la preparación', submensaje=body)

########################################################### EJECUCIONES ###################################################################


@ResultAdmin.route('/executions/editar', methods=['POST'])
@only_admin
def editar_execution():
    body = dict(request.values)
    execution = literal_eval(body['execution'])
    execution['results'] = json.dumps(execution['results'])
    return render_template('admin/'+endopoint+'execution_editar.html', e=execution)


@ResultAdmin.route('/executions/update', methods=['POST'])
@only_admin
def update_execution():
    execution = dict(request.values)
    name = execution.pop('name')
    try:
        execution['results'] = json.loads(
            execution['results'].replace("'", '"'))
        execution['results'] = dict(execution['results'])
    except:
        return render_template(
            'utils/message.html',
            message='No se pudo update la ejecución', submensaje='Error con el campo results no es un json'
        )

    status, body = put('executions/'+name, execution)
    if status:
        return redirect(url_for('ResultAdmin.executions'))

    return render_template(
        'utils/message.html',
        message='No se pudo update la ejecución',
        submensaje=body
    )


@ResultAdmin.route('/executions/delete', methods=['POST'])
@only_admin
def delete_execution():
    body = dict(request.values)
    execution = literal_eval(body['execution'])
    return render_template('admin/'+endopoint+'execution_remove.html', e=execution)


@ResultAdmin.route('/executions/remove', methods=['POST'])
@only_admin
def remove_execution():
    execution = dict(request.values)
    name = execution.pop('name')
    status, body = delete('executions/'+name)
    if status:
        # Borrar file
        if execution['status'] == 'Successful':
            exito, pagina_error = remove_file(
                upload_folder+'/deserters/'+'D '+name+'.json')
            if not (exito):
                return pagina_error
            remove_file(upload_folder+'/deserters/'+'D '+name+'.xls')

        return redirect(url_for('ResultAdmin.executions'))

    return render_template('utils/message.html', message='No se pudo Eliminar la ejecución', submensaje=body)
