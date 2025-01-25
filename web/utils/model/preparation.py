import math
import pandas as pd
import warnings
from flask import session
from utils.constants import (
    columns_to_remove_nulls,
    columns_to_remove_1,
    columns_to_remove_1_past,
    columns_to_remove_2,
    columns_to_remove_2_past,
)

################################################################################################################ PREPARACION DE DATOS DE UN CONJUNTO ##############################################################################################################


def prepare_data(data):
    # Condiciones Precisas
    conditions_precisas = [
        ('jornada', 'DIURNA'),
        ('genero', 'MASCULINO'),
        ('estado_civil', 'SOLTERO(A)'),
        ('trabaja', 'SI'),
        ('victima', 'SI'),
        ('pertenece_grupo_vulnerable', 'SI'),
        ('beca', 'SI'),
        ('intersemestral', 'SI'),
        ('desertor', 'SI'),
    ]
    for cond in conditions_precisas:
        column, criteria = cond[0], cond[1]

        def condicion_precisa_fn(
            row): return 1 if row[column] == criteria else 0

        data[column] = data.apply(condicion_precisa_fn, axis=1)

    # Condiciones conjuntas
    conditions_conjuntas = [
        (
            'lugar_residencia_sede',
            ['MEDELLIN', 'BELLO', 'ITAGUI', 'COPACABANA',
                'ENVIGADO', 'SABANETA', 'BARBOSA', 'LA ESTRELLA'],
            1,
            0,
        ),
        (
            'etnia',
            ['NO APLICA', None],
            0,
            1,
        ),
    ]

    for cond in conditions_conjuntas:
        column, criterias = cond[0], cond[1]
        yes_value, no_value = cond[2], cond[3]

        def condicion_conjunta_fn(row):
            value = str(row[column]).lower()
            return yes_value if any(
                c.lower() if isinstance(c, str) else c in value for c in criterias
            ) else no_value

        data[column] = data.apply(condicion_conjunta_fn, axis=1)

    # # Condiciones Especiales
    # def etnia_fn(row):
    #     return 0 if (
    #         row['etnia'] == 'NO APLICA' or
    #         row['etnia'] == None
    #     ) else 1
    # data['etnia'] = data.apply(etnia_fn, axis=1)

    # corregir tipos y name de la base de datos de deserción
    data_preparada = data.rename(columns={'REGISTRO': 'registro'})
    data_preparada['registro'] = data_preparada['registro'].astype(int)

    return data_preparada


############################################################################################################## EJECUCION DE MODELO CON UN CONJUNTO ##############################################################################################################

def elimination(data, no_desertion=False):
    data['registro'] = data['registro'].astype(int)
    warnings.filterwarnings('ignore')

    x = data.groupby('semestre')['edad'].mean()
    for indice_row, row in data.loc[data.edad.isnull()].iterrows():
        data.loc[indice_row, 'edad'] = x[row['semestre']]

    # Elminar desercíon temprana
    data = data.query('semestre != 1')

    if not pd.isna(data['promedio_acumulado']).all():
        data = data.query(
            'promedio_acumulado > 0.3'
        )

    # Obtener ultimo period a predict
    period_a_predict = data['registro'].max()

    if not period_a_predict or math.isnan(period_a_predict):
        raise Exception('Período a predict (REGISTRO maximo) indefinido.')

    # Separar data a predict y a train
    data_a_predict = data.query(f'registro >= {period_a_predict}')
    data = data.query(f'registro < {period_a_predict}')

    # Insertar el N% de la data a predict en entrenamiento
    period_closed = session.get('period_closed')

    # 75% sin cerrar/ 15% cerrado
    if no_desertion:
        umbral = 1
    elif period_closed:
        umbral = 0.10
    else:
        umbral = 0.65

    n_rows = int(data_a_predict.shape[0] * umbral)
    data_proxima = data_a_predict.iloc[:n_rows]

    data = pd.concat([data, data_proxima], ignore_index=True)

    # Eliminar columns inecesarias y nulls
    data = drop_columns(data)
    data_a_predict = drop_nulls(data_a_predict)

    return data, data_a_predict, period_a_predict


def elimination_predict(data):
    warnings.filterwarnings('ignore')

    # Rellenar la edad con promedio por semestre(nivel)
    average = data.groupby('semestre')['edad'].mean()
    for indice_row, row in data.loc[data.edad.isnull()].iterrows():
        data.loc[indice_row, 'edad'] = average[row['semestre']]

    # Elminar desercíon temprana
    data = data.query('semestre != 1 & promedio_acumulado > 0.5')

    return drop_nulls(data)


def drop_columns(data):
    try:
        data = data.drop(columns_to_remove_1, axis=1)
    except Exception as excep:
        data = data.drop(columns_to_remove_1_past, axis=1)

    data = drop_nulls(data)

    try:
        data = data.drop(columns_to_remove_2, axis=1)
    except Exception as excep:
        data = data.drop(columns_to_remove_2_past, axis=1)

    return data


def drop_nulls(data):
    data.dropna(subset=columns_to_remove_nulls, how='any', inplace=True)
    return data
