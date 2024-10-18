from flask import request, Blueprint, render_template
from ast import literal_eval

from views.auth import only_admin
from services.API import get

Faculty = Blueprint('Faculty', __name__)

endopoint = 'faculties/'


@Faculty.route('/')
@only_admin
def get_list():
    status, body = get(endopoint)
    if status:
        return render_template('admin/'+endopoint+'listar.html', faculties=body)
    else:
        return render_template('admin/'+endopoint+'listar.html', faculties=[], error=body)


@Faculty.route('/detalle', methods=['POST'])
@only_admin
def detalle():
    body = dict(request.values)
    facultad = literal_eval(body['facultad'])
    return render_template('admin/'+endopoint+'detalle.html', f=facultad)
