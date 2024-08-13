import logging
from flask import Blueprint, render_template, app, url_for, flash, redirect

error_logger = logging.getLogger('error_logger')

Error = Blueprint('Error', __name__)


@Error.app_errorhandler(404)
def page_not_found(e):
    return render_template('utils/error.html', error=str(e)), 404


@Error.app_errorhandler(405)
def method_not_allow(e):
    return render_template('utils/error.html', error=str(e)), 405


@Error.app_errorhandler(500)
@Error.route('/error')
def handle_500(e):
    error_logger.error(e)
    return render_template('utils/error.html', error=str(e)), 500


@Error.app_errorhandler(Exception)
def handle_exception(e):
    if len(e.args) > 1 and e.args[1]:
        flash(f'<b>{e.args[0]}</b>', 'warning')
        return redirect(url_for('Analista.modelos'))

    error_logger.error(f'EXCEPTION: {e}', exc_info=True)
    return render_template('utils/error.html', exception=True, mensaje=str(e), status=404), 500
