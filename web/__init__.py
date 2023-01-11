import os
import sys 
import locale
import logging
import datetime
from flask import Flask, session, render_template
from flask_session import Session
from dotenv import load_dotenv


# Config root path and language
locale.setlocale(locale.LC_ALL, 'es_MX.UTF-8') 
sys.path.append('./')
load_dotenv()

# Import controllers
from views.errors import Error
from views.auth import Auth

from views.admin.usuarios import Usuario
from views.admin.programas import Programa
from views.admin.facultades import Facultad
from views.admin.conjuntos import ConjuntoAdmin
from views.admin.resultados import ResultadoAdmin

from views.conjuntos import Conjunto
from views.resultados import Resultado
from views.tableros import Tablero

app = Flask(__name__, template_folder='templates', static_url_path='/static')

# IES config
from utils.mixins import obtener_ies_config
IES = obtener_ies_config()

# Variables de sesion
app.config['SECRET_KEY'] = os.getenv("SESSION_KEY")

@app.route('/')
@app.route('/inicio')
def inicio():
    return render_template('utils/inicio.html'), 200

@app.route('/contactanos')
def contactanos():
    return render_template('utils/contactanos.html', ies=IES), 200


'''ROUTES'''
app.register_blueprint(Error)
app.register_blueprint(Auth)
app.register_blueprint(Facultad, url_prefix='/admin/facultades')
app.register_blueprint(Programa, url_prefix='/admin/programas')
app.register_blueprint(Usuario, url_prefix='/admin/usuarios')
app.register_blueprint(Conjunto, url_prefix='/conjuntos')
app.register_blueprint(Resultado, url_prefix='/resultados')
app.register_blueprint(Tablero, url_prefix='/_deprecado/#TABLEROS')
app.register_blueprint(ConjuntoAdmin, url_prefix='/admin/conjuntos')
app.register_blueprint(ResultadoAdmin, url_prefix='/admin/resultados')

'''END ROUTES'''

'''LOGGING CONFIGURATION'''
LOG_FORMAT = '%(levelname)s %(asctime)s - %(message)s'

# GENERAL (ALL) LOGS
logging.basicConfig(filename=os.getcwd()+'/logs/GENERALS.log',level=logging.DEBUG,format=LOG_FORMAT)

# APP ERROR LOGS
error_logger = logging.getLogger('error_logger')
error_logger.setLevel(logging.ERROR)
file_handler = logging.FileHandler(os.getcwd()+'/logs/ERRORS.log')
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
error_logger.addHandler(file_handler)

# MODEL ERROR LOGS
model_logger = logging.getLogger('model_logger')
model_logger.setLevel(logging.ERROR)
file_handler = logging.FileHandler(os.getcwd()+'/logs/MODEL.log')
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
model_logger.addHandler(file_handler)

'''END LOGGING CONFIGURATION'''

@app.before_request
def make_session_permanent():
    session.modified = True
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(hours=2)

if __name__ == '__main__':
    # Sesion login usuario config   
    app.config['SESSION_PERMANENT'] = True
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(hours=2)
    app.config['SESSION_FILE_THRESHOLD'] = 100 
    #Iniciar sesion de login usuario
    sess = Session() 
    sess.init_app(app)
    
    # Run server
    app.run(host='0.0.0.0')
    # app.run(host='0.0.0.0',port=5000, debug=True, threaded=True)
