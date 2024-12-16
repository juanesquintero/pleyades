from flask import Flask, request, g
from flask_babel import Babel, _
from views import add_app_routes


app = Flask(__name__, template_folder='templates', static_url_path='/static')

# app_config(app)
app.config.from_object('config')

# Register routes
add_app_routes(app)


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
