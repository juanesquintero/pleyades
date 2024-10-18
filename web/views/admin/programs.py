from flask import request, Blueprint, render_template
from ast import literal_eval
from views.auth import only_admin
from services.API import get

Program = Blueprint('Program', __name__)

endopoint = 'programs/'


@Program.route('/')
@only_admin
def get_list():
    status, body = get(endopoint)
    if status:
        return render_template('admin/'+endopoint+'listar.html', programs=body)
    else:
        return render_template('admin/'+endopoint+'listar.html', programs=[], error=body)


@Program.route('/detalle', methods=['POST'])
@only_admin
def detalle():
    status_f, body_f = get('faculties')
    body = dict(request.values)
    programa = literal_eval(body['programa'])
    if status_f and body:
        return render_template('admin/'+endopoint+'detalle.html', p=programa, faculties=body_f,)
    else:
        return render_template('utils/mensaje.html', mensaje='No se pudieron cargar las programs y las faculties', submensaje=body_f)
