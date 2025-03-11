from flask import request, Blueprint, render_template
from web.app.views.auth import only_admin
from web.app.services.API import get

Student = Blueprint('Student', __name__)

endopoint = 'students/'


@Student.route('/')
@only_admin
def get_list():
    status, body = get('programs')
    if status:
        return render_template('admin/'+endopoint+'list.html', programs=body)
    return render_template('admin/'+endopoint+'list.html', programs=[], error=body)


@Student.route('/detail', methods=['POST'])
@only_admin
def detail():
    form = dict(request.values)
    program_id = form.get('id')
    program_name = form.get('name')
    status, body = get(f'desertion/students/program/{program_id}')
    if status:
        return render_template(
            'admin/'+endopoint+'detail.html',
            students=body,
            program=program_name
        )
    return render_template(
        'admin/'+endopoint+'detail.html',
        students=[],
        error=body,
        program=program_name
    )
