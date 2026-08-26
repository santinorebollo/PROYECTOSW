# ===============================================
# app/routes/api.py
# ===============================================
# API REST para Dispositivos IoT
#
# Proporciona endpoints JSON para:
# - Enviar lecturas desde dispositivos
# - Consultar datos
# - Gestionar dispositivos
# 
# Los dispositivos se autentican usando token_api
# ===============================================

from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from app.models import Device, Reading, Notification
import secrets

# Crear blueprint de API
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


def autenticar_dispositivo(f):
    """
    Decorador para autenticar dispositivos por token.
    
    El dispositivo debe enviar:
    Authorization: Bearer <token_api>
    """
    from functools import wraps
    
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Obtener token del header Authorization
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token no proporcionado'}), 401
        
        token = auth_header.split(' ')[1]
        
        # Buscar dispositivo por token
        dispositivo = Device.query.filter_by(token_api=token).first()
        
        if not dispositivo:
            return jsonify({'error': 'Token inválido'}), 401
        
        # Pasar dispositivo a la función
        kwargs['dispositivo'] = dispositivo
        return f(*args, **kwargs)
    
    return wrapper


@api_bp.route('/dispositivos', methods=['GET'])
def obtener_dispositivos():
    """
    Obtener listado de dispositivos.
    
    GET: Devolver JSON con todos los dispositivos
    """
    
    dispositivos = Device.query.all()
    
    return jsonify({
        'total': len(dispositivos),
        'dispositivos': [d.to_dict() for d in dispositivos]
    })


@api_bp.route('/dispositivos/<int:dispositivo_id>', methods=['GET'])
def obtener_dispositivo(dispositivo_id):
    """
    Obtener datos de un dispositivo específico.
    
    Args:
        dispositivo_id (int): ID del dispositivo
        
    GET: Devolver JSON con datos del dispositivo
    """
    
    dispositivo = Device.query.get_or_404(dispositivo_id)
    return jsonify(dispositivo.to_dict())


