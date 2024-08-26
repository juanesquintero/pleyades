from flask import request, Blueprint, render_template
from ast import literal_eval
from views.auth import only_admin
from services.API import get

Programa = Blueprint('Programa', __name__)

endopoint = 'programas/'


@Programa.route('/')
@only_admin
def listar():
    status, body = get(endopoint)
    if status:
        return render_template('admin/'+endopoint+'listar.html', programas=body)
    else:
        return render_template('admin/'+endopoint+'listar.html', programas=[], error=body)


@Programa.route('/detalle', methods=['POST'])
@only_admin
def detalle():
    status_f, body_f = get('facultades')
    body = dict(request.values)
    programa = literal_eval(body['programa'])
    if status_f and body:
        return render_template('admin/'+endopoint+'detalle.html', p=programa, facultades=body_f,)
    else:
        return render_template('utils/mensaje.html', mensaje='No se pudieron cargar las programas y las facultades', submensaje=body_f)
