import datetime
from app import app
from flask_session import Session


if __name__ == '__main__':
    # Sesion login usuario config
    app.config['SESSION_PERMANENT'] = True
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(hours=3)
    app.config['SESSION_FILE_THRESHOLD'] = 100
    # Iniciar sesion de login usuario
    sess = Session()
    sess.init_app(app)

    # Run server
    app.run(host='0.0.0.0')
