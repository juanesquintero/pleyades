from flask import Flask
# Import controllers
from views.index import Index
from views.errors import Error
from views.auth import Auth
from views.analist import Analista
from views.datasets import Dataset
from views.results import Result
from views.admin import ResultAdmin, DatasetAdmin, Faculty, Program, Student, User
# from views.dashboards import Tablero
from flask import session
import datetime


def add_route_config(app: Flask):
    excel_enabled = app.config.get('EXCEL_ENABLED')
    ies = app.config.get('IES')

    @app.before_request
    def before_each_request():
        # Excel data loading enabled
        session['excel'] = excel_enabled
        session['ies'] = ies
        # Session permanent
        session.modified = True
        session.permanent = True
        app.permanent_session_lifetime = datetime.timedelta(hours=3)


def add_routes(app: Flask):
    # Add route configuration
    add_route_config(app)

    # Register routes
    app.register_blueprint(Index)
    app.register_blueprint(Error)
    app.register_blueprint(Auth)
    app.register_blueprint(Analista, )
    app.register_blueprint(Faculty, url_prefix='/admin/faculties')
    app.register_blueprint(Program, url_prefix='/admin/programs')
    app.register_blueprint(Student, url_prefix='/admin/students')
    app.register_blueprint(User, url_prefix='/admin/users')
    app.register_blueprint(Dataset, url_prefix='/datasets')
    app.register_blueprint(Result, url_prefix='/results')
    app.register_blueprint(DatasetAdmin, url_prefix='/admin/datasets')
    app.register_blueprint(ResultAdmin, url_prefix='/admin/results')
    # app.register_blueprint(Tablero, url_prefix='#deprecated/#dashboards')
