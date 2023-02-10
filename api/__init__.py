import os
import sys 
import logging
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy

sys.path.append('./')
load_dotenv()

# ies_name = os.getenv('CLI_IES_NAME')
# base_path = ('/' + ies_name) if ies_name else '/'
base_path = '/'

db = SQLAlchemy()

def create_app():
    # Flask app config 
    app = Flask(__name__)
    
    with app.app_context():
        app.config['JSON_SORT_KEYS'] = False
        app.config['JWT_SECRET_KEY'] = os.getenv('JWT_KEY')

        # DB config
        app_db(app)

        # Other config 
        CORS(app)
        jwt = JWTManager(app)
        @jwt.expired_token_loader
        def my_expired_token_callback(jwt_header=None, jwt_data=None):
            return jsonify({
                'msg': 'Su sesión ha expirado, vuelva a loguearse'
            }), 401
     
        # ROUTES
        app_routes(app)

        # ERRORS
        app_errors(app, app_logging())

        return app

def app_db(app):
    _user = os.getenv('MYSQL_USER')
    _password = os.getenv('MYSQL_PASSWORD')
    _database = os.getenv('MYSQL_DATABASE')
    _host = os.getenv('MYSQL_SERVER')
    _port = os.getenv('MYSQL_SERVER_PORT')

    str_conn = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(_user, _password, _host, _port, _database)

    app.config['SQLALCHEMY_DATABASE_URI'] = str_conn
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
    
    db.app = app
    db.init_app(app)
    
    def execute(sql):
        return db.session.execute(text(sql))
    def query(sql):
        cur = db.session.execute(text(sql))
        rows = cur.fetchall()
        print(rows.__str__())
        columns = [i[0] for i in cur.description]
        return  [dict(zip(columns, row)) for row in rows]
    
    app.config['DB'] = {'execute': execute, 'query': query}


def app_logging():
    LOG_FORMAT = '%(levelname)s %(asctime)s - %(message)s'

    # GENERAL (ALL) LOGS
    logging.basicConfig(filename=os.getcwd()+'/logs/GENERALS.log', level=logging.DEBUG, format=LOG_FORMAT)

    # ERROR LOGS
    error_logger = logging.getLogger('error_logger')
    error_logger.setLevel(logging.ERROR)
    file_handler = logging.FileHandler(os.getcwd()+'/logs/ERRORS.log')
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    error_logger.addHandler(file_handler)

    return error_logger


def app_routes(app):

    @app.route(base_path)
    def index():
        return jsonify({'api': 'Pleyades'}), 200

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
    app.register_blueprint( Auth, url_prefix=base_path+'auth')
    app.register_blueprint( Facultad, url_prefix=base_path+'facultades')
    app.register_blueprint( Programa, url_prefix=base_path+'programas')
    app.register_blueprint( Usuario, url_prefix=base_path+'usuarios')
    app.register_blueprint( Conjunto, url_prefix=base_path+'conjuntos')
    app.register_blueprint( Preparacion, url_prefix=base_path+'preparaciones')
    app.register_blueprint( Ejecucion, url_prefix=base_path+'ejecuciones')
    app.register_blueprint( IES, url_prefix=base_path+'desercion/institucion')
    app.register_blueprint( Estudiante, url_prefix=base_path+'desercion/estudiantes')
    app.register_blueprint( Resultado, url_prefix=base_path+'desercion/resultados')


def app_errors(app, error_logger):
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
