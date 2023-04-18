import os
import pickle
import logging
import warnings
import pandas as pd
from flask import flash
import utils.constants as CONSTANTS
# Algoritmos comunes para clasificación
# Apoyo para la validación cruzada
from sklearn import (
    svm,
    tree,
    linear_model,
    neighbors,
    naive_bayes,
    ensemble,
    discriminant_analysis,
    model_selection
)


# TODO NEW! version 2 v2.0.0
modelos_folder = os.getcwd()+'/uploads/modelos'

error_logger = logging.getLogger('error_logger')

############################################################################################################# VERIFICACION DE DATOS CONJUNTO ##############################################################################################################


def verificar_data(data, periodoInicial, periodoFinal, programa):
    columnas = list(condiciones.keys())

    # Verificar si conjunto tiene columnas en str y la primera fila
    try:
        data.columns = map(str.lower, data.columns)
    except Exception as e:
        error_logger.error(e)
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
        data_verificada = asignar_tipos(data)
    except Exception as e:
        error_logger.error(e)
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
def preparar_data(data):
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

        def func(row):
            return yes_value if any(
                c.lower() in row[columna].lower() for c in criterios
            ) else no_value
        data[columna] = data.apply(func, axis=1)

    # Condiciones Especiales
    def func(row):
        return 0 if (
            row['etnia'] == 'NO APLICA' or
            row['etnia'] == None
        ) else 1
    data['etnia'] = data.apply(func, axis=1)

    return data


############################################################################################################## EJECUCION DE MODELO CON UN CONJUNTO ##############################################################################################################


def eliminacion(data, periodo_a_predecir=None, predicir=False,):

    warnings.filterwarnings('ignore')

    ''' FASE 1 '''
    if predicir:
        data_a_predecir = data
    else:
        periodo_a_predecir = data['registro'].max()

        data_a_predecir = data[data['registro'] >= periodo_a_predecir]
        # data = data[data['semestre']>1]
        data = data[data['registro'] < periodo_a_predecir]

    try:
        data = data.drop(CONSTANTS.columnas_eliminar_1, axis=1)
    except Exception as e:
        data = data.drop(CONSTANTS.columnas_eliminar_1_anteriores, axis=1)

    columnas_eliminar_nulos = CONSTANTS.columnas_eliminar_nulos

    data.dropna(subset=columnas_eliminar_nulos, how='any', inplace=True)
    data_a_predecir.dropna(
        subset=columnas_eliminar_nulos,
        how='any',
        inplace=True
    )

    ''' FASE 2 '''
    x = data.groupby('semestre')['edad'].mean()

    for indice_fila, fila in data.loc[data.edad.isnull()].iterrows():
        data.loc[indice_fila, 'edad'] = x[fila['semestre']]

    ''' FASE 3 '''
    try:
        data = data.drop(CONSTANTS.columnas_eliminar_2, axis=1)
    except Exception as e:
        data = data.drop(CONSTANTS.columnas_eliminar_2_anteriores, axis=1)

    if predicir:
        return data_a_predecir

    return data, data_a_predecir, periodo_a_predecir


