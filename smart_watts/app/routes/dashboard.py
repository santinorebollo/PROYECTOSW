# ===============================================
# app/routes/dashboard.py
# ===============================================
# Rutas del Dashboard Principal
#
# Contiene la página principal con:
# - Resumen de consumo
# - Gráficos en tiempo real
# - Alertas activas
# - Estadísticas rápidas
# - Dispositivos conectados
# ===============================================

from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func
from app import db
from app.models import Device, Reading, Notification, Budget, EnergyRate

# Crear blueprint del dashboard
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/')


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    """
    Ruta principal del dashboard.
    
    Muestra:
    - Resumen de consumo actual
    - Dispositivos activos/inactivos
    - Alertas recientes
    - Gráficos de consumo
    - Presupuesto disponible
    - Proyección de gasto
    
    GET: Renderizar página del dashboard
    """
    
    # ==================== OBTENER DATOS ====================
    
    # Obtener dispositivos del usuario
    dispositivos = current_user.dispositivos.all()
    
    # Contar dispositivos activos e inactivos
    activos = sum(1 for d in dispositivos if d.obtener_estado_conexion() == 'activo')
    inactivos = len(dispositivos) - activos
    
    # Obtener última lectura de cada dispositivo
    ultimas_lecturas = {}
    consumo_total_hoy = 0
    potencia_actual_total = 0
    
    for dispositivo in dispositivos:
        lectura = dispositivo.obtener_ultima_lectura()
        if lectura:
            ultimas_lecturas[dispositivo.id] = lectura
            potencia_actual_total += lectura.potencia
        
        # Consumo desde hoy a las 00:00
        hoy = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        consumo_total_hoy += dispositivo.obtener_consumo_total(hoy)
    
    # Obtener presupuesto del usuario para este mes
    presupuesto = Budget.obtener_o_crear_para_usuario(current_user.id)
    gasto_actual = presupuesto.obtener_gasto_actual()
    porcentaje_presupuesto = presupuesto.obtener_porcentaje_usado()
    
    # Obtener tarifa energética actual
    tarifa = EnergyRate.obtener_tarifa_actual()
    costo_actual_estimado = 0
    costo_proyectado = 0
    
    if tarifa:
        # Costo estimado del consumo de hoy
        _, _, costo_actual_estimado = tarifa.calcular_costo_kwh(consumo_total_hoy)
        
        # Proyección para el mes
        # Asumir que cada día es igual al promedio hasta ahora
        dias_pasados = datetime.utcnow().day
        consumo_promedio_diario = consumo_total_hoy / dias_pasados if dias_pasados > 0 else 0
        dias_mes = 30  # Promedio
        consumo_proyectado = consumo_promedio_diario * dias_mes
        _, _, costo_proyectado = tarifa.calcular_costo_kwh(consumo_proyectado)
    
    # Obtener últimas alertas no leídas
    alertas_activas = Notification.obtener_no_leidas(current_user.id)[:5]
    
    # Obtener lecturas de las últimas 24 horas para gráfico
    hace_24h = datetime.utcnow() - timedelta(hours=24)
    
    lecturas_24h = Reading.query.filter(
        Reading.device_id.in_([d.id for d in dispositivos]),
        Reading.fecha_hora >= hace_24h
    ).order_by(Reading.fecha_hora).all()
    
    # Agrupar lecturas por hora para gráfico
    consumo_por_hora = {}
    for lectura in lecturas_24h:
        hora = lectura.fecha_hora.replace(minute=0, second=0, microsecond=0)
        if hora not in consumo_por_hora:
            consumo_por_hora[hora] = 0
        consumo_por_hora[hora] += lectura.consumo
    
    # Preparar datos para template
    datos_consumo_24h = {
        'labels': [h.strftime('%H:%M') for h in sorted(consumo_por_hora.keys())],
        'consumo': list(sorted(consumo_por_hora.values()))
    }
    
    # ==================== PREPARAR CONTEXTO ====================
    
    contexto = {
        'dispositivos_totales': len(dispositivos),
        'dispositivos_activos': activos,
        'dispositivos_inactivos': inactivos,
        'potencia_actual': round(potencia_actual_total, 2),
        'consumo_hoy': round(consumo_total_hoy, 3),
        'costo_actual_estimado': round(costo_actual_estimado, 2),
        'costo_proyectado': round(costo_proyectado, 2),
        'presupuesto_mensual': round(presupuesto.presupuesto_mensual, 2),
        'gasto_actual': round(gasto_actual, 2),
        'dinero_restante': round(presupuesto.obtener_dinero_restante(), 2),
        'porcentaje_presupuesto': round(porcentaje_presupuesto, 1),
        'alertas_activas': alertas_activas,
        'alertas_no_leidas': Notification.contar_no_leidas(current_user.id),
        'ultimas_lecturas': ultimas_lecturas,
        'datos_consumo_24h': datos_consumo_24h
    }
    
    return render_template('dashboard/index.html', **contexto)


