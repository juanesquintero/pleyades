from flask import Flask, request, g
from flask_babel import Babel, _
from flask_session import Session

from celery import Celery, Task

from views import add_routes


def create_app(config_object='config') -> Flask:
    """Application Factory Function."""
    app = Flask(__name__, template_folder='templates',
                static_url_path='/static')

    # Load configuration
    app.config.from_object(config_object)

    # Register routes
    add_routes(app)

    # Set up Babel for localization
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

    babel = Babel(
        app,
        locale_selector=get_locale,
        timezone_selector=get_timezone
    )

    # Init user session
    sess = Session()
    sess.init_app(app)

    return app


# Entry point for Celery initialization
def create_celery_app(flask_app: Flask) -> Celery:
    class FlaskTask(Task):
        """Initialize Celery with Flask App Context."""

        def __call__(self, *args: object, **kwargs: object) -> object:
            with flask_app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(flask_app.name, task_cls=FlaskTask)
    celery_app.config_from_object(flask_app.config["CELERY"])
    celery_app.set_default()
    flask_app.extensions["celery"] = celery_app

    return celery_app
