import re
import os
import json
import logging
import pandas as pd
from flask import render_template
from datetime import datetime
from services.API import post, put, get

error_logger = logging.getLogger('error_logger')


def clean_exception(ex):
    ip_port = '[0-9]+(?:\.[0-9]+){3}(:[0-9]+)?'
    error = re.sub(ip_port, '', str(ex))

    words = ['MYSQL', 'SQL', 'MARIADB', 'MICROSOFT', 'SQL SERVER', 'ODBC']
    for word in words:
        error = re.sub(word+'(?i)', '', error)
    symbols = ['[', ']', '"', ')', '(']
    for symbol in symbols:
        error = error.replace(symbol, '')

    return error


def exception(op):
    if isinstance(op, Exception):
        ex = clean_exception(str(op))
        error_logger.error(ex)
        return render_template('utils/mensaje.html', mensaje='Ocurrió un error accesando a los datos'), 500
    else:
        return False

####################################### FUNCIONES logicas repetitivas ###############################################


def get_now_date():
    formato = '%Y-%m-%d %H:%M:%S'
    fecha = datetime.strftime(datetime.now(), formato)
    # Formateo para el api y la bd
    fecha_formateada = fecha.replace(' ', 'T')+'+00:00'
    return fecha_formateada


def set_date_format(resultados):
    for r in resultados:
        r['fechaInicial'] = str_to_date(r['fechaInicial'])
        r['fechaFinal'] = str_to_date(r['fechaFinal'])
    return resultados


def str_to_date(fecha):
    formato_lectura = '%Y-%m-%d %H:%M:%S'
    formato_escritura = '%A %d/%B/%Y - %H:%M %p'
    fecha_lec = datetime.strptime(fecha, formato_lectura)
    fecha_escr = fecha_lec.strftime(formato_escritura)
    return fecha_escr.title()


def guardar_archivo(data, ruta, tipo):
    try:
        if tipo == 'excel':
            data.to_excel(ruta, engine='openpyxl', index=False)
        elif tipo == 'json':
            data.to_json(ruta, orient='records')
        else:
            raise Exception(
                'No se pudo guardar el archivo \n Tipo de archivo incorrecto'
            )
    except Exception as e:
        error_logger.error(e)
        raise Exception('No se pudo guardar el archivo')
    return True, 'ERROR'


def eliminar_archivo(ruta):
    if os.path.exists(ruta):
        try:
            os.remove(ruta)
        except Exception as e:
            error_logger.error(e)
            return False, render_template('utils/mensaje.html', mensaje='No se pudo eliminar el archivo')
    else:
        return False, render_template('utils/mensaje.html', mensaje='No se pudo eliminar el archivo', submensaje='El archivo no existe')
    return True, 'ERROR'


def obtener_archivo_excel(ruta):
    if os.path.exists(ruta+'.xlsx'):
        data = pd.read_excel(ruta+'.xlsx')
    elif os.path.exists(ruta+'.xls'):
        data = pd.read_excel(ruta+'.xls')
    else:
        return False, render_template('utils/mensaje.html', mensaje='No se encontro el archivo')
    return True, data


def obtener_archivo_json(ruta):
    if os.path.exists(ruta+'.json'):
        try:
            with open(ruta+'.json', 'r') as json_file:
                data = json.load(json_file)
        except Exception as e:
            error_logger.error(e)
            return False, render_template('utils/mensaje.html', mensaje='No se pudo abrir el archivo de desertores:')
    else:
        return False, render_template('utils/mensaje.html', mensaje='No se encontro le archivo de desertores')
    return True, data


def actualizar_estado(nombre, estado):
    status, body = put('conjuntos/'+nombre, {'estado': estado})
    if not status:
        return render_template('utils/mensaje.html', mensaje='No fue posible actualizar el estado del conjunto a '+estado, submensaje=body)
    else:
        return None


def guardar_preparacion(preparacion, observaciones, estado):
    # Guardar REGISTRO de preparacion
    preparacion['fechaFinal'] = get_now_date()
    preparacion['observaciones'] = observaciones
    preparacion['estado'] = estado
    post('preparaciones', preparacion)
    return True, 'ERROR'


def guardar_ejecucion(ejecucion, resultados, estado):

    # Guardar REGISTRO de ejecución
    ejecucion['precision_modelo'] = resultados.get('precision', None)
    ejecucion['fechaFinal'] = get_now_date()
    ejecucion['resultados'] = dict(resultados)
    ejecucion['estado'] = estado

    status, body = post('ejecuciones', dict(ejecucion))

    if not status:
        raise Exception(
            f"No se pudo guardar la Ejecucion: {body.get('error')}"
        )

    return True, 'ERROR'


def obtener_nombre_conjunto(conjunto):
    # Obtener nombre del conjunto desde el api
    status_n, body_n = post('conjuntos/nombre', conjunto)
    if status_n:
        return body_n['nombre'], body_n['numero']

    error_logger.error(f'API ERROR: {status_n} {body_n}')
    return False, render_template('utils/mensaje.html', mensaje='No se pudo obtener el nombre del conjunto', submensaje=body_n)


def obtener_nombre_ejecucion(conjunto):
    # Obtener nombre de la ejecucion desde el api
    status_n, body_n = get(f'ejecuciones/nombre/{conjunto}')
    if status_n:
        return body_n['nombre'], body_n['numero']

    error_logger.error(f'API ERROR: {status_n} {body_n}')
    raise Exception('No se pudo obtener el nombre de la ejecución')


def obtener_ies_config():
    # Get IES definition
    ies_name = os.getenv('CLI_IES_NAME')
    base_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f'{base_dir}/../ies.json', 'r') as json_file:
        try:
            IES = json.load(json_file).get(ies_name)
            return IES
        except Exception as e:
            error_logger.error('EXCEPTION: IES Config ERROR: {}'.format(e))
            return {
                'nombre': 'Educatic',
                'url': 'http://educatic.com.co/',
                'logo': 'http://educatic.com.co/assets/images/logo.png',
                'descripcion': 'Oficina: Carrera 42 No 5 SUR 145 Piso 13, oficina 125 WeWork, Medellín, Antioquia Celular: (+57) 311 634 45 26 Email: walter.alvarez@educatic.com.co Servicio y Soporte: soporte@educatic.com.co (+57) 311 634 45 26'
            }
