from flask import request, session, Blueprint, render_template, redirect, send_file
from datetime import datetime
from services.API import get, post, put, delete
import re, os, sys, json, pandas as pd
import logging

error_logger = logging.getLogger('error_logger')

def clean_exception(ex):
    ip_port = '[0-9]+(?:\.[0-9]+){3}(:[0-9]+)?'
    error = re.sub(ip_port,'',str(ex))
    
    words = ['MYSQL', 'SQL', 'MARIADB', 'MICROSOFT','SQL SERVER','ODBC']
    for word in words:
        error = re.sub(word+'(?i)','',error)
    symbols = ['[',']','"',')','(']    
    for symbol in symbols:
        error = error.replace(symbol,'')

    return error

def exception(op):
    if isinstance(op, Exception):
        error_logger.error(op)
        return render_template('utils/mensaje.html', mensaje='Ocurrio un error accesando a los datos'), 500 
    else:
        return False

####################################### FUNCIONES logicas repetitivas ###############################################
def getNowDate():
    formato = '%Y-%m-%d %H:%M:%S'
    fecha = datetime.strftime(datetime.now(), formato)
    # Formateo para el api y la bd
    fecha_formateada = fecha.replace(' ','T')+'+00:00'
    return fecha_formateada

def set_date_format(resultados):
    for r in resultados: 
        r['fechaInicial']=str_to_date(r['fechaInicial'])
        r['fechaFinal']=str_to_date(r['fechaFinal'])
    return resultados

def str_to_date(fecha):
    formato_lectura = '%Y-%m-%d %H:%M:%S'
    formato_escritura = '%A %d, %B/%Y - %H:%M:%S %p'
    fecha_lec = datetime.strptime(fecha, formato_lectura)
    fecha_escr = fecha_lec.strftime(formato_escritura)
    return fecha_escr.title() 

def guardar_archivo(data,ruta,tipo):
    try:
        if tipo=='excel':
            data.to_excel(ruta, index=False)
        elif tipo=='json':
            data.to_json(ruta, orient='records')
        else:
            return False, render_template('utils/mensaje.html', mensaje='No se pudo guardar el archivo', submensaje='Tipo de archivo incorrecto')
    except Exception as e:
        error_logger.error(e)
        return False, render_template('utils/mensaje.html', mensaje='No se pudo guardar el archivo')
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
            with open(ruta+'.json','r') as json_file:
                data = json.load(json_file)
        except Exception as e:
            error_logger.error(e)
            return False, render_template('utils/mensaje.html', mensaje='No se pudo abrir el archivo de desertores:')
    else:
        return False, render_template('utils/mensaje.html', mensaje='No se encontro le archivo de desertores')
    return True, data

def actualizar_estado(nombre,estado):
    status, body = put('conjuntos/'+nombre,{'estado': estado})
    if not status:
        return render_template('utils/mensaje.html', mensaje='No fue posible actualizar el estado del conjunto a '+estado, submensaje=body)
    else:
        return None

def guardar_preparacion(preparacion,observaciones,estado):
    # Guardar registro de preparacion
    preparacion['fechaFinal'] = getNowDate()
    preparacion['observaciones'] = observaciones
    preparacion['estado'] = estado
    status, body = post('preparaciones', preparacion)
    if not status:
        return False, render_template('utils/mensaje.html', mensaje='No se pudo guardar el registro de preparacion', submensaje=body)
    else:
        return True, 'ERROR'

def guardar_ejecucion(ejecucion,resultados,estado):
    # Guardar registro de ejecucion
    ejecucion['precision_modelo'] = resultados['precision'] if 'precision' in resultados.keys() else None
    ejecucion['fechaFinal'] = getNowDate()
    ejecucion['resultados'] = resultados
    ejecucion['estado'] = estado
    status, body = post('ejecuciones',ejecucion)
    if not(status):
        return False, render_template('utils/mensaje.html', mensaje='No se pudo guardar el registro de la ejecucion', submensaje=body)
    else:
        return True, 'ERROR'