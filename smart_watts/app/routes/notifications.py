# ===============================================
# app/routes/notifications.py
# ===============================================
# Rutas de Notificaciones y Alertas
#
# Gestión del centro de notificaciones:
# - Listar notificaciones
# - Marcar como leída
# - Eliminar notificaciones
# - Filtrar por tipo y fecha
# ===============================================

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app import db
from app.models import Notification

# Crear blueprint de notificaciones
notifications_bp = Blueprint('notifications', __name__, url_prefix='/notificaciones')


@notifications_bp.route('/')
@login_required
def listado():
    """
    Centro de notificaciones.
    
    Mostrar todas las notificaciones del usuario con opciones
    para filtrar, buscar y marcar como leídas.
    
    GET: Renderizar página de notificaciones
    """
    
    # Parámetros de paginación y filtrado
    pagina = request.args.get('pagina', 1, type=int)
    filtro_tipo = request.args.get('tipo', '', type=str)
    filtro_estado = request.args.get('estado', '', type=str)
    
    # Query base: notificaciones del usuario actual
    query = Notification.query.filter_by(usuario_id=current_user.id)
    
    # Aplicar filtro de tipo
    if filtro_tipo and filtro_tipo != 'todas':
        query = query.filter_by(tipo=filtro_tipo)
    
    # Aplicar filtro de estado (leída/no leída)
    if filtro_estado == 'leida':
        query = query.filter_by(leida=True)
    elif filtro_estado == 'no_leida':
        query = query.filter_by(leida=False)
    
    # Ordenar por fecha descendente (más recientes primero)
    query = query.order_by(Notification.fecha.desc())
    
    # Paginar
    paginacion = query.paginate(page=pagina, per_page=15, error_out=False)
    
    notificaciones = paginacion.items
    
    # Contar notificaciones por estado
    total_notificaciones = Notification.query.filter_by(usuario_id=current_user.id).count()
    no_leidas = Notification.query.filter_by(usuario_id=current_user.id, leida=False).count()
    leidas = total_notificaciones - no_leidas
    
    contexto = {
        'notificaciones': notificaciones,
        'paginacion': paginacion,
        'filtro_tipo': filtro_tipo,
        'filtro_estado': filtro_estado,
        'total_notificaciones': total_notificaciones,
        'no_leidas': no_leidas,
        'leidas': leidas
    }
    
    return render_template('notifications/listado.html', **contexto)


@notifications_bp.route('/<int:notificacion_id>/marcar-leida', methods=['POST'])
@login_required
def marcar_leida(notificacion_id):
    """
    Marcar una notificación como leída.
    
    Args:
        notificacion_id (int): ID de la notificación
        
    POST: Marcar como leída
    """
    
    notificacion = Notification.query.get_or_404(notificacion_id)
    
    # Verificar que la notificación pertenece al usuario
    if notificacion.usuario_id != current_user.id:
        flash('No tienes acceso a esta notificación', 'danger')
        return redirect(url_for('notifications.listado'))
    
    try:
        notificacion.marcar_como_leida()
        
        if request.is_json:
            return jsonify({'success': True})
        else:
            flash('Notificación marcada como leída', 'success')
            return redirect(url_for('notifications.listado'))
    
    except Exception as e:
        if request.is_json:
            return jsonify({'error': str(e)}), 400
        else:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('notifications.listado'))


@notifications_bp.route('/<int:notificacion_id>/marcar-no-leida', methods=['POST'])
@login_required
def marcar_no_leida(notificacion_id):
    """
    Marcar una notificación como no leída.
    
    Args:
        notificacion_id (int): ID de la notificación
        
    POST: Marcar como no leída
    """
    
    notificacion = Notification.query.get_or_404(notificacion_id)
    
    if notificacion.usuario_id != current_user.id:
        flash('No tienes acceso a esta notificación', 'danger')
        return redirect(url_for('notifications.listado'))
    
    try:
        notificacion.marcar_como_no_leida()
        
        if request.is_json:
            return jsonify({'success': True})
        else:
            flash('Notificación marcada como no leída', 'success')
            return redirect(url_for('notifications.listado'))
    
    except Exception as e:
        if request.is_json:
            return jsonify({'error': str(e)}), 400
        else:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('notifications.listado'))


@notifications_bp.route('/<int:notificacion_id>/eliminar', methods=['POST'])
@login_required
def eliminar(notificacion_id):
    """
    Eliminar una notificación.
    
    Args:
        notificacion_id (int): ID de la notificación
        
    POST: Eliminar notificación
    """
    
    notificacion = Notification.query.get_or_404(notificacion_id)
    
    if notificacion.usuario_id != current_user.id:
        flash('No tienes acceso a esta notificación', 'danger')
        return redirect(url_for('notifications.listado'))
    
    try:
        db.session.delete(notificacion)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True})
        else:
            flash('Notificación eliminada', 'success')
            return redirect(url_for('notifications.listado'))
    
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'error': str(e)}), 400
        else:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('notifications.listado'))


@notifications_bp.route('/marcar-todas-leidas', methods=['POST'])
@login_required
def marcar_todas_leidas():
    """
    Marcar todas las notificaciones del usuario como leídas.
    
    POST: Marcar todas como leídas
    """
    
    try:
        notificaciones = Notification.query.filter_by(
            usuario_id=current_user.id,
            leida=False
        ).all()
        
        for notificacion in notificaciones:
            notificacion.leida = True
        
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'cantidad': len(notificaciones)})
        else:
            flash(f'{len(notificaciones)} notificaciones marcadas como leídas', 'success')
            return redirect(url_for('notifications.listado'))
    
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'error': str(e)}), 400
        else:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('notifications.listado'))


@notifications_bp.route('/limpiar', methods=['POST'])
@login_required
def limpiar():
    """
    Eliminar todas las notificaciones leídas del usuario.
    
    POST: Eliminar notificaciones leídas
    """
    
    try:
        notificaciones = Notification.query.filter_by(
            usuario_id=current_user.id,
            leida=True
        ).all()
        
        cantidad = len(notificaciones)
        
        for notificacion in notificaciones:
            db.session.delete(notificacion)
        
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'cantidad': cantidad})
        else:
            flash(f'{cantidad} notificaciones eliminadas', 'success')
            return redirect(url_for('notifications.listado'))
    
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'error': str(e)}), 400
        else:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('notifications.listado'))


@notifications_bp.route('/api/sin-leer')
@login_required
def api_sin_leer():
    """
    API endpoint para obtener notificaciones no leídas.
    
    Usado por AJAX/SocketIO para actualizar contador en tiempo real.
    
    GET: Devolver JSON con notificaciones no leídas
    """
    
    notificaciones_no_leidas = Notification.obtener_no_leidas(current_user.id)
    
    return jsonify({
        'cantidad': len(notificaciones_no_leidas),
        'notificaciones': [
            {
                'id': n.id,
                'tipo': n.tipo,
                'mensaje': n.mensaje,
                'fecha': n.fecha.isoformat()
            }
            for n in notificaciones_no_leidas[:5]  # Últimas 5
        ]
    })
