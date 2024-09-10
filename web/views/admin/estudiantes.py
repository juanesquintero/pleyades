from flask import request, Blueprint, render_template
from views.auth import only_admin
from services.API import get

Estudiante = Blueprint('Estudiante', __name__)

endopoint = 'estudiantes/'


@Estudiante.route('/')
@only_admin
def listar():
    status, body = get('programas')
    if status:
        return render_template('admin/'+endopoint+'listar.html', programas=body)
    return render_template('admin/'+endopoint+'listar.html', programas=[], error=body)


@Estudiante.route('/detalle', methods=['POST'])
@only_admin
def detalle():
    form = dict(request.values)
    idprograma = form.get('idprograma')
    programa = form.get('programa')
    status, body = get(f'desercion/estudiantes/programa/{idprograma}')
    if status:
        return render_template('admin/'+endopoint+'detalle.html', estudiantes=body, programa=programa)
    return render_template('admin/'+endopoint+'detalle.html', estudiantes=[], error=body, programa=programa)
