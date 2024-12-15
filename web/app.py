import datetime
from flask import Flask, session, render_template, request, g
from flask_babel import Babel, _
from views import add_app_routes


app = Flask(__name__, template_folder='templates', static_url_path='/static')

# app_config(app)
app.config.from_object('config')
base_path = app.config['BASE_PATH']
excel_enabled = app.config['EXCEL_ENABLED']
ies = app.config['IES']


@app.route(base_path)
@app.route(base_path+'inicio')
def inicio():
    return render_template('utils/home.html'), 200


@app.route(base_path+'contactanos')
def contactanos():
    return render_template('utils/contactanos.html', ies=ies), 200


# Register routes
add_app_routes(app, base_path)


@app.before_request
def before_each_request():
    # Excel data loading enabled
    session['excel'] = excel_enabled
    # Session permanent
    session.modified = True
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(hours=3)


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