@dashboard_bp.route('/api/datos-tiempo-real')
@login_required
def datos_tiempo_real():
    """
    Endpoint para obtener datos actualizados en tiempo real.
    
    Devuelve JSON con:
    - Potencia instantánea actual
    - Consumo del día actual
    - Estado de dispositivos
    - Nuevas alertas
    
    GET: Devolver JSON con datos actuales
    """
    
    dispositivos = current_user.dispositivos.all()
    
    # Obtener datos actuales
    potencia_total = 0
    consumo_hoy = 0
    dispositivos_estado = []
    
    hoy = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    for dispositivo in dispositivos:
        lectura = dispositivo.obtener_ultima_lectura()
        
        if lectura:
            potencia_total += lectura.potencia
        
        consumo_hoy += dispositivo.obtener_consumo_total(hoy)
        
        dispositivos_estado.append({
            'id': dispositivo.id,
            'nombre': dispositivo.nombre,
            'estado': dispositivo.obtener_estado_conexion(),
            'potencia': lectura.potencia if lectura else 0
        })
    
    # Obtener nuevas alertas
    alertas_recientes = Notification.obtener_no_leidas(current_user.id)[:3]
    
    return jsonify({
        'potencia_total': round(potencia_total, 2),
        'consumo_hoy': round(consumo_hoy, 3),
        'dispositivos': dispositivos_estado,
        'alertas': [
            {
                'id': a.id,
                'tipo': a.tipo,
                'mensaje': a.mensaje,
                'fecha': a.fecha.isoformat()
            }
            for a in alertas_recientes
        ]
    })


@dashboard_bp.route('/api/grafico-consumo/<periodo>')
@login_required
def grafico_consumo(periodo):
    """
    Endpoint para obtener datos de gráfico de consumo.
    
    Períodos:
    - 'dia': Últimas 24 horas
    - 'semana': Últimos 7 días
    - 'mes': Últimos 30 días
    
    Args:
        periodo (str): Período de tiempo solicitado
        
    GET: Devolver JSON con datos para gráfico
    """
    
    dispositivos = [d.id for d in current_user.dispositivos]
    
    if not dispositivos:
        return jsonify({'labels': [], 'consumo': []})
    
    # Calcular rango de tiempo
    ahora = datetime.utcnow()
    
    if periodo == 'dia':
        fecha_inicio = ahora - timedelta(hours=24)
        agrupar_por = 'hora'
    elif periodo == 'semana':
        fecha_inicio = ahora - timedelta(days=7)
        agrupar_por = 'dia'
    elif periodo == 'mes':
        fecha_inicio = ahora - timedelta(days=30)
        agrupar_por = 'dia'
    else:
        fecha_inicio = ahora - timedelta(hours=24)
        agrupar_por = 'hora'
    
    # Obtener lecturas
    lecturas = Reading.query.filter(
        Reading.device_id.in_(dispositivos),
        Reading.fecha_hora >= fecha_inicio
    ).order_by(Reading.fecha_hora).all()
    
    # Agrupar por período
    consumo_agrupado = {}
    
    for lectura in lecturas:
        if agrupar_por == 'hora':
            clave = lectura.fecha_hora.replace(minute=0, second=0, microsecond=0)
            formato = '%H:%M'
        else:  # día
            clave = lectura.fecha_hora.replace(hour=0, minute=0, second=0, microsecond=0)
            formato = '%Y-%m-%d'
        
        if clave not in consumo_agrupado:
            consumo_agrupado[clave] = 0
        consumo_agrupado[clave] += lectura.consumo
    
    # Preparar datos
    labels = [k.strftime(formato) for k in sorted(consumo_agrupado.keys())]
    valores = list(dict(sorted(consumo_agrupado.items())).values())
    
    return jsonify({
        'labels': labels,
        'consumo': valores
    })


@dashboard_bp.route('/api/estado-dispositivos')
@login_required
def estado_dispositivos():
    """
    Endpoint para obtener estado de todos los dispositivos.
    
    GET: Devolver JSON con estado de cada dispositivo
    """
    
    dispositivos = current_user.dispositivos.all()
    
    datos = []
    for dispositivo in dispositivos:
        lectura = dispositivo.obtener_ultima_lectura()
        
        datos.append({
            'id': dispositivo.id,
            'nombre': dispositivo.nombre,
            'ubicacion': dispositivo.ubicacion,
            'estado': dispositivo.obtener_estado_conexion(),
            'potencia': lectura.potencia if lectura else None,
            'voltaje': lectura.voltaje if lectura else None,
            'corriente': lectura.corriente if lectura else None,
            'ultima_conexion': dispositivo.ultima_conexion.isoformat() if dispositivo.ultima_conexion else None
        })
    
    return jsonify(datos)
