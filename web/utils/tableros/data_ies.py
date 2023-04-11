import logging
import pandas as pd
from services.API import get

ies_route = 'desercion/institucion/'
estudiantes_route = 'desercion/estudiantes/'
error_logger = logging.getLogger('error_logger')


########################################################## Vista VWDATADESERCIONINSTITUCION de institucion ##########################################################

def get_IES_total_data(periodo: int):
    status, body = get(ies_route+'totales/{}'.format(periodo))
    return validate(status, body, True)


def get_IES_periodo(periodo: int):
    status, body = get(ies_route+'{}'.format(periodo))
    return validate(status, body, True)


def get_IES_programa(programa: int):
    status, body = get(ies_route+'programa/{}'.format(programa))
    return validate(status, body, True)


def get_IES_periodo_programa(periodo: int, programa: int):
    status, body = get(ies_route+'programa/{}/{}'.format(programa, periodo))
    return validate(status, body, True)


def check_IES_periodo_programa(periodo: int, programa: int):
    status, body = get(ies_route+'programa/{}/{}'.format(programa, periodo))
    return status


def get_periodos():
    status, body = get(ies_route+'periodos')
    return validate(status, body)


def get_programas():
    status, body = get(ies_route+'programas')
    return validate(status, body)


def get_programas_by_periodo(periodo: int):
    status, body = get(ies_route+'programas/{}'.format(periodo))
    return validate(status, body)


def get_programa(programa: int):
    status, body = get(ies_route+'programa/{}'.format(programa))
    return validate(status, body, True)

########################################################### Vista VWDATADESERCION de estudiantes ##########################################################


def get_estudiantes_periodo_programa(periodo: int, programa: int):
    status, body = get(estudiantes_route +
                       'programa/{}/{}'.format(programa, periodo))
    return validate(status, body, True)


def get_estudiantes_programa(programa: str):
    status, body = get(estudiantes_route+'programa/{}'.format(programa))
    return validate(status, body, True)


def get_estudiantes_documento(documento: str):
    status, body = get(estudiantes_route+'documento/{}'.format(documento))
    return validate(status, body, True)


def get_periodos_origen():
    status, body = get(estudiantes_route+'periodos')
    return validate(status, body)


def get_programas_origen():
    status, body = get(estudiantes_route+'programas')
    return validate(status, body)


def validate(status, body, df=False):
    if status:
        if df:
            return pd.DataFrame(body)
        return body
    raise Exception('Consulta fallida a la base de datos de Deserción')
