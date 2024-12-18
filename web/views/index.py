
from flask import render_template, session, Blueprint


index = Blueprint('Index', __name__)


@index.route('')
@index.route('home')
def index():
    return render_template('utils/home.html'), 200


@index.route('contact')
def contact():
    ies = session.get('ies', {})
    return render_template('utils/contact.html', ies=ies), 200
