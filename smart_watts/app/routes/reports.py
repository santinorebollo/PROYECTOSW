# ===============================================
# app/routes/reports.py
# ===============================================
# Blueprint para reportes y configuración
# Contiene rutas para:
# - Generación de reportes diarios, semanales, mensuales
# - Configuración de presupuesto y tarifas
# - Perfil de usuario
# ===============================================

import csv
import io
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, Response
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from app.models import Device, Reading, Budget, EnergyRate, User
from app.forms import ConfigurarPresupuestoForm, ConfiguracionTarifasForm, EditarPerfilForm
from app import db


# ==================== BLUEPRINTS ====================
reports_bp = Blueprint('reports', __name__, url_prefix='/reportes')
settings_bp = Blueprint('settings', __name__, url_prefix='/configuracion')


# ==================== REPORTES ====================

@reports_bp.route('/listado')
@login_required
def listado():
    """
    Página principal de reportes con links a reportes específicos.
    """
    return render_template('reports/listado.html')


@reports_bp.route('/diario')
@login_required
def diario():
    """
    Reporte diario con estadísticas de hoy.
    
    GET: Mostrar reporte del día actual
    Incluye: consumo total, costo, gráfico de consumo por hora
    """
    hoy = datetime.now().date()
    
    # Obtener dispositivos del usuario
    dispositivos = Device.query.filter_by(usuario_id=current_user.id).all()
    
    if not dispositivos:
        flash('No tienes dispositivos registrados', 'warning')
        return redirect(url_for('dashboard.index'))
    
    device_ids = [d.id for d in dispositivos]
    
    # Consumo total del día
    consumo_total = db.session.query(
        func.sum(Reading.consumo)
    ).filter(
        and_(
            Reading.device_id.in_(device_ids),
            func.date(Reading.fecha_hora) == hoy
        )
    ).scalar() or 0
    
    # Costo del consumo
    tarifa = EnergyRate.obtener_tarifa_actual()
    costo = consumo_total * tarifa.precio_kwh if tarifa else 0
    
    # Datos para gráfico por hora
    lecturas = db.session.query(
        func.extract('hour', Reading.fecha_hora).label('hora'),
        func.sum(Reading.consumo).label('consumo')
    ).filter(
        and_(
            Reading.device_id.in_(device_ids),
            func.date(Reading.fecha_hora) == hoy
        )
    ).group_by(
        func.extract('hour', Reading.fecha_hora)
    ).all()
    
    horas = [str(int(r[0])) + ':00' for r in lecturas]
    consumos = [float(r[1]) or 0 for r in lecturas]
    
    return render_template('reports/diario.html',
        consumo_total=round(consumo_total, 2),
        costo=round(costo, 2),
        horas=horas,
        consumos=consumos
    )


@reports_bp.route('/semanal')
@login_required
def semanal():
    """
    Reporte semanal con estadísticas de los últimos 7 días.
    
    GET: Mostrar reporte semanal
    Incluye: consumo por día, comparativa
    """
    hoy = datetime.now().date()
    hace_7_dias = hoy - timedelta(days=7)
    
    dispositivos = Device.query.filter_by(usuario_id=current_user.id).all()
    if not dispositivos:
        flash('No tienes dispositivos registrados', 'warning')
        return redirect(url_for('dashboard.index'))
    
    device_ids = [d.id for d in dispositivos]
    
    # Consumo por día
    lecturas = db.session.query(
        func.date(Reading.fecha_hora).label('fecha'),
        func.sum(Reading.consumo).label('consumo')
    ).filter(
        and_(
            Reading.device_id.in_(device_ids),
            func.date(Reading.fecha_hora).between(hace_7_dias, hoy)
        )
    ).group_by(
        func.date(Reading.fecha_hora)
    ).all()
    
    fechas = [str(r[0]) for r in lecturas]
    consumos = [float(r[1]) or 0 for r in lecturas]
    
    return render_template('reports/semanal.html',
        fechas=fechas,
        consumos=consumos
    )