def ejecutar_modelo(data, conjunto=''):

    idprograma = int(data['idprograma'][0])
    nombre_programa = str(data['programa'][0])

    idfacultad = int(data['idfacultad'][0])
    nombre_facultad = str(data['facultad'][0])

    data, data_a_predecir, periodo_a_predecir = eliminacion(data)

    if len(data_a_predecir) <= 0:
        return False, 'No hay suficientes datos en el periodo final, revisa el conjunto.'

    ''' FASE 1 '''
    # Algoritmos de Machine Learning (AML)
    AML = [
        # Métodos Combinados
        ensemble.AdaBoostClassifier(),
        ensemble.BaggingClassifier(),
        ensemble.ExtraTreesClassifier(),
        ensemble.GradientBoostingClassifier(),
        ensemble.RandomForestClassifier(),

        # Modelo Lineal Generalizado (GLM)
        linear_model.LogisticRegressionCV(),
        linear_model.PassiveAggressiveClassifier(),
        linear_model.RidgeClassifierCV(),
        linear_model.SGDClassifier(),
        linear_model.Perceptron(),

        # Navies Bayes
        naive_bayes.BernoulliNB(),
        naive_bayes.GaussianNB(),

        # K-Nearest Neighbor
        neighbors.KNeighborsClassifier(),

        # Máquina de Vectores de Soporte (SVM)
        svm.SVC(probability=True),
        svm.LinearSVC(),

        # Árboles de Decisión
        tree.DecisionTreeClassifier(),
        tree.ExtraTreeClassifier(),

        # Análisis Discriminante (Discriminant Analysis)
        discriminant_analysis.LinearDiscriminantAnalysis(),
        discriminant_analysis.QuadraticDiscriminantAnalysis(),
    ]

    cv_split = model_selection.ShuffleSplit(
        n_splits=10, test_size=.3, train_size=.6, random_state=0
    )
    AML_columns = ['Nombre',
                   'objeto',
                   'Parametros',
                   'Precision Media de Prueba',
                   'STD de la Precision * 3',
                   'Tiempo'
                   ]
    AML_compare = pd.DataFrame(columns=AML_columns)

    col_preparadas = CONSTANTS.col_preparadas

    Target = ['desertor']
    AML_predict = data[Target]

    row_index = 0
    for alg in AML:

        AML_nombre = alg.__class__.__name__
        AML_compare.loc[row_index, 'Nombre'] = AML_nombre
        AML_compare.loc[row_index, 'Parametros'] = str(alg.get_params())
        cv_results = model_selection.cross_validate(
            alg, data[col_preparadas], data[Target], cv=cv_split)

        AML_compare.loc[row_index,
                        'Precision Media de Prueba'] = cv_results['test_score'].mean()
        # Si es una muestra aleatoria sin sesgo, entonces la media +/- 3*(desviación estándar), deberían capturar el 99.7% de los subconjuntos
        AML_compare.loc[row_index,
                        'STD de la Precision * 3'] = cv_results['test_score'].std()*3
        AML_compare.loc[row_index, 'Tiempo'] = cv_results['fit_time'].mean()

        alg.fit(data[col_preparadas], data[Target])
        AML_predict[AML_nombre] = alg.predict(data[col_preparadas])
        AML_compare.loc[row_index, 'objeto'] = alg
        row_index += 1

    AML_compare.sort_values(
        by=['Precision Media de Prueba'], ascending=False, inplace=True)

    ''' FASE 2 '''
    x = data_a_predecir.groupby('semestre')['edad'].mean()
    for indice_fila, fila in data_a_predecir.loc[data_a_predecir.edad.isnull()].iterrows():
        data_a_predecir.loc[indice_fila, 'edad'] = x[fila['semestre']]

    ''' FASE 2 '''
    AML_best = AML_compare.head(1)
    mejor_clasificador = AML_best['objeto'].tolist()[0]

    # TODO NEW! version 2 v2.0.0
    guardar_clasificador(mejor_clasificador, conjunto)

    predc_sem_act = data_a_predecir[[
        'documento', 'nombre_completo', 'desertor', 'idprograma', 'idestado']]

    predc_sem_act['prediccion'] = mejor_clasificador.predict(
        data_a_predecir[col_preparadas])

    potenciales_desertores = predc_sem_act.query('prediccion==1 & desertor!=1')
    # TODO filtro de idestado
    potenciales_desertores_matriculados = potenciales_desertores.query('idestado==6')

    # Eliminar valores repetidos
    potenciales_desertores = potenciales_desertores.drop_duplicates(
        subset=['documento'],
        keep='first'
    ).reset_index()

    # Setear resultados para insertar en la BD
    potenciales_desertores['semestre_prediccion'] = periodo_a_predecir

    resultados_desertores = potenciales_desertores
    potenciales_desertores = potenciales_desertores.drop(
        ['idprograma', 'semestre_prediccion'],
        axis=1
    )

    ''' FASE 3 '''
    pd.crosstab(predc_sem_act.prediccion, predc_sem_act.desertor, margins=True)
    matriz_confusion = pd.crosstab(
        predc_sem_act.prediccion,
        predc_sem_act.desertor,
        margins=True
    )

    total_desertores = len(potenciales_desertores.index)
    total_estudiantes_analizados = len(predc_sem_act['documento'].unique())
    potenciales_desertores.drop(['index'], axis=1, inplace=True)

    periodo_a_predecir_mas_1 = f'{periodo_a_predecir} + 1'
    precision_modelo = AML_best['Precision Media de Prueba'].tolist()[0] * 100
    desercion_prevista = int(total_desertores) / \
        int(total_estudiantes_analizados)

    resultados = {
        'idprograma': idprograma,
        'programa': nombre_programa,
        'idfacultad': idfacultad,
        'tipo': 'Entrenamiento',
        'facultad': nombre_facultad,
        'periodo_a_predecir': periodo_a_predecir_mas_1,
        'desertores': potenciales_desertores,
        'estudiantes_analizados': int(total_estudiantes_analizados),
        'desercion_prevista': float(round(desercion_prevista, 2)),
        'clasificador': str(AML_best['Nombre'].tolist()[0]),
        'precision': float(round(precision_modelo, 2)),
        'periodo_anterior': str(periodo_a_predecir),
        'total_potenciales_desertores': int(total_desertores),
        'total_desertores':  str(len(data_a_predecir[data_a_predecir['desertor'] == 1])),
        'total_desertores_matriculados'.format(periodo_a_predecir):  str(len(data_a_predecir.query('idestado==6'))),
    }

    # Reasignar el tipo de la columna documento
    resultados_desertores['documento'] = resultados_desertores['documento'].astype(
        str, copy=False)
    resultados_desertores = resultados_desertores[[
        'documento', 'nombre_completo', 'desertor', 'prediccion', 'semestre_prediccion', 'idprograma'
    ]]

    return resultados, resultados_desertores


