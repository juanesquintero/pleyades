import os
import json
from ast import literal_eval
from dotenv import load_dotenv
from flask import request, Blueprint, render_template, redirect, url_for


from views.auth import only_admin
from services.API import get, put, delete

from utils.mixins import *

load_dotenv()

endopoint = 'results/'

ResultadoAdmin = Blueprint('ResultadoAdmin', __name__)

upload_folder = os.getcwd()+'/uploads'


@ResultadoAdmin.route('/')
@ResultadoAdmin.route('/preparations')
@ResultadoAdmin.route('/preparations/<conjunto>')
@only_admin
def preparations(conjunto=None):
    if conjunto:
        return list_set('preparations', conjunto)
    return get_list('preparations')


@ResultadoAdmin.route('/executions')
@ResultadoAdmin.route('/executions/<conjunto>')
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


@ResultadoAdmin.route('/preparations/editar', methods=['POST'])
@only_admin
def editar_preparacion():
    body = dict(request.values)
    preparacion = literal_eval(body['preparacion'])
    preparacion['observaciones'] = json.dumps(preparacion['observaciones'])
    return render_template('admin/'+endopoint+'preparacion_editar.html', p=preparacion)


@ResultadoAdmin.route('/preparations/actualizar', methods=['POST'])
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
            return render_template('utils/mensaje.html', mensaje='No se pudo actualizar la preparación', submensaje='Error con el campo observaciones no es un json o nulo')

    status, body = put('preparations/'+nombre, preparacion)
    if status:
        return redirect(url_for('ResultadoAdmin.preparations'))
    else:
        return render_template('utils/mensaje.html', mensaje='No se pudo actualizar la preparación', submensaje=body)


@ResultadoAdmin.route('/preparations/borrar', methods=['POST'])
@only_admin
def borrar_preparacion():
    body = dict(request.values)
    preparacion = literal_eval(body['preparacion'])
    return render_template('admin/'+endopoint+'preparacion_borrar.html', p=preparacion)


@ResultadoAdmin.route('/preparations/eliminar', methods=['POST'])
@only_admin
def eliminar_preparacion():
    preparacion = dict(request.values)
    nombre = preparacion.pop('nombre')
    status, body = delete('preparations/'+nombre)
    if status:
        return redirect(url_for('ResultadoAdmin.preparations'))
    else:
        return render_template('utils/mensaje.html', mensaje='No se pudo Eliminar la preparación', submensaje=body)

########################################################### EJECUCIONES ###################################################################


@ResultadoAdmin.route('/executions/editar', methods=['POST'])
@only_admin
def editar_ejecucion():
    body = dict(request.values)
    ejecucion = literal_eval(body['ejecucion'])
    ejecucion['results'] = json.dumps(ejecucion['results'])
    return render_template('admin/'+endopoint+'ejecucion_editar.html', e=ejecucion)


@ResultadoAdmin.route('/executions/actualizar', methods=['POST'])
@only_admin
def actualizar_ejecucion():
    ejecucion = dict(request.values)
    nombre = ejecucion.pop('nombre')
    try:
        ejecucion['results'] = json.loads(
            ejecucion['results'].replace("'", '"'))
        ejecucion['results'] = dict(ejecucion['results'])
    except:
        return render_template('utils/mensaje.html', mensaje='No se pudo actualizar la ejecución', submensaje='Error con el campo results no es un json')

    status, body = put('executions/'+nombre, ejecucion)
    if status:
        return redirect(url_for('ResultadoAdmin.executions'))
    else:
        return render_template('utils/mensaje.html', mensaje='No se pudo actualizar la ejecución', submensaje=body)


@ResultadoAdmin.route('/executions/borrar', methods=['POST'])
@only_admin
def borrar_ejecucion():
    body = dict(request.values)
    ejecucion = literal_eval(body['ejecucion'])
    return render_template('admin/'+endopoint+'ejecucion_borrar.html', e=ejecucion)


@ResultadoAdmin.route('/executions/eliminar', methods=['POST'])
@only_admin
def eliminar_ejecucion():
    ejecucion = dict(request.values)
    nombre = ejecucion.pop('nombre')
    status, body = delete('executions/'+nombre)
    if status:
        # Borrar archivo
        if ejecucion['estado'] == 'Exitosa':
            exito, pagina_error = eliminar_archivo(
                upload_folder+'/desertores/'+'D '+nombre+'.json')
            if not (exito):
                return pagina_error
            eliminar_archivo(upload_folder+'/desertores/'+'D '+nombre+'.xls')

        return redirect(url_for('ResultadoAdmin.executions'))
    else:
        return render_template('utils/mensaje.html', mensaje='No se pudo Eliminar la ejecución', submensaje=body)