@reports_bp.route('/mensual')
@login_required
def mensual():
    """
    Reporte mensual con estadísticas y comparativa con presupuesto.
    
    GET: Mostrar reporte del mes actual
    Incluye: consumo total, costo, presupuesto, progreso
    """
    hoy = datetime.now().date()
    primer_dia_mes = hoy.replace(day=1)
    
    dispositivos = Device.query.filter_by(usuario_id=current_user.id).all()
    if not dispositivos:
        flash('No tienes dispositivos registrados', 'warning')
        return redirect(url_for('dashboard.index'))
    
    device_ids = [d.id for d in dispositivos]
    
    # Consumo del mes
    consumo_mes = db.session.query(
        func.sum(Reading.consumo)
    ).filter(
        and_(
            Reading.device_id.in_(device_ids),
            func.date(Reading.fecha_hora) >= primer_dia_mes
        )
    ).scalar() or 0
    
    # Tarifa y costo
    tarifa = EnergyRate.obtener_tarifa_actual()
    costo_mes = consumo_mes * tarifa.precio_kwh if tarifa else 0
    
    # Presupuesto
    presupuesto = Budget.obtener_o_crear_para_usuario(current_user.id)
    porcentaje = (costo_mes / presupuesto.presupuesto_mensual * 100) if presupuesto.presupuesto_mensual > 0 else 0
    
    # Top dispositivos
    top_dispositivos = db.session.query(
        Device.nombre,
        func.sum(Reading.consumo).label('total')
    ).join(Reading).filter(
        and_(
            Device.usuario_id == current_user.id,
            func.date(Reading.fecha_hora) >= primer_dia_mes
        )
    ).group_by(Device.nombre).order_by(func.sum(Reading.consumo).desc()).limit(5).all()
    
    return render_template('reports/mensual.html',
        consumo_mes=round(consumo_mes, 2),
        costo_mes=round(costo_mes, 2),
        presupuesto=presupuesto,
        porcentaje=round(porcentaje, 1),
        top_dispositivos=top_dispositivos
    )


@reports_bp.route('/exportar/<tipo>')
@login_required
def exportar(tipo):
    """
    Exportar las lecturas de consumo del periodo seleccionado a CSV.

    Args:
        tipo (str): 'diario', 'semanal' o 'mensual'
    """
    hoy = datetime.now().date()

    if tipo == 'diario':
        fecha_inicio = hoy
    elif tipo == 'semanal':
        fecha_inicio = hoy - timedelta(days=7)
    elif tipo == 'mensual':
        fecha_inicio = hoy.replace(day=1)
    else:
        flash('Tipo de reporte inválido', 'danger')
        return redirect(url_for('reports.listado'))

    dispositivos = Device.query.filter_by(usuario_id=current_user.id).all()
    device_ids = [d.id for d in dispositivos]
    nombres_dispositivos = {d.id: d.nombre for d in dispositivos}

    lecturas = []
    if device_ids:
        lecturas = Reading.query.filter(
            and_(
                Reading.device_id.in_(device_ids),
                func.date(Reading.fecha_hora) >= fecha_inicio
            )
        ).order_by(Reading.fecha_hora.asc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Fecha/Hora', 'Dispositivo', 'Voltaje (V)', 'Corriente (A)', 'Potencia (W)', 'Consumo (kWh)', 'Factor de Potencia'])

    for lectura in lecturas:
        writer.writerow([
            lectura.fecha_hora.strftime('%Y-%m-%d %H:%M:%S'),
            nombres_dispositivos.get(lectura.device_id, '-'),
            lectura.voltaje,
            lectura.corriente,
            lectura.potencia,
            lectura.consumo,
            lectura.factor_potencia
        ])

    nombre_archivo = f'reporte_{tipo}_{hoy.strftime("%Y%m%d")}.csv'

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={nombre_archivo}'}
    )


