import traceback
import pandas as pd
import os, json, logging
import utils.tableros.data_ies as DataIES

from flask import request, session, Blueprint, render_template, redirect, send_file, url_for, jsonify
from dotenv import load_dotenv
from ast import literal_eval
from googletrans import Translator

from utils.modelo import preparar_data, verificar_data, ejecutar_modelo
from views.auth import login_required
from services.API import get, post, put

from utils.mixins import actualizar_estado, guardar_archivo, guardar_ejecucion, guardar_preparacion, getNowDate, obtener_archivo_excel, obtener_nombre_conjunto

model_logger = logging.getLogger('model_logger')
error_logger = logging.getLogger('error_logger')

load_dotenv()

Conjunto = Blueprint('Conjunto', __name__)

endopoint = 'conjuntos/'

upload_folder = os.getcwd()+'/uploads'

translator = Translator()

@Conjunto.route('/crudos')
@Conjunto.route('/crudos/')
@login_required
def crudos():
    return listar('crudos')

@Conjunto.route('/procesados')
@Conjunto.route('/procesados/')
@Conjunto.route('/procesados/<conjunto>')
@login_required
def procesados(conjunto=None):
    if conjunto: return listar('procesados',str(conjunto))
    return listar('procesados')

def listar(estado, conjunto=None):
    status_p,body_p = get('programas')
    status_c,body_c = get('conjuntos/encargado/'+session['user']['correo']+'?estado='+estado)
    
    if status_c and status_p:
        if conjunto: 
            body_c = [d for d in body_c if conjunto in d['nombre']]
        return render_template(endopoint+estado+'.html', conjuntos=body_c, programas=body_p)        
    elif not(status_c) and not(status_p):
        error = {**body_c,**body_p}
    elif not(status_c):
        error = body_c
    else:
        error = body_p
    return render_template(endopoint+estado+'.html', conjuntos=[],error=error)

@Conjunto.route('/descargar/<estado>/<nombre>')
def descargar (estado, nombre):

    status_c,body_c = get('conjuntos/'+nombre)
    if not status_c:
        return render_template('utils/mensaje.html', mensaje='No existe ese conjunto')
    
    if estado.lower() == 'crudos':
        nombre = 'C '+nombre
    elif estado.lower() == 'procesados':
        nombre = 'P '+nombre
    else:
        return render_template('utils/mensaje.html', mensaje='Estado del conjunto incorrecto')

    ruta = upload_folder+'/'+estado.lower()+'/'+nombre
    
    if os.path.exists(ruta+'.xlsx'):
        return send_file(ruta+'.xlsx', as_attachment=True)
    elif os.path.exists(ruta+'.xls'):
        return send_file(ruta+'.xls', as_attachment=True)
    else:
        return render_template('utils/mensaje.html', mensaje='No se encontro el archivo a descargar')    
    

@Conjunto.route('/crear')
@Conjunto.route('/crear/')
@login_required
def crear():
    periodos =  DataIES.get_periodos_origen();
    status_f,body_f = get('facultades')
    status_p,body_p = get('programas')

    if status_f and status_p and periodos:
        return render_template(endopoint+'crear.html', facultades=body_f, programas=body_p)
    elif not(status_f) and not(status_p):
        error = {**body_f,**body_p}
    elif not(status_f):
        error = body_f
    else:
        error = body_p
    return render_template('utils/mensaje.html', mensaje='No se pudieron cargar las programas y las facultades', submensaje=error)

@Conjunto.route('crear/periodos/programa/<int:programa>')
@login_required
def get_periodos_programa(programa):
    status,body = get('desercion/estudiantes/periodos/programa/{}'.format(programa))
    if status:
        return jsonify(body)
    return jsonify([])

