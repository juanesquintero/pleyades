import re
import logging
import traceback
from decimal import Decimal

error_logger = logging.getLogger('error_logger')


def exception(op):
    if isinstance(op, Exception) or op is None:
        message, exception_info = 'EXCEPTION: {}'.format(
            op), traceback.format_exc()
        if exception_info:
            message += '   ---->   {}'.format(exception_info)
        error_logger.error(message, exc_info=True)
        return {'error': 'Ha ocurrido un error en la ejecución del servidor, si es necesario contacte al Admin del sistema para verificar el error.'}, 500
    
    return False


def clean_exception(excep):
    ip_port = '[0-9]+(?:\.[0-9]+){3}(:[0-9]+)?'
    error = re.sub(ip_port, '', str(excep))

    words = ['MYSQL', 'SQL', 'MARIADB', 'MICROSOFT', 'SQL SERVER', 'ODBC']
    for word in words:
        error = re.sub(word+'(?i)', '', error)

    symbols = ['[', ']', '"']
    for symbol in symbols:
        error = error.replace(symbol, '')

    return error


def decimal_format(obj: dict):
    for k, v in obj.items():
        if isinstance(v, Decimal) and not isinstance(v, float):
            obj[k] = int(v)
    return obj


def _format(query):
    if isinstance(query, list):
        for obj in query:
            if isinstance(obj, dict):
                obj = decimal_format(obj)
            else:
                break
    if query is dict:
        query = decimal_format(query)

    return query
