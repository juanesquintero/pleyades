import os
import pandas as pd
from dotenv import load_dotenv
from flask import request, session, Blueprint, render_template, send_file
from views.auth import login_required
from services.API import get
from utils.mixins import guardar_archivo, obtener_archivo_json, set_date_format

load_dotenv()

endopoint = 'results/'

Resultado = Blueprint('Resultado', __name__)

upload_folder = os.getcwd()+'/uploads'


@Resultado.route('/preparaciones')
@Resultado.route('/preparaciones/<conjunto>')
@login_required
def preparaciones(conjunto=None):
    if conjunto:
        return list_set('preparaciones', conjunto)
    return get_list('preparaciones')


@Resultado.route('/ejecuciones')
@Resultado.route('/ejecuciones/<conjunto>')
@login_required
def ejecuciones(conjunto=None):
    if conjunto:
        return list_set('ejecuciones', conjunto)
    return get_list('ejecuciones')


def get_list(results):
    rol = 'preparador' if results == 'preparaciones' else 'ejecutor'
    status, body = get(results+'/'+rol+'/'+session['user']['correo'])
    if status:
        return render_template(endopoint+results+'.html', results=set_date_format(body))
    else:
        return render_template(endopoint+results+'.html', results=[], error=body)


def list_set(results, conjunto):
    status, body = get(results+'/student-set/'+conjunto)
    if status:
        return render_template(endopoint+results+'.html', results=set_date_format(body))
    else:
        return render_template(endopoint+results+'.html', results=[], error=body)


@Resultado.route('/ejecucion/detalle', methods=['POST'])
@login_required
def ejecucion_detalle():
    body = dict(request.values)
    ejecucion = body['ejecucion']

    # Obtener el archivo de desertores
    archivo = 'D '+ejecucion
    ruta = upload_folder+'/desertores/'+archivo
    exito, desertores = obtener_archivo_json(ruta)

    status, body = get('ejecuciones/'+ejecucion)

    if status and exito:
        del body['precision_modelo']
        del body['numero']
        return render_template(endopoint+'ejecucion_detalle.html', desertores=desertores, results=body.pop('results'), ejecucion=body)
    elif status and not (exito):
        if body['estado'] == 'Fallida':
            del body['precision_modelo']
            del body['numero']
            return render_template(
                endopoint+'ejecucion_detalle.html',
                desertores=None,
                results=body.pop('results'),
                ejecucion=body
            )
        else:
            return desertores
    else:
        return render_template(
            'utils/mensaje.html',
            mensaje='No se obtener la ejecución',
            submensaje=body
        )


@Resultado.route('/preparacion/detalle', methods=['POST'])
@login_required
def preparacion_detalle():
    body = dict(request.values)
    preparacion = body['preparacion']
    status, body = get('preparaciones/'+preparacion)

    if status:
        del body['numero']
        return render_template(
            endopoint+'preparacion_detalle.html',
            observaciones=body.pop('observaciones'),
            p=body
        )
    else:
        return render_template(
            'utils/mensaje.html',
            mensaje='No se obtener los resultaods de la ejecución',
            submensaje=body
        )


@Resultado.route('/descargar/desertores/<ejecucion>', methods=['GET'])
@login_required
def download(ejecucion):
    status_c, body_c = get('ejecuciones/'+ejecucion)
    if not status_c:
        return render_template('utils/mensaje.html', mensaje='No existe esa ejecución')

    archivo = 'D '+ejecucion
    ruta = upload_folder+'/desertores/'+archivo
    try:
        data = pd.read_json(ruta+'.json')
    except Exception as e:
        return render_template(
            'utils/mensaje.html',
            mensaje='No se pudo abrir el archivo de desertores:',
            submensaje=str(e)
        )

    exito, pagina_error = guardar_archivo(data, ruta+'.xls', 'excel')
    if not (exito):
        return pagina_error

    return send_file(ruta+'.xls', as_attachment=True)
