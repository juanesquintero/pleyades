import warnings
from flask import session
from utils.constants import (
    columnas_eliminar_nulos,
    columnas_eliminar_1,
    columnas_eliminar_1_anteriores,
    columnas_eliminar_2,
    columnas_eliminar_2_anteriores,
)

################################################################################################################ PREPARACION DE DATOS DE UN CONJUNTO ##############################################################################################################


def prepare_data(data):
    # Condiciones Precisas
    condiciones = [
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
    for cond in condiciones:
        columna, criterio = cond[0], cond[1]
        def func(row): return 1 if row[columna] == criterio else 0
        data[columna] = data.apply(func, axis=1)

    # Condiciones conjuntas
    condiciones = [
        ('lugar_residencia_sede',  ['MEDELLIN', 'BELLO', 'ITAGUI',
         'COPACABANA', 'ENVIGADO', 'SABANETA', 'BARBOSA', 'LA ESTRELLA'], 1, 0),
    ]
    for cond in condiciones:
        yes_value, no_value = cond[2], cond[3]
        columna, criterios = cond[0], cond[1]

        def func1(row):
            return yes_value if any(
                c.lower() in row[columna].lower() for c in criterios
            ) else no_value
        data[columna] = data.apply(func1, axis=1)

    # Condiciones Especiales
    def func2(row):
        return 0 if (
            row['etnia'] == 'NO APLICA' or
            row['etnia'] == None
        ) else 1
    data['etnia'] = data.apply(func2, axis=1)

    # corregir tipos y nombre de la base de datos de deserción
    data_preparada = data.rename(columns={'REGISTRO': 'registro'})
    data_preparada['registro'] = data_preparada['registro'].astype(int)

    return data_preparada


############################################################################################################## EJECUCION DE MODELO CON UN CONJUNTO ##############################################################################################################

def elimination(data, no_desertion=False):
    data['registro'] = data['registro'].astype(int)
    warnings.filterwarnings('ignore')

    x = data.groupby('semestre')['edad'].mean()
    for indice_fila, fila in data.loc[data.edad.isnull()].iterrows():
        data.loc[indice_fila, 'edad'] = x[fila['semestre']]

    # Elminar desercíon temprana
    data = data.query('semestre != 1 & promedio_acumulado > 0.5')

    periodo_a_predecir = data['registro'].max()


    # Separar data a predecir y a entrenar
    data_a_predecir = data.query(f'registro >= {periodo_a_predecir}')
    data = data.query(f'registro < {periodo_a_predecir}')

    # Insertar el N% de la data a predecir en entrenamiento
    periodo_cerrado = session.get('periodo_cerrado')
    
    # 75% sin cerrar/ 15% cerrado
    if no_desertion:
        umbral = 1
    elif periodo_cerrado:
        umbral = 0.05
    else:
        umbral = 0.75

    n_rows = int(data_a_predecir.shape[0] * umbral)
    data_proxima = data_a_predecir.iloc[:n_rows]

    data = data.append(data_proxima)

    # Eliminar columnas inecesarias y nulos
    data = drop_columns(data)
    data_a_predecir = drop_nulls(data_a_predecir)

    return data, data_a_predecir, periodo_a_predecir


def elimination_predict(data):
    warnings.filterwarnings('ignore')

    # Rellenar la edad con promedio por semestre(nivel)
    x = data.groupby('semestre')['edad'].mean()
    for indice_fila, fila in data.loc[data.edad.isnull()].iterrows():
        data.loc[indice_fila, 'edad'] = x[fila['semestre']]

    # Elminar desercíon temprana
    data = data.query('semestre != 1 & promedio_acumulado > 0.5')

    return drop_nulls(data)


def drop_columns(data):
    try:
        data = data.drop(columnas_eliminar_1, axis=1)
    except Exception as e:
        data = data.drop(columnas_eliminar_1_anteriores, axis=1)

    data = drop_nulls(data)

    try:
        data = data.drop(columnas_eliminar_2, axis=1)
    except Exception as e:
        data = data.drop(columnas_eliminar_2_anteriores, axis=1)

    return data


def drop_nulls(data):
    data.dropna(subset=columnas_eliminar_nulos, how='any', inplace=True)
    return data
