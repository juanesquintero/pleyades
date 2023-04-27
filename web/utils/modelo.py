import os
import pickle
import logging
import warnings
import pandas as pd
from flask import flash, session
from sklearn import model_selection
from utils.constants import (
    AML,
    col_preparadas,
    columnas_eliminar_nulos,
    columnas_eliminar_1,
    columnas_eliminar_1_anteriores,
    columnas_eliminar_2,
    columnas_eliminar_2_anteriores,
    condiciones
)


modelos_folder = os.getcwd()+'/uploads/modelos'

model_logger = logging.getLogger('model_logger')

############################################################################################################# VERIFICACION DE DATOS CONJUNTO ##############################################################################################################


def verify_data(data, periodoInicial, periodoFinal, programa):
    columnas = list(condiciones.keys())

    # Verificar si conjunto tiene columnas en str y la primera fila
    try:
        data.columns = map(str.lower, data.columns)
    except Exception as e:
        model_logger.error(e)
        return False, 'El conjunto no tiene columnas', None, periodoInicial

    # Verificar si hay registros
    if not(len(data) > 0):
        return False, 'El conjunto no tiene registros (esta vacio)', None, periodoInicial

    # Verificar Si todas las columnas existen
    if not(all(col in data.columns for col in columnas)):
        return False, 'El conjunto ingresado no posee las columnas requeridas', None, periodoInicial
    if not(len(data.columns) == len(columnas)):
        return False, 'El conjunto ingresado tiene mas columnas de las requeridas', None, periodoInicial
    # Verificar si los tipos de datos de colunma son correctos
    try:
        data_verificada = assign_types(data)
    except Exception as e:
        model_logger.error(e)
        return False, 'El conjunto ingresado no tiene los tipos de dato por columna requeridos', None, periodoInicial
    # Verificar si en conjunto posee mas de un  valor en la columna programa
    if not(len(set(data_verificada['programa'].tolist())) == 1):
        return False, 'El conjunto tiene resgistros de mas de un programa, los modelos se ejecutan por programa', None, periodoInicial
    # Verificar si en conjunto posee los valores de periodo Inicial y Final Correctamente
    if not(data_verificada['registro'].max() == periodoFinal):
        return False, 'El conjunto no tiene como periodo final {}, verifique los registros'.format(str(periodoFinal)), None, periodoInicial
    if not(data_verificada['registro'].min() == periodoInicial):
        _periodoInicial = periodoInicial
        periodoInicial = data_verificada['registro'].min()
        flash('El conjunto no tiene como periodo inicial {}, se reasignó a <b>{}</b>'.format(
            str(_periodoInicial), str(periodoInicial)), 'warning')
    if not(data_verificada['idprograma'] == programa).all():
        return False, 'El conjunto no pertenece al programa indicado, verifique los registros', None, periodoInicial

    # Verificacion correcta
    return True, None, data_verificada, periodoInicial


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

def elimination(data):
    data['registro'] = data['registro'].astype(int)
    warnings.filterwarnings('ignore')

    x = data.groupby('semestre')['edad'].mean()
    for indice_fila, fila in data.loc[data.edad.isnull()].iterrows():
        data.loc[indice_fila, 'edad'] = x[fila['semestre']]

    # Elminar desercíon temprana
    data = data.query('semestre != 1 & promedio_acumulado > 0.5')

    periodo_a_predecir = data['registro'].max()

    # Separar data a predecir y a entrenar
    data_a_predecir = data.query(f"registro >= {periodo_a_predecir}")
    data = data.query(f'registro < {periodo_a_predecir}')

    # Insertar el N% de la data a predecir en entrenamiento
    periodo_cerrado = session.get('periodo_cerrado')
    # 85% sin cerrar/ 15% cerrado
    umbral = 0.85
    if periodo_cerrado:
        umbral = 0.15

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


