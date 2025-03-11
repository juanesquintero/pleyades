from flask import request, Blueprint, render_template
from ast import literal_eval
from web.app.views.auth import only_admin
from web.app.services.API import get

Program = Blueprint('Program', __name__)

endopoint = 'programs/'


@Program.route('/')
@only_admin
def get_list():
    status, body = get(endopoint)
    if status:
        return render_template('admin/'+endopoint+'list.html', programs=body)
    else:
        return render_template('admin/'+endopoint+'list.html', programs=[], error=body)


@Program.route('/detail', methods=['POST'])
@only_admin
def detail():
    status_f, body_f = get('faculties')
    body = dict(request.values)
    program = literal_eval(body['program'])
    if status_f and body:
        return render_template('admin/'+endopoint+'detail.html', p=program, faculties=body_f,)
    else:
        return render_template('utils/message.html', message='Could Not load the programs y the faculties', submensaje=body_f)
