import os
import sys 
import logging
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

sys.path.append('./')
load_dotenv()

from utils.utils import *

# Flask app config 
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_KEY")

CORS(app)
jwt = JWTManager(app)

@jwt.expired_token_loader
def my_expired_token_callback(expired_token):
    return jsonify({
        'msg': 'Su sesión ha expirado, vuelva a loguearse'
    }), 401

@app.route('/')
def index():
    return jsonify({'api': 'Pleyades'}), 200

'''LOGGING CONFIGURATION'''
LOG_FORMAT = '%(levelname)s %(asctime)s - %(message)s'

# GENERAL (ALL) LOGS
logging.basicConfig(
    filename=os.getcwd()+'/logs/GENERALS.log',
    level=logging.DEBUG,
    format=LOG_FORMAT
    )

# ERROR LOGS
error_logger = logging.getLogger('error_logger')
error_logger.setLevel(logging.ERROR)
file_handler = logging.FileHandler(os.getcwd()+'/logs/ERRORS.log')
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
error_logger.addHandler(file_handler)
'''END LOGGING CONFIGURATION'''

'''ROUTES'''
#Import Controllers
from controllers.Auth import Auth
from controllers.Facultades import Facultad
from controllers.Programas import Programa
from controllers.Usuarios import Usuario
from controllers.Conjuntos import Conjunto
from controllers.Preparaciones import Preparacion
from controllers.Ejecuciones import Ejecucion
from controllers.desercion.Institucion import IES
from controllers.desercion.Estudiantes import Estudiante
from controllers.desercion.Resultados import Resultado

# Register routes
app.register_blueprint( Auth, url_prefix='/auth')
app.register_blueprint( Facultad, url_prefix='/facultades')
app.register_blueprint( Programa, url_prefix='/programas')
app.register_blueprint( Usuario, url_prefix='/usuarios')
app.register_blueprint( Conjunto, url_prefix='/conjuntos')
app.register_blueprint( Preparacion, url_prefix='/preparaciones')
app.register_blueprint( Ejecucion, url_prefix='/ejecuciones')
app.register_blueprint( IES, url_prefix='/desercion/institucion')
app.register_blueprint( Estudiante, url_prefix='/desercion/estudiantes')
app.register_blueprint( Resultado, url_prefix='/desercion/resultados')
'''END ROUTES'''


'''ERRORS'''
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'error': 'Endpoint No Encontrado'}), 404

@app.errorhandler(405)
def method_not_allow(e):
    return jsonify({'error': 'Metodo No Permitido'}),  405

@app.errorhandler(500)
def handle_500(e):
    error_logger.error(e)
    return jsonify({'error': 'Error en el Servidor del Sistema'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    error_logger.error('EXCEPTION: '+str(e))
    return {'error': 'Ha ocurrido un error en la ejecución del servidor, si es necesario contacte al Admin del Sistema para verificar el error.'}, 500 
'''END ERRORS'''


# Run server
if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
    # app.run(host='0.0.0.0',port=3000,debug=True, threaded=True)