def execute_model(data, conjunto=''):
    data['registro'] = data['registro'].astype(int)

    basic_info = {
        'idprograma': int(data['idprograma'][0]),
        'programa': str(data['programa'][0]),
        'idfacultad': int(data['idfacultad'][0]),
        'facultad': str(data['facultad'][0]),
        'tipo': 'Entrenamiento',
    }

    # Eliminacion depuracion de columnas
    data, data_a_predecir, periodo_a_predecir = elimination(data)

    basic_info['periodo_a_predecir_mas_1'] = f'{periodo_a_predecir} + 1'

    if len(data_a_predecir) <= 0:
        return False, 'No hay suficientes datos en el periodo final, revisa el conjunto.'

    ''' FASE 1 '''

    cv_split = model_selection.ShuffleSplit(
        n_splits=10, test_size=.3, train_size=.7, random_state=42
    )
    AML_columns = ['Nombre',
                   'objeto',
                   'Parametros',
                   'Precision Media de Prueba',
                   'STD de la Precision * 3',
                   'Tiempo'
                   ]
    AML_compare = pd.DataFrame(columns=AML_columns)
    Target = ['desertor']
    AML_predict = data[Target]
    row_index = 0

    for alg in AML:
        AML_nombre = alg.__class__.__name__
        AML_compare.loc[row_index, 'Nombre'] = AML_nombre
        AML_compare.loc[row_index, 'Parametros'] = str(alg.get_params())
        cv_results = model_selection.cross_validate(
            alg,
            data[col_preparadas],
            data[Target],
            cv=cv_split
        )

        AML_compare.loc[
            row_index,
            'Precision Media de Prueba'
        ] = cv_results['test_score'].mean()
        # Si es una muestra aleatoria sin sesgo, entonces la media +/- 3*(desviación estándar), deberían capturar el 99.7% de los subconjuntos
        AML_compare.loc[
            row_index,
            'STD de la Precision * 3'
        ] = cv_results['test_score'].std()*3
        AML_compare.loc[row_index, 'Tiempo'] = cv_results['fit_time'].mean()

        alg.fit(data[col_preparadas], data[Target])
        AML_predict[AML_nombre] = alg.predict(data[col_preparadas])
        AML_compare.loc[row_index, 'objeto'] = alg
        row_index += 1

    AML_compare.sort_values(
        by=['Precision Media de Prueba'],
        ascending=False,
        inplace=True
    )

    AML_best = AML_compare.head(1)
    mejor_clasificador = AML_best['objeto'].tolist()[0]

    # Guardar clasificador
    save_classifire(mejor_clasificador, conjunto)

    # Usar mejor clasificador para prediction
    result = predict_classifier(
        data_a_predecir, periodo_a_predecir, mejor_clasificador
    )

    precision_modelo = AML_best['Precision Media de Prueba'].tolist()[0] * 100

    resultados = {
        **basic_info,
        'clasificador': str(AML_best['Nombre'].tolist()[0]),
        'precision': float(round(precision_modelo, 2)),
        'periodo_anterior': int(periodo_a_predecir),
        'desertores': result.get('desertores'),
        'periodo_a_predecir': int(periodo_a_predecir),
        'estudiantes_analizados': result.get('total_analizados'),
        'desercion_prevista': result.get('desercion'),
        'desertores_reportados':  int(len(data_a_predecir[data_a_predecir['desertor'] == 1])),
        'potenciales_desertores': result.get('total'),
    }

    return resultados, result.get('resultado')


# TODO NEW! version 2 v2.0.0
def predict(data_a_predecir, periodo_a_predecir, basic_info):

    data_a_predecir['registro'] = data_a_predecir['registro'].astype(int)

    if len(data_a_predecir) < 3:
        raise Exception(
            f'Hay muy pocos registros para el periodo {periodo_a_predecir} (menos de 3)', True
        )

    # Eliminacion depuracion de columnas
    data_a_predecir = elimination_predict(data_a_predecir)

    # Obtener el clasificador como archivo local
    nombre_modelo = basic_info.get('modelo')
    mejor_clasificador = load_classifer(nombre_modelo)

    # Predecir
    result = predict_classifier(
        data_a_predecir, periodo_a_predecir, mejor_clasificador
    )

    resultados = {
        **basic_info,
        'tipo': 'Prediccion',
        'desertores': result.get('desertores'),
        'periodo_a_predecir': int(periodo_a_predecir),
        'estudiantes_analizados': result.get('total_analizados'),
        'desercion_prevista': result.get('desercion'),
        'potenciales_desertores': result.get('total'),
        'clasificador': str(mejor_clasificador.__class__.__name__),
    }

    return resultados, result.get('resultado')


