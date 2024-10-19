from flask import request, Blueprint, render_template
from views.auth import only_admin
from services.API import get

Student = Blueprint('Student', __name__)

endopoint = 'students/'


@Student.route('/')
@only_admin
def get_list():
    status, body = get('programs')
    if status:
        return render_template('admin/'+endopoint+'listar.html', programs=body)
    return render_template('admin/'+endopoint+'listar.html', programs=[], error=body)


@Student.route('/detalle', methods=['POST'])
@only_admin
def detalle():
    form = dict(request.values)
    idprograma = form.get('idprograma')
    programa = form.get('programa')
    status, body = get(f'desertion/students/programa/{idprograma}')
    if status:
        return render_template(
            'admin/'+endopoint+'detalle.html',
            students=body,
            programa=programa
        )
    return render_template(
        'admin/'+endopoint+'detalle.html',
        students=[],
        error=body,
        programa=programa
    )
