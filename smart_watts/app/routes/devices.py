# ===============================================
# app/routes/devices.py
# ===============================================
# Rutas de Gestión de Dispositivos
#
# Contiene operaciones CRUD:
# - Crear dispositivo
# - Ver dispositivos
# - Editar dispositivo
# - Eliminar dispositivo
# - Asociar dispositivo a usuario
# ===============================================

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_
import secrets
from datetime import datetime
from app import db
from app.models import Device, User, Reading
from app.forms import CrearDispositivoForm, EditarDispositivoForm

# Crear blueprint de dispositivos
devices_bp = Blueprint('devices', __name__, url_prefix='/dispositivos')


def es_admin():
    """Verificar si el usuario actual es administrador"""
    return current_user.is_authenticated and current_user.rol == 'admin'


@devices_bp.route('/')
@login_required
def listado():
    """
    Listar todos los dispositivos.
    
    - Administrador: Ve todos los dispositivos
    - Usuario: Ve solo sus dispositivos
    
    GET: Renderizar página con listado de dispositivos
    """
    
    # Página actual para paginación
    pagina = request.args.get('pagina', 1, type=int)
    
    # Búsqueda
    buscar = request.args.get('buscar', '', type=str)
    
    if es_admin():
        # Admin ve todos los dispositivos
        query = Device.query
    else:
        # Usuarios ven solo sus dispositivos
        query = Device.query.filter_by(usuario_id=current_user.id)
    
    # Aplicar búsqueda
    if buscar:
        query = query.filter(
            or_(
                Device.nombre.ilike(f'%{buscar}%'),
                Device.ubicacion.ilike(f'%{buscar}%')
            )
        )
    
    # Paginar
    paginacion = query.paginate(
        page=pagina,
        per_page=10,
        error_out=False
    )
    
    dispositivos = paginacion.items
    
    return render_template(
        'devices/listado.html',
        dispositivos=dispositivos,
        paginacion=paginacion,
        buscar=buscar
    )