def predict_classifier(data_a_predecir, periodo_a_predecir, mejor_clasificador):
    predc_sem_act = data_a_predecir[
        [
            'registro', 'semestre', 'documento', 'nombre_completo',
            'desertor', 'idprograma', 'idestado', 'promedio_acumulado'
        ]
    ]

    if data_a_predecir.empty:
        raise Exception(
            'No se detectaron potenciales desertores! en esta predicción', True)

    try:
        predc_sem_act['prediccion'] = mejor_clasificador.predict(
            data_a_predecir[col_preparadas]
        )
    except Exception as e:
        model_logger.error(e)
        raise Exception(
            f'Ocurrió un error al ejecutar la predicción! por favor intente con otro periodo o modelo', True
        )
    total_estudiantes_analizados = len(predc_sem_act['documento'].unique())
    potenciales_desertores = predc_sem_act.query('prediccion == 1 & desertor == 0').drop_duplicates(
        subset=['documento'],
        keep='first'
    ).reset_index()

    # TODO filtro de idestado
    # Elminar no matriculados
    potenciales_desertores = potenciales_desertores.query(
        f"idestado == 6 & registro == {periodo_a_predecir}"
    )

    potenciales_desertores = potenciales_desertores.drop('registro', axis=1)

    # Re asignar tipos
    potenciales_desertores['semestre'] = potenciales_desertores['semestre'].astype(
        int, copy=False
    )
    potenciales_desertores['documento'] = potenciales_desertores['documento'].astype(
        str, copy=False
    )

    # Setear resultados para insertar en la BD
    potenciales_desertores['semestre_prediccion'] = periodo_a_predecir

    # Elminar desercíon temprana
    no_desercion_temprana = potenciales_desertores.query(
        'semestre != 1 & promedio_acumulado > 0.5'
    )

    if not no_desercion_temprana.empty:
        potenciales_desertores = no_desercion_temprana

    total_desertores, desercion_prevista = calculate_desercion(total_estudiantes_analizados, potenciales_desertores)

    # Filtrar bajo promedio por alta deserción
    if desercion_prevista > 0.20:
        potenciales_desertores = potenciales_desertores.query('promedio_acumulado < 3.7')
        total_desertores, desercion_prevista = calculate_desercion(total_estudiantes_analizados, potenciales_desertores)

    resultados_desertores = potenciales_desertores

    ''' FASE 3 '''
    pd.crosstab(predc_sem_act.prediccion, predc_sem_act.desertor, margins=True)

    matriz_confusion = pd.crosstab(
        predc_sem_act.prediccion, predc_sem_act.desertor, margins=True
    )

    potenciales_desertores.drop(['index'], axis=1, inplace=True)

    # Reasignar el tipo de la columna documento
    resultados_desertores['documento'] = resultados_desertores['documento'].astype(
        str, copy=False)
    resultados_desertores = resultados_desertores[[
        'documento', 'nombre_completo', 'desertor', 'prediccion', 'semestre_prediccion', 'idprograma'
    ]]

    return {
        'resultado': resultados_desertores,
        'desertores': potenciales_desertores,
        'total': int(total_desertores),
        'total_analizados': int(total_estudiantes_analizados),
        'desercion': float(round(desercion_prevista, 3))
    }

def calculate_desercion(total_estudiantes, potenciales_desertores):
    total_desertores = len(potenciales_desertores.index)
    desercion_prevista = int(total_desertores) / \
        int(total_estudiantes)
        
    return total_desertores,desercion_prevista


def save_classifire(mejor_clasificador, conjunto=''):
    clf_file = f'{modelos_folder}/{conjunto}.pkl'
    with open(clf_file, 'wb') as f:
        pickle.dump(mejor_clasificador, f)
    pickle.dump(mejor_clasificador, open(
        f'{modelos_folder}/{conjunto}.sav', 'wb'))


def load_classifer(conjunto):
    clf_file = f'{modelos_folder}/{conjunto}.pkl'
    with open(clf_file, 'rb') as f:
        clf = pickle.load(f)
    clf = pickle.load(open(clf_file, 'rb'))
    return clf


############################################################################################################### FUNCION DE ASIGNACION DE TIPOS DE DATOS CORRECTOS ###########################################################################################################################################

def assign_types(data):
    # Asignar tipos de datos en cada columna
    for key, value in condiciones.items():
        # Obtener los valores de cada columna que no sean nulos
        # y asignarle el tipo requerido para la columna
        data[key][data[key].notna()] = data[key][data[key].notna()].astype(value)
    return data
