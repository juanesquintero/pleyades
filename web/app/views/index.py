from flask import render_template, session, Blueprint

Index = Blueprint('Index', __name__)


@Index.route('/')
@Index.route('/home')
def home():
    return render_template('utils/home.html'), 200


@Index.route('/contact')
def contact():
    ies = session.get('ies', {})
    return render_template('utils/contact.html', ies=ies), 200