# ==================== CONFIGURACIÓN ====================

@settings_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    """
    Editar perfil del usuario.
    
    GET: Mostrar formulario con datos del usuario
    POST: Actualizar perfil
    """
    form = EditarPerfilForm()
    
    if form.validate_on_submit():
        current_user.nombre = form.nombre.data
        current_user.email = form.email.data

        db.session.commit()
        flash('Perfil actualizado correctamente', 'success')
        return redirect(url_for('settings.perfil'))
    
    elif request.method == 'GET':
        form.nombre.data = current_user.nombre
        form.email.data = current_user.email
    
    return render_template('settings/perfil.html', form=form)


@settings_bp.route('/presupuesto', methods=['GET', 'POST'])
@login_required
def presupuesto():
    """
    Configurar presupuesto mensual.
    
    GET: Mostrar formulario con presupuesto actual
    POST: Actualizar presupuesto
    """
    presupuesto_obj = Budget.obtener_o_crear_para_usuario(current_user.id)
    form = ConfigurarPresupuestoForm()
    
    if form.validate_on_submit():
        presupuesto_obj.presupuesto_mensual = float(form.presupuesto_mensual.data)
        presupuesto_obj.fecha = datetime.now()
        db.session.commit()
        flash('Presupuesto actualizado correctamente', 'success')
        return redirect(url_for('settings.presupuesto'))

    elif request.method == 'GET':
        form.presupuesto_mensual.data = presupuesto_obj.presupuesto_mensual
    
    gasto_actual = presupuesto_obj.obtener_gasto_actual()
    porcentaje = presupuesto_obj.obtener_porcentaje_usado()
    
    return render_template('settings/presupuesto.html',
        form=form,
        gasto_actual=round(gasto_actual, 2),
        porcentaje=round(porcentaje, 1)
    )


@settings_bp.route('/tarifas', methods=['GET', 'POST'])
@login_required
def tarifas():
    """
    Configurar tarifas energéticas (solo admin).
    
    GET: Mostrar formulario con tarifas actuales
    POST: Actualizar tarifas
    """
    
    if not current_user.es_admin():
        flash('No tienes permisos de administrador', 'danger')
        return redirect(url_for('dashboard.index'))

    tarifa = EnergyRate.obtener_tarifa_actual()
    if not tarifa:
        tarifa = EnergyRate(precio_kwh=50.0, impuestos=10.0, cargos_fijos=200.0)
        db.session.add(tarifa)
        db.session.commit()

    form = ConfiguracionTarifasForm()

    if form.validate_on_submit():
        tarifa.precio_kwh = float(form.precio_kwh.data)
        tarifa.impuestos = float(form.impuestos.data)
        tarifa.cargos_fijos = float(form.cargos_fijos.data)
        tarifa.fecha_actualizacion = datetime.now()
        db.session.commit()
        flash('Tarifas actualizadas correctamente', 'success')
        return redirect(url_for('settings.tarifas'))
    
    elif request.method == 'GET':
        form.precio_kwh.data = tarifa.precio_kwh
        form.impuestos.data = tarifa.impuestos
        form.cargos_fijos.data = tarifa.cargos_fijos
    
    return render_template('settings/tarifas.html', form=form)


@settings_bp.route('/api/presupuesto-info')
@login_required
def api_presupuesto_info():
    """
    API para obtener información del presupuesto en JSON.
    """
    presupuesto = Budget.obtener_o_crear_para_usuario(current_user.id)
    gasto = presupuesto.obtener_gasto_actual()
    
    return jsonify({
        'presupuesto': presupuesto.presupuesto_mensual,
        'gasto': round(gasto, 2),
        'porcentaje': round(presupuesto.obtener_porcentaje_usado(), 1),
        'restante': round(presupuesto.obtener_dinero_restante(), 2)
    })
