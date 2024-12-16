# Import controllers
from views.analist import Analista
from views.errors import Error
from views.auth import Auth
from views.admin import ResultAdmin, DatasetAdmin, Faculty, Program, Student, User
from views.datasets import Dataset
from views.results import Result
# from views.dashboards import Tablero
from flask import render_template, session
import datetime


def add_route_config(app, base_path):

    excel_enabled = app.config.get('EXCEL_ENABLED')
    ies = app.config.get('IES')

    @app.before_request
    def before_each_request():
        # Excel data loading enabled
        session['excel'] = excel_enabled
        # Session permanent
        session.modified = True
        session.permanent = True
        app.permanent_session_lifetime = datetime.timedelta(hours=3)

    @app.route(base_path)
    @app.route(base_path+'home')
    def index():
        return render_template('utils/home.html'), 200

    @app.route(base_path+'contact')
    def contact():
        return render_template('utils/contact.html', ies=ies), 200


def add_routes(app):
    base_path = app.config.get('BASE_PATH')

    # Add route configuration
    add_route_config(app, base_path)

    # Register routes
    app.register_blueprint(Error, url_prefix=base_path)
    app.register_blueprint(Auth, url_prefix=base_path)
    app.register_blueprint(Analista, url_prefix=base_path)
    app.register_blueprint(Faculty, url_prefix=base_path+'admin/faculties')
    app.register_blueprint(Program, url_prefix=base_path+'admin/programs')
    app.register_blueprint(Student, url_prefix=base_path+'admin/students')
    app.register_blueprint(User, url_prefix=base_path+'admin/users')
    app.register_blueprint(Dataset, url_prefix=base_path+'datasets')
    app.register_blueprint(Result, url_prefix=base_path+'results')
    app.register_blueprint(DatasetAdmin, url_prefix=base_path+'admin/datasets')
    app.register_blueprint(ResultAdmin, url_prefix=base_path+'admin/results')
    # app.register_blueprint(Tablero, url_prefix=base_path+'_deprecado/#TABLEROS')
