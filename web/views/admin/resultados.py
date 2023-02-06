from flask import request, session, Blueprint, render_template, redirect, send_file, url_for
from dotenv import load_dotenv
from ast import literal_eval
from datetime import datetime
import os, json, pandas as pd

from views.auth import only_admin
from services.API import get, post, put, delete

from utils.mixins import *

load_dotenv()

endopoint = 'resultados/'

ResultadoAdmin = Blueprint('ResultadoAdmin', __name__)

upload_folder = os.getcwd()+'/uploads'

@ResultadoAdmin.route('/')
@ResultadoAdmin.route('/preparaciones')
@ResultadoAdmin.route('/preparaciones/<conjunto>')
@only_admin
def preparaciones(conjunto=None):
    if conjunto:
        return listar_conjunto('preparaciones', conjunto)
    return listar('preparaciones')

@ResultadoAdmin.route('/ejecuciones')
@ResultadoAdmin.route('/ejecuciones/<conjunto>')
@only_admin
def ejecuciones(conjunto=None):
    if conjunto:
        return listar_conjunto('ejecuciones',conjunto)
    return listar('ejecuciones')

def listar(resultados):
    status, body = get(resultados)
    if status:
        return render_template('admin/'+endopoint+resultados+'.html', resultados=body)
    else:
        return render_template('admin/'+endopoint+resultados+'.html', resultados=[], error=body)

def listar_conjunto(resultados, conjunto):
    status, body = get(resultados+'/conjunto/'+conjunto)
    if status:
        return render_template('admin/'+endopoint+resultados+'.html', resultados=body)
    else:
        return render_template('admin/'+endopoint+resultados+'.html', resultados=[], error=body)

########################################################### PREPARACIONES ###################################################################
@ResultadoAdmin.route('/preparaciones/editar',methods=['POST'])
@only_admin
def editar_preparacion():
    body = dict(request.values)
    preparacion = literal_eval(body['preparacion'])
    preparacion['observaciones'] = json.dumps(preparacion['observaciones'])
    return render_template('admin/'+endopoint+'preparacion_editar.html', p=preparacion)

@ResultadoAdmin.route('/preparaciones/actualizar',methods=['POST'])
@only_admin
def actualizar_preparacion():
    preparacion = dict(request.values)
    nombre = preparacion.pop('nombre') 
    if preparacion['observaciones'].lower().strip() in ['none', 'nulo', 'null', '']:
        preparacion['observaciones'] = None
    else:
        try:
            preparacion['observaciones']  = json.loads(preparacion['observaciones'].replace("'",'"'))
            preparacion['observaciones']  = dict(preparacion['observaciones'])
        except:
            return render_template('utils/mensaje.html', mensaje='No se pudo actualizar la preparación', submensaje='Error con el campo observaciones no es un json o nulo')
    
    status,body = put('preparaciones/'+nombre,preparacion)
    if status:
        return redirect(url_for('ResultadoAdmin.preparaciones'))
    else:
        return render_template('utils/mensaje.html', mensaje='No se pudo actualizar la preparación', submensaje=body)

@ResultadoAdmin.route('/preparaciones/borrar',methods=['POST'])
@only_admin
def borrar_preparacion():
    body = dict(request.values)
    preparacion = literal_eval(body['preparacion'])
    return render_template('admin/'+endopoint+'preparacion_borrar.html', p=preparacion)

@ResultadoAdmin.route('/preparaciones/eliminar',methods=['POST'])
@only_admin
def eliminar_preparacion():
    preparacion = dict(request.values)
    nombre = preparacion.pop('nombre') 
    status,body = delete('preparaciones/'+nombre)
    if status:
        return redirect(url_for('ResultadoAdmin.preparaciones'))
    else:
        return render_template('utils/mensaje.html', mensaje='No se pudo Eliminar la preparación', submensaje=body)

########################################################### EJECUCIONES ###################################################################

@ResultadoAdmin.route('/ejecuciones/editar',methods=['POST'])
@only_admin
def editar_ejecucion():
    body = dict(request.values)
    ejecucion = literal_eval(body['ejecucion'])
    ejecucion['resultados'] = json.dumps(ejecucion['resultados'])
    return render_template('admin/'+endopoint+'ejecucion_editar.html', e=ejecucion)

@ResultadoAdmin.route('/ejecuciones/actualizar',methods=['POST'])
@only_admin
def actualizar_ejecucion():
    ejecucion = dict(request.values)
    nombre = ejecucion.pop('nombre') 
    try:
        ejecucion['resultados']  = json.loads(ejecucion['resultados'].replace("'",'"'))
        ejecucion['resultados']  = dict(ejecucion['resultados'])
    except:
        return render_template('utils/mensaje.html', mensaje='No se pudo actualizar la ejecución', submensaje='Error con el campo resultados no es un json')
    
    status,body = put('ejecuciones/'+nombre,ejecucion)
    if status:
        return redirect(url_for('ResultadoAdmin.ejecuciones'))
    else:
        return render_template('utils/mensaje.html', mensaje='No se pudo actualizar la ejecución', submensaje=body)


@ResultadoAdmin.route('/ejecuciones/borrar',methods=['POST'])
@only_admin
def borrar_ejecucion():
    body = dict(request.values)
    ejecucion = literal_eval(body['ejecucion'])
    return render_template('admin/'+endopoint+'ejecucion_borrar.html', e=ejecucion)

@ResultadoAdmin.route('/ejecuciones/eliminar',methods=['POST'])
@only_admin
def eliminar_ejecucion():
    ejecucion = dict(request.values)
    nombre = ejecucion.pop('nombre') 
    status,body = delete('ejecuciones/'+nombre)
    if status:
        # Borrar archivo 
        if ejecucion['estado'] == 'Exitosa':
            exito,pagina_error = eliminar_archivo(upload_folder+'/desertores/'+'D '+nombre+'.json')
            if not(exito): return pagina_error
            eliminar_archivo(upload_folder+'/desertores/'+'D '+nombre+'.xls')

        return redirect(url_for('ResultadoAdmin.ejecuciones'))
    else:
        return render_template('utils/mensaje.html', mensaje='No se pudo Eliminar la ejecución', submensaje=body)