@Conjunto.route('/detalle',methods=['POST'])
@login_required
def detalle():
    # Obtener Lo valores del formulario
    body = dict(request.values)
    conjunto = literal_eval(body['conjunto'])
    # Consultas para mostrar info
    status_f,body_f = get('facultades')
    status_p,body_p = get('programas')
    status_u, body_u = get('usuarios')
    
    if status_p and status_f and status_u and conjunto:
        return render_template(endopoint+'detalle.html', facultades=body_f, programas=body_p, usuarios=body_u, c=conjunto)
    elif not(status_f) and not(status_p) and not(status_u):
        error = {**body_f,**body_p,**body_u}
    elif not(status_f):
        error = body_f
    elif not(status_p):
        error = body_p
    elif not(conjunto):
        return render_template('utils/mensaje.html', mensaje='No se encontro un conjunto para detallar')
    else:
        error = body_u
    return render_template('utils/mensaje.html', mensaje='No se pudieron cargar los datos para detallar el conjunto', submensaje=error)

@Conjunto.route('/crear', methods=['POST'])
@Conjunto.route('/crear/', methods=['POST'])
@login_required
def guardar():
    # Obtener Lo valores del formulario
    conjunto = dict(request.values)
    # Preparar conjunto para la insercion
    del conjunto['facultad']
    conjunto['estado'] = 'Crudos'
    conjunto['periodoInicial'] = int(conjunto['periodoInicial'])
    conjunto['periodoFinal'] = int(conjunto['periodoFinal'])
    conjunto['programa'] = int(conjunto['programa'])
    conjunto['encargado'] = session['user']['correo']

    tipo = conjunto['tipo']
    archivo = request.files['archivo']
    ruta = upload_folder+'/crudos'

    # Guardar archivo en Upload folder

    ############# ARCHIVO ##############
    if (archivo.filename and tipo=='excel'):
        extension = '.'+archivo.filename.split('.')[1]
        # Guardar archivo de excel
        
        if not (extension in ['.xls', '.xlsx']):
            return render_template('utils/mensaje.html', mensaje='Extension de archivo incorrecta: '+str(extension), submensaje='Solo se permiten archivos excel .xls & xlsx')
    
        # VERIFICACION de formato
        data = pd.read_excel(archivo)

        error_logger.error('\n\n\n\n\nPeriodoInicial:  {} '.format(conjunto.get('periodoInicial')))

        validacion, mensaje_error, data_verificada, periodoInicial = verificar_data(data, conjunto.get('periodoInicial'), conjunto.get('periodoFinal'), conjunto.get('programa'))
        conjunto['periodoInicial'] =  periodoInicial

        error_logger.error('\n\n\n\n\n\n\n\n\n Conjunto: '+ conjunto.__str__()) 

        # Obtener nombre del conjunto desde el api
        nombre, numero = obtener_nombre_conjunto(conjunto)
        if not nombre: return numero
        archivo_guardar = 'C '+ nombre + '.xls'

        if validacion:
            try:
                data_verificada.to_excel(ruta+'/'+archivo_guardar, index=False)
                # archivo.save(os.path.join(ruta, nombre + extension))
            except Exception as e:
                error_logger.error(e)
                return render_template('utils/mensaje.html', mensaje='Ocurrió un error guardando el conjunto de datos')
        else:
            return render_template('utils/mensaje.html', mensaje='Incorrecto el formato de la fuente de datos', submensaje=mensaje_error)
    
    ############# CONSULTA ##############
    elif tipo=='consulta':
        # Obtener datos de los estudiantes en ese programas y periodos
        endpoint_conjunto = 'desercion/estudiantes/conjunto/{}/{}/{}'
        endpoint_conjunto_values = endpoint_conjunto.format(conjunto['programa'], conjunto['periodoInicial'], conjunto['periodoFinal'])
        status,body = get(endpoint_conjunto_values)
        if status:
            data = pd.DataFrame(body)
        else:
            return render_template('utils/mensaje.html', mensaje='Consulta fallida a la base de datos')
        
        error_logger.error('\n\n\n\n\nPeriodoInicial:  {} '.format(conjunto.get('periodoInicial')))
        
        # VERIFICACION de formato
        validacion, mensaje_error, data_verificada, periodoInicial = verificar_data(data, conjunto.get('periodoInicial'), conjunto.get('periodoFinal'), conjunto.get('programa'))
        conjunto['periodoInicial'] =  periodoInicial
        
        error_logger.error('\n\n\n\n\n\n\n\n\n Conjunto: '+ conjunto.__str__()) 

        # Obtener nombre del conjunto desde el api
        nombre, numero = obtener_nombre_conjunto(conjunto)
        if not nombre: return numero
        archivo_guardar = 'C '+ nombre + '.xls'

        if validacion:
            # Guardar tabla sql como excel
            try:
                data_verificada.to_excel(ruta+'/'+archivo_guardar, index=False)
            except Exception as e:
                error_logger.error(e)
                return render_template('utils/mensaje.html', mensaje='Ocurrió un error guardando el conjunto de datos')
        else:
            return render_template('utils/mensaje.html', mensaje='Incorrecto el formato de la fuente de datos', submensaje=mensaje_error)
    else:
        return render_template('utils/mensaje.html', mensaje='Formulario incorrecto', submensaje='Verifica el formulario de creacion o notifica al Administrador del sistema')
           
    # Guardar registro de conjunto en la BD
    conjunto['nombre'] =  nombre
    conjunto['numero'] =  numero

    status, body = post('conjuntos',conjunto)
    if status:
        return redirect(url_for('Conjunto.crudos'))
    else:
        return render_template('utils/mensaje.html', mensaje='No se pudo guardar el conjunto', submensaje=body)


