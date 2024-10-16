
import os
import sys
import locale
import logging
import datetime
from flask import Flask, session, render_template
from dotenv import load_dotenv

from views.analista import Analista
from views.errors import Error
from views.auth import Auth
from views.admin import ResultadoAdmin, ConjuntoAdmin, Facultad, Programa, Estudiante, Usuario
from views.conjuntos import StudentSet
from views.resultados import Resultado
from utils.mixins import obtener_ies_config


# Config root path and language
locale.setlocale(locale.LC_ALL, 'es_MX.UTF-8')
sys.path.append('./')
load_dotenv()

# Import controllers


app = Flask(__name__, template_folder='templates', static_url_path='/static')

# IES config
IES = obtener_ies_config()
ies_name = os.getenv('CLI_IES_NAME')
base_path = '/'  # base_path = ('/' + ies_name) if ies_name else '/'
excel_enabled = os.getenv('EXCEL', 'false').lower() in ('true', '1', 't')

# Variables de sesion
app.config['SECRET_KEY'] = os.getenv('SESSION_KEY')


@app.route(base_path)
@app.route(base_path+'inicio')
def inicio():
    return render_template('utils/inicio.html'), 200


@app.route(base_path+'contactanos')
def contactanos():
    return render_template('utils/contactanos.html', ies=IES), 200


'''ROUTES'''
# from views.tableros import Tablero

app.register_blueprint(Error, url_prefix=base_path)
app.register_blueprint(Auth, url_prefix=base_path)
app.register_blueprint(Analista, url_prefix=base_path)
app.register_blueprint(Facultad, url_prefix=base_path+'admin/facultades')
app.register_blueprint(Programa, url_prefix=base_path+'admin/programas')
app.register_blueprint(Estudiante, url_prefix=base_path+'admin/estudiantes')
app.register_blueprint(Usuario, url_prefix=base_path+'admin/usuarios')
app.register_blueprint(StudentSet, url_prefix=base_path+'conjuntos')
app.register_blueprint(Resultado, url_prefix=base_path+'resultados')
# app.register_blueprint(Tablero, url_prefix=base_path+'_deprecado/#TABLEROS')
app.register_blueprint(ConjuntoAdmin, url_prefix=base_path+'admin/conjuntos')
app.register_blueprint(ResultadoAdmin, url_prefix=base_path+'admin/resultados')

'''END ROUTES'''

'''LOGGING CONFIGURATION'''
LOG_FORMAT = '%(levelname)s %(asctime)s - %(message)s'

# GENERAL (ALL) LOGS
logging.basicConfig(
    filename=os.getcwd()+'/logs/GENERALS.log',
    level=logging.DEBUG,
    format=LOG_FORMAT
)

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
def before_each_request():
    # Excel data loading enabled
    session['excel'] = excel_enabled
    # Session permanent
    session.modified = True
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(hours=3)
