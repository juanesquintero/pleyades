from flask import request, Blueprint, render_template, redirect, url_for
from ast import literal_eval

from views.auth import only_admin
from services.API import get, post, put, delete

Usuario = Blueprint('Usuario', __name__, template_folder='/usuarios')

endopoint = 'usuarios/'


@Usuario.route('/')
@only_admin
def get_list():
    status, body = get(endopoint)
    if status:
        return render_template('admin/'+endopoint+'listar.html', usuarios=body)
    return render_template('admin/'+endopoint+'listar.html', usuarios=[], error=body)


@Usuario.route('/crear')
@only_admin
def post_create():
    return render_template('admin/'+endopoint+'crear.html')


@Usuario.route('/crear', methods=['POST'])
@only_admin
def post_save():
    usuario = dict(request.values)
    status, body = post(endopoint, usuario)
    if status:
        return redirect(url_for('Usuario.listar'))
    else:
        return render_template('utils/mensaje.html', mensaje='No se pudo guardar el Usuario', submensaje=body)


@Usuario.route('/editar', methods=['POST'])
@only_admin
def post_edit():
    body = dict(request.values)
    usuario = literal_eval(body['usuario'])
    if usuario:
        return render_template('admin/'+endopoint+'editar.html', u=usuario)
    else:
        return render_template('utils/mensaje.html', mensaje='No se pudo cargar el usuario')


@Usuario.route('/actualizar', methods=['POST'])
@only_admin
def update():
    usuario = dict(request.values)
    if 'clave' in usuario.keys():
        if len(usuario['clave']) < 8:
            del usuario['clave']

    correo = usuario.pop('correo')
    status, body = put(endopoint+correo, usuario)
    if status:
        return redirect(url_for('Usuario.listar'))
    else:
        return render_template('utils/mensaje.html', mensaje='No se pudo actualizar el Usuario', submensaje=body)


@Usuario.route('/borrar', methods=['POST'])
@only_admin
def remove():
    body = dict(request.values)
    usuario = literal_eval(body['usuario'])
    if usuario:
        return render_template('admin/'+endopoint+'borrar.html', u=usuario)
    else:
        return render_template('utils/mensaje.html', mensaje='No se pudo actualizar el Usuario')


@Usuario.route('/eliminar', methods=['POST'])
@only_admin
def delete():
    usuario = dict(request.values)
    correo = usuario.pop('correo')
    status, body = delete(endopoint+correo)
    if status:
        return redirect(url_for('Usuario.listar'))
    else:
        return render_template('utils/mensaje.html', mensaje='No se pudo Eliminar el Usuario', submensaje=body)
