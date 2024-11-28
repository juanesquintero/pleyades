
import os
import sys
import locale
import logging
import datetime
from flask import Flask, session, render_template, request, g
from flask_babel import Babel, _
from dotenv import load_dotenv

from views.analist import Analista
from views.errors import Error
from views.auth import Auth
from views.admin import ResultAdmin, DatasetAdmin, Faculty, Program, Student, User
from views.datasets import Dataset
from views.results import Result
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
    return render_template('utils/home.html'), 200


@app.route(base_path+'contactanos')
def contactanos():
    return render_template('utils/contactanos.html', ies=IES), 200


'''ROUTES'''
# from views.dashboards import Tablero

app.register_blueprint(Error, url_prefix=base_path)
app.register_blueprint(Auth, url_prefix=base_path)
app.register_blueprint(Analista, url_prefix=base_path)
app.register_blueprint(Faculty, url_prefix=base_path+'admin/faculties')
app.register_blueprint(Program, url_prefix=base_path+'admin/programs')
app.register_blueprint(Student, url_prefix=base_path+'admin/students')
app.register_blueprint(User, url_prefix=base_path+'admin/users')
app.register_blueprint(Dataset, url_prefix=base_path+'datasets')
app.register_blueprint(Result, url_prefix=base_path+'results')
# app.register_blueprint(Tablero, url_prefix=base_path+'_deprecado/#TABLEROS')
app.register_blueprint(DatasetAdmin, url_prefix=base_path+'admin/datasets')
app.register_blueprint(ResultAdmin, url_prefix=base_path+'admin/results')

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


# Configure available languages and default settings
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'
app.config['LANGUAGES'] = ['en', 'es']  # Example languages


def get_locale():
    # if a user is logged in, use the locale from the user settings
    user = getattr(g, 'user', None)
    if user is not None:
        return user.locale
    # otherwise try to guess the language from the user accept
    # header the browser transmits.  We support de/fr/en in this
    # example.  The best match wins.
    return request.accept_languages.best_match(['de', 'fr', 'en'])


def get_timezone():
    user = getattr(g, 'user', None)
    if user is not None:
        return user.timezone


babel = Babel(app, locale_selector=get_locale, timezone_selector=get_timezone)
