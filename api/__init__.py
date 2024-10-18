import traceback
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask import Flask, jsonify
from dotenv import load_dotenv
import logging
import os
import sys
sys.path.append('.')
sys.path.append('..')


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
        def expired_token_callback(jwt_header=None, jwt_data=None):
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

    str_conn = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(
        _user, _password, _host, _port, _database)

    app.config['SQLALCHEMY_DATABASE_URI'] = str_conn
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.app = app
    db.init_app(app)

    def execute(sql):
        return db.session.execute(text(sql))

    def query(sql):
        cur = db.session.execute(text(sql))
        rows = cur.fetchall()
        columns = [i[0] for i in cur.description]
        return [dict(zip(columns, row)) for row in rows]

    app.config['DB'] = {'execute': execute, 'query': query}


def app_logging():
    LOG_FORMAT = '%(levelname)s %(asctime)s - %(message)s'

    # GENERAL (ALL) LOGS
    logging.basicConfig(filename=os.getcwd()+'/logs/GENERALS.log',
                        level=logging.DEBUG, format=LOG_FORMAT)

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

    # Import Controllers
    from controllers.Auth import Auth
    from controllers.Facultades import Faculty
    from controllers.Programas import Program
    from controllers.users import User
    from controllers.Conjuntos import Set
    from controllers.Preparaciones import Preparacion
    from controllers.Ejecuciones import Ejecucion
    from controllers.desertion.Institucion import IES
    from controllers.desertion.Estudiantes import Student
    from controllers.desertion.Resultados import Result

    # Register routes
    app.register_blueprint(Auth, url_prefix=base_path+'auth')
    app.register_blueprint(Faculty, url_prefix=base_path+'faculties')
    app.register_blueprint(Program, url_prefix=base_path+'programs')
    app.register_blueprint(User, url_prefix=base_path+'users')
    app.register_blueprint(Set, url_prefix=base_path+'sets')
    app.register_blueprint(Preparacion, url_prefix=base_path+'preparations')
    app.register_blueprint(Ejecucion, url_prefix=base_path+'executions')
    app.register_blueprint(IES, url_prefix=base_path+'desertion/institute')
    app.register_blueprint(
        Student, url_prefix=base_path+'desertion/estudiantes')
    app.register_blueprint(
        Result, url_prefix=base_path+'desertion/resultados')


def app_errors(app, error_logger):
    def exception(e):
        message, exception_info = f'EXCEPTION: {e}', traceback.format_exc()
        if exception_info:
            message += f'   ---->   {exception_info}'
            logging.getLogger('error_logger').error(message, exc_info=True)

    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify({'error': 'Endpoint No Encontrado'}), 404

    @app.errorhandler(405)
    def method_not_allow(e):
        return jsonify({'error': 'Metodo No Permitido'}),  405

    @app.errorhandler(500)
    def handle_500(e):
        exception(e)
        return jsonify({'error': 'Error en el Servidor del Sistema'}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        exception(e)
        return {'error': 'Excepción, Ha ocurrido un error en la ejecución del servidor.'}, 500
