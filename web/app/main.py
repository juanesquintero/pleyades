from flask import Flask, request, g
from flask_babel import Babel, _
from flask_session import Session
from celery import Celery, Task


def create_app(config_object: str = 'web.config') -> Flask:
    """Application Factory Function."""
    app = Flask(
        __name__,
        template_folder='templates',
        static_url_path='/static'
    )

    # Load configuration
    app.config.from_object(config_object)

    create_celery_app(app)

    # Register routes
    from web.app.views import add_routes
    add_routes(app)

    # Set up Babel for localization
    def get_locale() -> str | None:
        """Determine the user's preferred locale."""
        user = getattr(g, 'user', None)
        if user is not None:
            return user.locale
        return request.accept_languages.best_match(['de', 'fr', 'en'])

    def get_timezone() -> str | None:
        """Determine the user's preferred timezone."""
        user = getattr(g, 'user', None)
        if user is not None:
            return user.timezone
        return None

    babel = Babel(
        app,
        locale_selector=get_locale,
        timezone_selector=get_timezone
    )

    # Initialize user session
    Session(app)

    return app


# Entry point for Celery initialization
def create_celery_app(flask_app: Flask) -> Celery:
    """Initialize and configure Celery with Flask app context support."""
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with flask_app.app_context():
                return self.run(*args, **kwargs)

    # Initialize Celery with the Flask app name and custom task class
    celery_app = Celery(flask_app.name, task_cls=FlaskTask)
    celery_app.config_from_object(flask_app.config.get("CELERY"))
    # Set the Celery app as the default
    celery_app.set_default()
    # Store the Celery app in Flask's extensions for easy access
    flask_app.extensions["celery"] = celery_app
    # Autodiscover tasks
    celery_app.autodiscover_tasks(packages=["web.app.utils.tasks"], force=True)

    return celery_app
