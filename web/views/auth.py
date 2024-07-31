import os
import dotenv
import jwt
from functools import wraps
from flask import session, request, Blueprint, render_template
from services.API import post

dotenv.load_dotenv()


Auth = Blueprint('auth', __name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not 'user' in session.keys():
            return render_template('utils/login.html'), 200
        if session['user'] is None:
            return render_template('utils/login.html'), 200
        return f(*args, **kwargs)
    return decorated_function


def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not 'user' in session.keys():
            return f(*args, **kwargs)
        if session['user'] is None:
            return f(*args, **kwargs)
        return render_template('utils/inicio.html'), 200
    return decorated_function


def only_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not 'user' in session.keys():
            return render_template('utils/login.html'), 200
        if session['user'] is None:
            return render_template('utils/login.html'), 200
        if session['user']['rol'] == 'Admin':
            return f(*args, **kwargs)
        return render_template('utils/mensaje.html', mensaje='Usted no tiene autorizacion para realizar esta accion'), 401
    return decorated_function


@Auth.route('/login', methods=['GET', 'POST'])
@logout_required
def login():
    if request.method == 'GET':
        return render_template('utils/login.html'), 200
    # Loguear
    raw_usuario = dict(request.values)
    usuario = {'correo': raw_usuario['InputEmailLogin'],
               'clave': raw_usuario['InputPasswordLogin']}

    status, body = post('auth/login', usuario)
    if status:
        session['user'] = None
        session['headers'] = None
        # Obtener token
        token = body.get('access_token')
        # Setear usuario de la session
        user = jwt.decode(
            token,
            os.getenv('JWT_KEY'),
            algorithms=["HS256"],
        ).get('sub')
        session['user'] = user
        # Definir objeto request para realizar peticiones  al API
        session['headers'] = {'Authorization': 'Bearer ' + token}
        session.permanent = True

        return render_template('utils/inicio.html'), 200
    if 'msg' in body.keys():
        return render_template('utils/login.html', mensaje=body.get('msg')), 401
    return render_template('utils/error.html', mensaje='Ocurrió un error loguandose', submensaje=body.get('error')), 400


@Auth.route('/logout')
@login_required
def logout():
    session['user'] = None
    session['headers'] = None
    session.clear()
    return render_template('utils/login.html'), 200