@Conjunto.route('/preparar', methods=['POST'])
@login_required
def preparar():
    # Obtener Lo valores del formulario
    body = dict(request.values)
    conjunto = literal_eval(body['conjunto'])
    
    nombre = conjunto['nombre']

    # Actualizar conjunto de datos de crudo a en proceso 
    act_estado =  actualizar_estado(nombre,'En Proceso')
    if act_estado: return act_estado

    # Crear prepraracion
    preparacion = {}
    preparacion['conjunto'] = conjunto['nombre']
    preparacion['preparador'] = session['user']['correo']
    preparacion['fechaInicial'] = getNowDate()
    # Obtener numero de preparacion para el conjunto
    status_p, body_p = get('preparaciones/nombre/'+nombre)
    if status_p:
        preparacion['numero'] = body_p['numero']
        preparacion['nombre'] = body_p['nombre']
    else:
        return render_template('utils/mensaje.html', mensaje='No se pudo obtener el consecutivo de la preparación para este conjunto', submensaje=body_p)

    ########### PREPARAR ############

    # Obtener archivo crudo
    archivo_crudo = 'C '+nombre 
    ruta = upload_folder+'/crudos/'+archivo_crudo
    exito,data_cruda = obtener_archivo_excel(ruta) 
    if not(exito): return data_cruda 

    # Algoritmo de preparacion
    try:
        data_preparada = preparar_data(data_cruda)
    except Exception as e:
        model_logger.error(e)
        model_logger.error(traceback.format_exc())
        observaciones = {'error': str(e)}
        exito,pagina_error = guardar_preparacion(preparacion, observaciones,'Fallida')
        if not(exito): return pagina_error 
        return render_template('utils/mensaje.html', mensaje='la preparación falló')

    # Guardar archivo en Upload folder procesados
    archivo_procesado = 'P '+nombre+'.xls'
    ruta = upload_folder+'/procesados/'+archivo_procesado
    exito,pagina_error = guardar_archivo(data_preparada, ruta, 'excel')
    if not(exito): return pagina_error 

    # Guardar registro de preparacion en la BD 
    exito, pagina_error = guardar_preparacion(preparacion,None,'Exitosa')
    if not(exito): return pagina_error 

    ########### FIN PREPARAR ############    

    # Actualizar conjunto de datos de crudo a procesado
    act_estado =  actualizar_estado(nombre,'Procesados')
    if act_estado: return act_estado

    return redirect(url_for('Conjunto.procesados', conjunto=conjunto['nombre']))


