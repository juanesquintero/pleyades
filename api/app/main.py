import sys
import logging
import traceback
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask import Flask, jsonify

sys.path.append('.')
sys.path.append('..')


db = SQLAlchemy()


def create_app(config_object: str = 'api.config') -> Flask:
    # Flask app config
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config_object)

    with app.app_context():

        # DB config
        app_db(app)

        # Other config
        CORS(app)

        jwt = JWTManager(app)

        @jwt.expired_token_loader
        def expired_token_callback(jwt_header=None, jwt_data=None):
            return jsonify({
                'msg': 'Su session ha expired, vuelva a loguearse'
            }), 401

        # ROUTES
        app_routes(app)

        # ERRORS
        app_errors(app)

        return app


def app_db(app):
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


def app_routes(app):
    base_path = app.config.get('BASE_PATH', '/')

    @app.route(base_path)
    def index():
        return jsonify({'api': 'Pleyades'}), 200

    # Import Controllers
    from app.controllers import (
        Auth,
        Faculty,
        Program,
        User,
        Dataset,
        Preparation,
        Execution,
        IES,
        Student,
        Result,
    )

    # Register routes
    app.register_blueprint(Auth, url_prefix=base_path+'auth')
    app.register_blueprint(Faculty, url_prefix=base_path+'faculties')
    app.register_blueprint(Program, url_prefix=base_path+'programs')
    app.register_blueprint(User, url_prefix=base_path+'users')
    app.register_blueprint(Dataset, url_prefix=base_path+'datasets')
    app.register_blueprint(Preparation, url_prefix=base_path+'preparations')
    app.register_blueprint(Execution, url_prefix=base_path+'executions')
    app.register_blueprint(IES, url_prefix=base_path+'desertion/institute')
    app.register_blueprint(
        Student, url_prefix=base_path+'desertion/students'
    )
    app.register_blueprint(
        Result, url_prefix=base_path+'desertion/results'
    )


def app_errors(app):
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
        return {'error': 'Excepción, Ha ocurrido un error en the ejecución del servidor.'}, 500
