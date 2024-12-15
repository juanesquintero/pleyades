# Import controllers
from views.analist import Analista
from views.errors import Error
from views.auth import Auth
from views.admin import ResultAdmin, DatasetAdmin, Faculty, Program, Student, User
from views.datasets import Dataset
from views.results import Result
# from views.dashboards import Tablero


def add_app_routes(app, base_path):
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
