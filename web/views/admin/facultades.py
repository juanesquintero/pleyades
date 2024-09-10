from flask import request, Blueprint, render_template
from ast import literal_eval

from views.auth import only_admin
from services.API import get

Facultad = Blueprint('Facultad', __name__)

endopoint = 'facultades/'


@Facultad.route('/')
@only_admin
def listar():
    status, body = get(endopoint)
    if status:
        return render_template('admin/'+endopoint+'listar.html', facultades=body)
    else:
        return render_template('admin/'+endopoint+'listar.html', facultades=[], error=body)


@Facultad.route('/detalle', methods=['POST'])
@only_admin
def detalle():
    body = dict(request.values)
    facultad = literal_eval(body['facultad'])
    return render_template('admin/'+endopoint+'detalle.html', f=facultad)