@api_bp.route('/lecturas', methods=['POST'])
@autenticar_dispositivo
def crear_lectura(dispositivo):
    """
    Crear una nueva lectura de energía.
    
    El dispositivo envía sus mediciones en formato JSON:
    {
        "voltaje": 220.5,
        "corriente": 5.2,
        "potencia": 1000,
        "consumo": 0.5,
        "frecuencia": 50,
        "factor_potencia": 0.95
    }
    
    POST: Guardar lectura en BD
    """
    
    # Validar que es JSON
    if not request.is_json:
        return jsonify({'error': 'Content-Type debe ser application/json'}), 400
    
    datos = request.get_json()
    
    # Validar campos requeridos
    campos_requeridos = ['voltaje', 'corriente', 'potencia']
    
    for campo in campos_requeridos:
        if campo not in datos:
            return jsonify({'error': f'Campo requerido: {campo}'}), 400
    
    try:
        # Validar que los valores sean números
        voltaje = float(datos.get('voltaje'))
        corriente = float(datos.get('corriente'))
        potencia = float(datos.get('potencia'))
        consumo = float(datos.get('consumo', 0))
        frecuencia = float(datos.get('frecuencia', 50))
        factor_potencia = float(datos.get('factor_potencia', 1.0))
        
        # Validaciones de rango
        if voltaje < 0 or voltaje > 500:
            return jsonify({'error': 'Voltaje fuera de rango'}), 400
        
        if corriente < 0 or corriente > 100:
            return jsonify({'error': 'Corriente fuera de rango'}), 400
        
        if potencia < 0:
            return jsonify({'error': 'Potencia no puede ser negativa'}), 400
        
        if consumo < 0:
            return jsonify({'error': 'Consumo no puede ser negativo'}), 400
        
        if factor_potencia < 0 or factor_potencia > 1.0:
            return jsonify({'error': 'Factor de potencia debe estar entre 0 y 1'}), 400
        
        # Crear lectura
        lectura = Reading(
            device_id=dispositivo.id,
            voltaje=voltaje,
            corriente=corriente,
            potencia=potencia,
            consumo=consumo,
            frecuencia=frecuencia,
            factor_potencia=factor_potencia,
            fecha_hora=datetime.utcnow()
        )
        
        # Guardar lectura
        db.session.add(lectura)
        
        # Actualizar última conexión del dispositivo
        dispositivo.actualizar_ultima_conexion()
        
        db.session.commit()
        
        # ==================== VERIFICAR ALERTAS ====================
        
        # Verificar si hay anomalías
        if lectura.es_anomalia(desviacion_std=3):
            Notification.crear_alerta_consumo(
                dispositivo.usuario_id,
                dispositivo.id,
                potencia,
                1000  # Límite por defecto
            )
        
        # Verificar presupuesto
        from app.models import Budget
        presupuesto = Budget.obtener_o_crear_para_usuario(dispositivo.usuario_id)
        alerta_necesaria = presupuesto.obtener_alerta_necesaria()
        
        if alerta_necesaria:
            # Verificar si ya existe alerta para este hito
            alerta_existente = Notification.query.filter(
                Notification.usuario_id == dispositivo.usuario_id,
                Notification.tipo == 'presupuesto',
                Notification.mensaje.ilike(f'%{alerta_necesaria}%')
            ).first()
            
            if not alerta_existente:
                Notification.crear_alerta_presupuesto(
                    dispositivo.usuario_id,
                    presupuesto.obtener_porcentaje_usado(),
                    alerta_necesaria
                )
        
        return jsonify({
            'success': True,
            'lectura_id': lectura.id,
            'mensaje': 'Lectura guardada exitosamente'
        }), 201
    
    except ValueError as e:
        return jsonify({'error': f'Valor inválido: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/lecturas', methods=['GET'])
def obtener_lecturas():
    """
    Obtener lecturas de los últimos N minutos.
    
    Parámetros de query:
    - dispositivo_id: ID del dispositivo (opcional)
    - minutos: Últimos N minutos (default 60)
    - limite: Máximo de resultados (default 100)
    
    GET: Devolver JSON con lecturas
    """
    
    dispositivo_id = request.args.get('dispositivo_id', type=int)
    minutos = request.args.get('minutos', 60, type=int)
    limite = request.args.get('limite', 100, type=int)
    
    from datetime import timedelta
    
    hace = datetime.utcnow() - timedelta(minutes=minutos)
    
    query = Reading.query.filter(Reading.fecha_hora >= hace)
    
    if dispositivo_id:
        query = query.filter_by(device_id=dispositivo_id)
    
    lecturas = query.order_by(Reading.fecha_hora.desc()).limit(limite).all()
    
    return jsonify({
        'total': len(lecturas),
        'lecturas': [l.to_dict() for l in lecturas]
    })


@api_bp.route('/dispositivos/<int:dispositivo_id>/lecturas-recientes', methods=['GET'])
def obtener_lecturas_recientes(dispositivo_id):
    """
    Obtener lecturas recientes de un dispositivo específico.
    
    Args:
        dispositivo_id (int): ID del dispositivo
        
    GET: Devolver últimas 20 lecturas
    """
    
    dispositivo = Device.query.get_or_404(dispositivo_id)
    
    lecturas = Reading.query.filter_by(
        device_id=dispositivo_id
    ).order_by(Reading.fecha_hora.desc()).limit(20).all()
    
    return jsonify({
        'dispositivo_id': dispositivo_id,
        'total': len(lecturas),
        'lecturas': [l.to_dict() for l in lecturas]
    })


@api_bp.route('/dispositivos/<int:dispositivo_id>/consumo-total', methods=['GET'])
def obtener_consumo_total(dispositivo_id):
    """
    Obtener consumo total de un dispositivo.
    
    Parámetros:
    - desde: Fecha inicio (ISO format)
    - hasta: Fecha fin (ISO format)
    
    Args:
        dispositivo_id (int): ID del dispositivo
        
    GET: Devolver consumo total en kWh
    """
    
    dispositivo = Device.query.get_or_404(dispositivo_id)
    
    desde = request.args.get('desde')
    hasta = request.args.get('hasta')
    
    fecha_inicio = None
    fecha_fin = None
    
    if desde:
        try:
            fecha_inicio = datetime.fromisoformat(desde)
        except:
            return jsonify({'error': 'Fecha inicio inválida'}), 400
    
    if hasta:
        try:
            fecha_fin = datetime.fromisoformat(hasta)
        except:
            return jsonify({'error': 'Fecha fin inválida'}), 400
    
    consumo = dispositivo.obtener_consumo_total(fecha_inicio, fecha_fin)
    
    return jsonify({
        'dispositivo_id': dispositivo_id,
        'consumo_total_kwh': round(consumo, 3),
        'desde': desde,
        'hasta': hasta
    })


@api_bp.route('/estado', methods=['GET'])
def estado_api():
    """
    Endpoint de prueba/estado de la API.
    
    GET: Devolver información del estado
    """
    
    return jsonify({
        'status': 'online',
        'version': '1.0.0',
        'nombre': 'Smart Watts API',
        'timestamp': datetime.utcnow().isoformat()
    })


@api_bp.errorhandler(404)
def no_encontrado(error):
    """Manejo de error 404 en API"""
    return jsonify({'error': 'Recurso no encontrado'}), 404


@api_bp.errorhandler(500)
def error_servidor(error):
    """Manejo de error 500 en API"""
    return jsonify({'error': 'Error interno del servidor'}), 500