@devices_bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear():
    """
    Crear un nuevo dispositivo.
    
    GET: Mostrar formulario de creación
    POST: Crear dispositivo en base de datos
    
    Solo administradores pueden crear dispositivos inicialmente.
    """
    
    # Solo admins pueden crear dispositivos
    if not es_admin():
        flash('No tienes permiso para crear dispositivos', 'danger')
        return redirect(url_for('devices.listado'))
    
    form = CrearDispositivoForm()
    
    if form.validate_on_submit():
        try:
            # Generar token único para el dispositivo
            token = secrets.token_urlsafe(32)
            
            # Crear dispositivo
            dispositivo = Device(
                nombre=form.nombre.data,
                ubicacion=form.ubicacion.data,
                firmware=form.firmware.data,
                usuario_id=current_user.id,  # Asignar al usuario actual
                estado='inactivo',
                token_api=token
            )
            
            db.session.add(dispositivo)
            db.session.commit()
            
            flash(f'Dispositivo "{dispositivo.nombre}" creado exitosamente', 'success')
            flash(f'Token de API: {token} (guárdalo para configurar el dispositivo)', 'info')
            
            return redirect(url_for('devices.ver', dispositivo_id=dispositivo.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear dispositivo: {str(e)}', 'danger')
    
    return render_template('devices/crear.html', form=form)


@devices_bp.route('/<int:dispositivo_id>')
@login_required
def ver(dispositivo_id):
    """
    Ver detalles de un dispositivo.
    
    Args:
        dispositivo_id (int): ID del dispositivo a ver
        
    GET: Renderizar página de detalles del dispositivo
    """
    
    dispositivo = Device.query.get_or_404(dispositivo_id)
    
    # Verificar permisos
    if not es_admin() and dispositivo.usuario_id != current_user.id:
        flash('No tienes acceso a este dispositivo', 'danger')
        return redirect(url_for('devices.listado'))
    
    # Obtener última lectura
    ultima_lectura = dispositivo.obtener_ultima_lectura()
    
    # Obtener consumo total
    consumo_total = dispositivo.obtener_consumo_total()
    
    # Obtener lecturas recientes (últimas 10)
    lecturas_recientes = dispositivo.lecturas.order_by(Reading.fecha_hora.desc()).limit(10).all()
    
    # Estadísticas
    todas_las_lecturas = dispositivo.lecturas.all()
    
    if todas_las_lecturas:
        potencia_promedio = sum(l.potencia for l in todas_las_lecturas) / len(todas_las_lecturas)
        potencia_maxima = max(l.potencia for l in todas_las_lecturas)
        potencia_minima = min(l.potencia for l in todas_las_lecturas)
    else:
        potencia_promedio = potencia_maxima = potencia_minima = 0
    
    contexto = {
        'dispositivo': dispositivo,
        'ultima_lectura': ultima_lectura,
        'consumo_total': consumo_total,
        'lecturas_recientes': lecturas_recientes,
        'potencia_promedio': round(potencia_promedio, 2),
        'potencia_maxima': round(potencia_maxima, 2),
        'potencia_minima': round(potencia_minima, 2),
        'estado_conexion': dispositivo.obtener_estado_conexion()
    }
    
    return render_template('devices/ver.html', **contexto)


@devices_bp.route('/<int:dispositivo_id>/editar', methods=['GET', 'POST'])
@login_required
def editar(dispositivo_id):
    """
    Editar un dispositivo existente.
    
    Args:
        dispositivo_id (int): ID del dispositivo a editar
        
    GET: Mostrar formulario de edición
    POST: Guardar cambios en base de datos
    """
    
    dispositivo = Device.query.get_or_404(dispositivo_id)
    
    # Verificar permisos (solo admin o propietario)
    if not es_admin() and dispositivo.usuario_id != current_user.id:
        flash('No tienes permiso para editar este dispositivo', 'danger')
        return redirect(url_for('devices.listado'))
    
    form = EditarDispositivoForm()
    
    if form.validate_on_submit():
        try:
            dispositivo.nombre = form.nombre.data
            dispositivo.ubicacion = form.ubicacion.data
            dispositivo.estado = form.estado.data
            dispositivo.firmware = form.firmware.data
            
            db.session.commit()
            
            flash('Dispositivo actualizado correctamente', 'success')
            return redirect(url_for('devices.ver', dispositivo_id=dispositivo.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar: {str(e)}', 'danger')
    
    elif request.method == 'GET':
        form.nombre.data = dispositivo.nombre
        form.ubicacion.data = dispositivo.ubicacion
        form.estado.data = dispositivo.estado
        form.firmware.data = dispositivo.firmware
    
    return render_template('devices/editar.html', form=form, dispositivo=dispositivo)


@devices_bp.route('/<int:dispositivo_id>/eliminar', methods=['POST'])
@login_required
def eliminar(dispositivo_id):
    """
    Eliminar un dispositivo.
    
    Args:
        dispositivo_id (int): ID del dispositivo a eliminar
        
    POST: Confirmar eliminación y eliminar de BD
    """
    
    dispositivo = Device.query.get_or_404(dispositivo_id)
    
    # Verificar permisos (solo admin)
    if not es_admin():
        flash('No tienes permiso para eliminar dispositivos', 'danger')
        return redirect(url_for('devices.listado'))
    
    try:
        nombre = dispositivo.nombre
        db.session.delete(dispositivo)
        db.session.commit()
        
        flash(f'Dispositivo "{nombre}" eliminado', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar: {str(e)}', 'danger')
    
    return redirect(url_for('devices.listado'))


@devices_bp.route('/asignar/<int:dispositivo_id>/usuario/<int:usuario_id>', methods=['POST'])
@login_required
def asignar_usuario(dispositivo_id, usuario_id):
    """
    Asignar un dispositivo a un usuario.
    
    Solo administradores pueden hacer esto.
    
    Args:
        dispositivo_id (int): ID del dispositivo
        usuario_id (int): ID del usuario a asignar
        
    POST: Realizar la asignación
    """
    
    if not es_admin():
        return jsonify({'error': 'No tienes permiso'}), 403
    
    dispositivo = Device.query.get_or_404(dispositivo_id)
    usuario = User.query.get_or_404(usuario_id)
    
    try:
        dispositivo.usuario_id = usuario_id
        db.session.commit()
        
        return jsonify({
            'success': True,
            'mensaje': f'Dispositivo asignado a {usuario.nombre}'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
