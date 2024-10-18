from flask import request, Blueprint, render_template, redirect, url_for
from ast import literal_eval

from views.auth import only_admin
from services.API import get, post, put, delete

User = Blueprint('User', __name__, template_folder='/users')

endopoint = 'users/'


@User.route('/')
@only_admin
def get_list():
    status, body = get(endopoint)
    if status:
        return render_template('admin/'+endopoint+'listar.html', users=body)
    return render_template('admin/'+endopoint+'listar.html', users=[], error=body)


@User.route('/crear')
@only_admin
def post_create():
    return render_template('admin/'+endopoint+'crear.html')


@User.route('/crear', methods=['POST'])
@only_admin
def post_save():
    usuario = dict(request.values)
    status, body = post(endopoint, usuario)
    if status:
        return redirect(url_for('User.get_list'))
    else:
        return render_template('utils/mensaje.html', mensaje='No se pudo save el User', submensaje=body)


@User.route('/editar', methods=['POST'])
@only_admin
def post_edit():
    body = dict(request.values)
    usuario = literal_eval(body['usuario'])
    if usuario:
        return render_template('admin/'+endopoint+'editar.html', u=usuario)
    else:
        return render_template('utils/mensaje.html', mensaje='No se pudo cargar el usuario')


@User.route('/actualizar', methods=['POST'])
@only_admin
def update():
    usuario = dict(request.values)
    if 'clave' in usuario.keys():
        if len(usuario['clave']) < 8:
            del usuario['clave']

    correo = usuario.pop('correo', '')
    status, body = put(endopoint+correo, usuario)
    if status:
        return redirect(url_for('User.get_list'))
    else:
        return render_template('utils/mensaje.html', mensaje='No se pudo actualizar el User', submensaje=body)


@User.route('/borrar', methods=['POST'])
@only_admin
def remove():
    body = dict(request.values)
    usuario = literal_eval(body['usuario'])
    if usuario:
        return render_template('admin/'+endopoint+'borrar.html', u=usuario)
    else:
        return render_template('utils/mensaje.html', mensaje='No se pudo actualizar el User')


@User.route('/eliminar', methods=['POST'])
@only_admin
def post_delete():
    usuario = dict(request.values)
    correo = usuario.pop('correo', '')
    status, body = delete(endopoint+correo)
    if status:
        return redirect(url_for('User.get_list'))
    else:
        return render_template('utils/mensaje.html', mensaje='No se pudo Eliminar el User', submensaje=body)
