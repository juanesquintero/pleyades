import os
import pandas as pd
from dotenv import load_dotenv
from flask import request, session, Blueprint, render_template, send_file
from views.auth import login_required
from services.API import get
from utils.mixins import save_archivo, obtener_archivo_json, set_date_format

load_dotenv()

endopoint = 'results/'

Result = Blueprint('Result', __name__)

upload_folder = os.getcwd()+'/uploads'


@Result.route('/preparations')
@Result.route('/preparations/<conjunto>')
@login_required
def preparations(conjunto=None):
    if conjunto:
        return list_set('preparations', conjunto)
    return get_list('preparations')


@Result.route('/executions')
@Result.route('/executions/<conjunto>')
@login_required
def executions(conjunto=None):
    if conjunto:
        return list_set('executions', conjunto)
    return get_list('executions')


def get_list(results):
    rol = 'preparador' if results == 'preparations' else 'ejecutor'
    status, body = get(results+'/'+rol+'/'+session.get('user')['correo'])
    if status:
        return render_template(endopoint+results+'.html', results=set_date_format(body))
    else:
        return render_template(endopoint+results+'.html', results=[], error=body)


def list_set(results, conjunto):
    status, body = get(results+'/set/'+conjunto)
    if status:
        return render_template(endopoint+results+'.html', results=set_date_format(body))
    else:
        return render_template(endopoint+results+'.html', results=[], error=body)


@Result.route('/execution/detalle', methods=['POST'])
@login_required
def ejecucion_detalle():
    body = dict(request.values)
    execution = body['execution']

    # Obtener el archivo de desertores
    archivo = 'D '+execution
    ruta = upload_folder+'/deserters/'+archivo
    exito, deserters = obtener_archivo_json(ruta)

    status, body = get('executions/'+execution)

    if status and exito:
        del body['precision_model']
        del body['numero']
        return render_template(endopoint+'ejecucion_detalle.html', deserters=deserters, results=body.pop('results'), execution=body)
    elif status and not (exito):
        if body['status'] == 'Fallida':
            del body['precision_model']
            del body['numero']
            return render_template(
                endopoint+'ejecucion_detalle.html',
                deserters=None,
                results=body.pop('results'),
                execution=body
            )
        else:
            return deserters
    else:
        return render_template(
            'utils/message.html',
            message='No se obtener la ejecución',
            submensaje=body
        )


@Result.route('/preparacion/detalle', methods=['POST'])
@login_required
def preparacion_detalle():
    body = dict(request.values)
    preparacion = body['preparacion']
    status, body = get('preparations/'+preparacion)

    if status:
        del body['numero']
        return render_template(
            endopoint+'preparacion_detalle.html',
            observaciones=body.pop('observaciones'),
            p=body
        )
    else:
        return render_template(
            'utils/message.html',
            message='No se obtener los resultaods de la ejecución',
            submensaje=body
        )


@Result.route('/donwload/deserters/<execution>', methods=['GET'])
@login_required
def download(execution):
    status_c, body_c = get('executions/'+execution)
    if not status_c:
        return render_template('utils/message.html', message='No existe esa ejecución')

    archivo = 'D '+execution
    ruta = upload_folder+'/deserters/'+archivo
    try:
        data = pd.read_json(ruta+'.json')
    except Exception as e:
        return render_template(
            'utils/message.html',
            message='No se pudo abrir el archivo de desertores:',
            submensaje=str(e)
        )

    exito, pagina_error = save_archivo(data, ruta+'.xls', 'excel')
    if not (exito):
        return pagina_error

    return send_file(ruta+'.xls', as_attachment=True)