@Conjunto.route('/ejecutar', methods=['POST'])
@login_required
def ejecutar():
    ejecucion_guardada = False
    # Obtener Lo valores del formulario
    body = dict(request.values)
    conjunto = literal_eval(body['conjunto'])
    nombre = conjunto['nombre']

    # Actualizar conjunto de datos de crudo a procesado
    act_estado =  actualizar_estado(nombre,'En Proceso')
    if act_estado: return act_estado
    
    
    # Crear prepraracion
    ejecucion = {}
    ejecucion['conjunto'] = conjunto['nombre']
    ejecucion['ejecutor'] = session['user']['correo']
    ejecucion['fechaInicial'] = getNowDate()

    # Obtener numero de ejecución para el conjunto
    status_p, body_p = get('ejecuciones/nombre/'+nombre)
    if status_p:
        ejecucion['nombre'] = body_p['nombre']
        ejecucion['numero'] = body_p['numero']
    else:
        return render_template('utils/mensaje.html', mensaje='No se pudo obtener el consecutivo de la preparación para este conjunto', submensaje=body_p)

    ########### EJECUTAR ############

    # Obtener archivo procesado
    archivo_procesado = 'P '+nombre 
    ruta = upload_folder+'/procesados/'+archivo_procesado
    exito, data_preparada = obtener_archivo_excel(ruta) 
    if not(exito): return data_preparada 
    
    # Algoritmo de ejecución
    # try:
    #     resultados_modelo,resultados_desertores = clasificador(data_preparada)
    # except Exception as e:
    #   pass
    try:
        resultados_modelo,resultados_desertores = ejecutar_modelo(data_preparada)
    except Exception as e:
        error_logger.error(e)
        try:
            error_spa = translator.translate(str(e), src='en', dest='es').text
        except:
            error_spa = str(e)
        model_logger.error(error_spa)
        model_logger.error(traceback.format_exc())
        
        resultados = {'error': error_spa }
        exito,pagina_error = guardar_ejecucion(ejecucion, resultados,'Fallida')
        ejecucion_guardada = True
        if not(exito): return pagina_error
        act_estado =  actualizar_estado(nombre,'Procesados')
        if act_estado: return act_estado
        return render_template('utils/mensaje.html', mensaje='La ejecución falló', submensaje=error_spa)
    
    if not resultados_modelo:
        # Actualizar conjunto de datos de crudo a procesado 
        act_estado =  actualizar_estado(nombre,'Procesados')
        if act_estado: return act_estado
        return render_template('utils/mensaje.html', mensaje='La ejecución falló', submensaje=resultados_desertores)

    # Guardar registro de los desertores en la BD del cli
    
    # Actualizar los resultados a ultimo 
    endpoint_ultimo = 'desercion/resultados/ultimo/{}/{}'
    endpoint_ultimo_values = endpoint_ultimo.format(conjunto['programa'], conjunto['periodoFinal'])
    status_update, body_update = put(endpoint_ultimo_values, {}) 

    # Insertar los resultados
    if resultados_desertores.any().any():
        resultados_insert = json.loads(resultados_desertores.to_json(orient='records'))
        status_insert, body_insert = post('desercion/resultados', resultados_insert) 
        if not status_update or not status_insert:
            act_estado =  actualizar_estado(nombre,'Procesados')
            if act_estado: return act_estado

            if not status_insert: 
                error_logger.error('Error insertando los nuevos desertores'.format(json.dumps(body_insert)))
                
            if not status_update: 
                error_logger.error('Error actualizando los desertores del programa'.format(json.dumps(body_update)))

            return render_template('utils/mensaje.html', mensaje='Ocurrió un error insertando y/o actualizando los resultados'), 500 
        
        estado_ejecucion = 'Exitosa'
        # Guardar resultados de desertotres en Upload folder desertores
        archivo_desertores = 'D '+ejecucion['nombre']+'.json'
        ruta = upload_folder+'/desertores/'+archivo_desertores
        exito,pagina_error = guardar_archivo(resultados_modelo.pop('desertores'), ruta, 'json')
        if not(exito): return pagina_error 

    else:
        resultados_modelo.pop('desertores')
        estado_ejecucion = 'Fallida'
    # Guardar registro de ejecución en la BD 
    if not ejecucion_guardada:
        exito, pagina_error = guardar_ejecucion(ejecucion=ejecucion, resultados=resultados_modelo ,estado=estado_ejecucion)
        if not(exito): 
            act_estado =  actualizar_estado(nombre,'Procesados')
            if act_estado: return act_estado
            return pagina_error 

    ########### FIN EJECUTAR ############
    # Actualizar conjunto de datos de crudo a procesado 
    act_estado =  actualizar_estado(nombre,'Procesados')
    if act_estado: return act_estado
    return redirect(url_for('Resultado.ejecuciones',conjunto=nombre))