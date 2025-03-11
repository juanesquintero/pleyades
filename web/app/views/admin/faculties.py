from flask import request, Blueprint, render_template
from ast import literal_eval

from web.app.views.auth import only_admin
from web.app.services.API import get

Faculty = Blueprint('Faculty', __name__)

endopoint = 'faculties/'


@Faculty.route('/')
@only_admin
def get_list():
    status, body = get(endopoint)
    if status:
        return render_template('admin/'+endopoint+'list.html', faculties=body)
    else:
        return render_template('admin/'+endopoint+'list.html', faculties=[], error=body)


@Faculty.route('/detail', methods=['POST'])
@only_admin
def detail():
    body = dict(request.values)
    faculty = literal_eval(body['faculty'])
    return render_template('admin/'+endopoint+'detail.html', f=faculty)
