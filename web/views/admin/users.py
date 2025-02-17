from flask import request, Blueprint, render_template, redirect, url_for
from ast import literal_eval

from web.views.auth import only_admin
from web.services.API import get, post, put, delete

User = Blueprint('User', __name__, template_folder='/users')

endopoint = 'users/'


@User.route('/')
@only_admin
def get_list():
    status, body = get(endopoint)
    if status:
        return render_template('admin/'+endopoint+'list.html', users=body)
    return render_template('admin/'+endopoint+'list.html', users=[], error=body)


@User.route('/create')
@only_admin
def post_create():
    return render_template('admin/'+endopoint+'create.html')


@User.route('/create', methods=['POST'])
@only_admin
def post_save():
    usuario = dict(request.values)
    status, body = post(endopoint, usuario)
    if status:
        return redirect(url_for('User.get_list'))
    else:
        return render_template('utils/message.html', message='Can Not pudo save el User', submensaje=body)


@User.route('/edit', methods=['POST'])
@only_admin
def post_edit():
    body = dict(request.values)
    usuario = literal_eval(body['usuario'])
    if usuario:
        return render_template('admin/'+endopoint+'edit.html', u=usuario)
    else:
        return render_template('utils/message.html', message='Can Not pudo cargar el usuario')


@User.route('/update', methods=['POST'])
@only_admin
def update():
    usuario = dict(request.values)
    if 'password' in usuario.keys():
        if len(usuario['password']) < 8:
            del usuario['password']

    email = usuario.pop('email', '')
    status, body = put(endopoint+email, usuario)
    if status:
        return redirect(url_for('User.get_list'))

    return render_template('utils/message.html', message='Can Not pudo update el User', submensaje=body)


@User.route('/delete', methods=['POST'])
@only_admin
def remove():
    body = dict(request.values)
    usuario = literal_eval(body['usuario'])
    if usuario:
        return render_template('admin/'+endopoint+'delete.html', u=usuario)
    else:
        return render_template('utils/message.html', message='Can Not pudo update el User')


@User.route('/remove', methods=['POST'])
@only_admin
def post_delete():
    usuario = dict(request.values)
    email = usuario.pop('email', '')
    status, body = delete(endopoint+email)
    if status:
        return redirect(url_for('User.get_list'))
    else:
        return render_template('utils/message.html', message='Can Not pudo Eliminar el User', submensaje=body)