# TODO NEW! version 2 v2.0.0
def predecir(data_a_predecir, periodo_a_predecir, basic_info):
    if len(data_a_predecir) < 5:
        raise Exception(
            f'Hay muy pocos registros para el periodo {periodo_a_predecir} (menos de 5)'
        )

    # Eliminacion y Relleno
    data_a_predecir = eliminacion(data_a_predecir, periodo_a_predecir, True)
    x = data_a_predecir.groupby('semestre')['edad'].mean()
    for indice_fila, fila in data_a_predecir.loc[data_a_predecir.edad.isnull()].iterrows():
        data_a_predecir.loc[indice_fila, 'edad'] = x[fila['semestre']]

    nombre_modelo = basic_info.get('modelo')
    mejor_clasificador = cargar_clasificador(nombre_modelo)
    col_preparadas = CONSTANTS.col_preparadas

    # data_a_predecir.to_excel('data.xlsx')

    predc_sem_act = data_a_predecir[
        ['documento', 'nombre_completo', 'desertor', 'idprograma', 'idestado']
    ]

    predc_sem_act['prediccion'] = mejor_clasificador.predict(
        data_a_predecir[col_preparadas]
    )

    potenciales_desertores = predc_sem_act.query('prediccion==1 & desertor!=1')
    # TODO filtro de idestado
    potenciales_desertores_matriculados = potenciales_desertores.query('idestado==6')

    # Eliminar valores repetidos
    potenciales_desertores = potenciales_desertores.drop_duplicates(
        subset=['documento'],
        keep='first'
    ).reset_index()

    # Setear resultados para insertar en la BD
    potenciales_desertores['semestre_prediccion'] = periodo_a_predecir

    resultados_desertores = potenciales_desertores
    potenciales_desertores = potenciales_desertores.drop(
        ['idprograma', 'semestre_prediccion'],
        axis=1
    )

    ''' FASE 3 '''
    pd.crosstab(predc_sem_act.prediccion, predc_sem_act.desertor, margins=True)
    matriz_confusion = pd.crosstab(
        predc_sem_act.prediccion, predc_sem_act.desertor, margins=True
    )

    total_desertores = len(potenciales_desertores.index)
    total_estudiantes_analizados = len(predc_sem_act['documento'].unique())
    potenciales_desertores.drop(['index'], axis=1, inplace=True)
    desercion_prevista = int(total_desertores) / \
        int(total_estudiantes_analizados)

    resultados = {
        **basic_info,
        'tipo': 'Prediccion',
        'desertores': potenciales_desertores,
        'periodo_a_predecir': periodo_a_predecir,
        'estudiantes_analizados': int(total_estudiantes_analizados),
        'desercion_prevista': float(round(desercion_prevista, 2)),
        'clasificador': str(mejor_clasificador.__class__.__name__),
        'total_desertores': int(total_desertores),
        'total_desertores_matriculados':  str(len()),
    }

    # Reasignar el tipo de la columna documento
    resultados_desertores['documento'] = resultados_desertores['documento'].astype(
        str, copy=False)
    resultados_desertores = resultados_desertores[[
        'documento', 'nombre_completo', 'desertor', 'prediccion', 'semestre_prediccion', 'idprograma'
    ]]

    return resultados, resultados_desertores


# TODO NEW! version 2 v2.0.0
def guardar_clasificador(mejor_clasificador, conjunto=''):
    clf_file = f'{modelos_folder}/{conjunto}.pkl'
    with open(clf_file, 'wb') as f:
        pickle.dump(mejor_clasificador, f)
    pickle.dump(mejor_clasificador, open(
        f'{modelos_folder}/{conjunto}.sav', 'wb'))


# TODO NEW! version 2 v2.0.0
def cargar_clasificador(conjunto):
    clf_file = f'{modelos_folder}/{conjunto}.pkl'
    with open(clf_file, 'rb') as f:
        clf = pickle.load(f)
    clf = pickle.load(open(clf_file, 'rb'))
    return clf


############################################################################################################### FUNCION DE ASIGNACION DE TIPOS DE DATOS CORRECTOS ###########################################################################################################################################


condiciones = CONSTANTS.condiciones


def asignar_tipos(data):
    # # Cambiar valores NaN por None
    # data.replace([np.inf, -np.inf], None, inplace=True)
    # data.replace({np.nan: None}, inplace=True)

    # Asignar tipos de datos en cada columna
    for key, value in condiciones.items():
        # Obtener los valores de cada columna que no sean nulos
        # y asignarle el tipo requerido para la columna
        data[key][data[key].notna()] = data[key][data[key].notna()].astype(value)

    return data
