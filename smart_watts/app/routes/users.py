# ===============================================
# app/routes/users.py
# ===============================================
# Rutas de Gestión de Usuarios
#
# Solo accesible por administradores.
# Permite crear, editar, eliminar y desactivar usuarios.
# ===============================================

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_
from app import db
from app.models import User, Budget
from app.forms import CrearUsuarioForm, EditarUsuarioForm

# Crear blueprint de usuarios
users_bp = Blueprint('users', __name__, url_prefix='/usuarios')


def requiere_admin(f):
    """Decorador para verificar que el usuario sea admin"""
    from functools import wraps
    
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.es_admin():
            flash('No tienes permisos de administrador', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    
    return wrapper


@users_bp.route('/')
@login_required
@requiere_admin
def listado():
    """
    Listar todos los usuarios del sistema.
    
    GET: Renderizar página con listado de usuarios
    """
    
    pagina = request.args.get('pagina', 1, type=int)
    buscar = request.args.get('buscar', '', type=str)
    
    query = User.query
    
    # Aplicar búsqueda
    if buscar:
        query = query.filter(
            or_(
                User.nombre.ilike(f'%{buscar}%'),
                User.email.ilike(f'%{buscar}%')
            )
        )
    
    # Paginar
    paginacion = query.paginate(page=pagina, per_page=10, error_out=False)
    
    usuarios = paginacion.items
    
    return render_template(
        'users/listado.html',
        usuarios=usuarios,
        paginacion=paginacion,
        buscar=buscar
    )


@users_bp.route('/crear', methods=['GET', 'POST'])
@login_required
@requiere_admin
def crear():
    """
    Crear un nuevo usuario.
    
    GET: Mostrar formulario
    POST: Crear usuario en BD
    """
    
    form = CrearUsuarioForm()
    
    if form.validate_on_submit():
        try:
            # Verificar que el email no exista
            if User.query.filter_by(email=form.email.data).first():
                flash('El email ya está registrado', 'danger')
                return render_template('users/crear.html', form=form)
            
            # Crear usuario
            usuario = User(
                nombre=form.nombre.data,
                email=form.email.data,
                rol=form.rol.data,
                activo=True
            )
            usuario.set_password(form.password.data)
            
            db.session.add(usuario)
            db.session.flush()
            
            # Crear presupuesto inicial
            Budget.obtener_o_crear_para_usuario(usuario.id)
            
            db.session.commit()
            
            flash(f'Usuario "{usuario.nombre}" creado exitosamente', 'success')
            return redirect(url_for('users.ver', usuario_id=usuario.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('users/crear.html', form=form)


@users_bp.route('/<int:usuario_id>')
@login_required
@requiere_admin
def ver(usuario_id):
    """
    Ver detalles de un usuario.
    """
    
    usuario = User.query.get_or_404(usuario_id)
    
    contexto = {
        'usuario': usuario,
        'dispositivos_count': usuario.dispositivos.count(),
        'presupuesto': usuario.presupuesto
    }
    
    return render_template('users/ver.html', **contexto)


@users_bp.route('/<int:usuario_id>/editar', methods=['GET', 'POST'])
@login_required
@requiere_admin
def editar(usuario_id):
    """
    Editar un usuario.
    """
    
    usuario = User.query.get_or_404(usuario_id)
    form = EditarUsuarioForm()
    
    if form.validate_on_submit():
        try:
            usuario.nombre = form.nombre.data
            usuario.rol = form.rol.data
            usuario.activo = form.activo.data == 'True'
            
            db.session.commit()
            flash('Usuario actualizado', 'success')
            return redirect(url_for('users.ver', usuario_id=usuario.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    elif request.method == 'GET':
        form.nombre.data = usuario.nombre
        form.rol.data = usuario.rol
        form.activo.data = 'True' if usuario.activo else 'False'
    
    return render_template('users/editar.html', form=form, usuario=usuario)


@users_bp.route('/<int:usuario_id>/eliminar', methods=['POST'])
@login_required
@requiere_admin
def eliminar(usuario_id):
    """
    Eliminar un usuario.
    """
    
    # No permitir eliminar a sí mismo
    if usuario_id == current_user.id:
        flash('No puedes eliminar tu propia cuenta', 'danger')
        return redirect(url_for('users.listado'))
    
    usuario = User.query.get_or_404(usuario_id)
    
    try:
        nombre = usuario.nombre
        db.session.delete(usuario)
        db.session.commit()
        flash(f'Usuario "{nombre}" eliminado', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('users.listado'))


@users_bp.route('/<int:usuario_id>/desactivar', methods=['POST'])
@login_required
@requiere_admin
def desactivar(usuario_id):
    """
    Desactivar un usuario (sin eliminar).
    """
    
    if usuario_id == current_user.id:
        flash('No puedes desactivar tu propia cuenta', 'danger')
        return redirect(url_for('users.ver', usuario_id=usuario_id))
    
    usuario = User.query.get_or_404(usuario_id)
    
    try:
        usuario.activo = False
        db.session.commit()
        flash(f'Usuario "{usuario.nombre}" desactivado', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('users.ver', usuario_id=usuario_id))


@users_bp.route('/<int:usuario_id>/activar', methods=['POST'])
@login_required
@requiere_admin
def activar(usuario_id):
    """
    Activar un usuario desactivado.
    """
    
    usuario = User.query.get_or_404(usuario_id)
    
    try:
        usuario.activo = True
        db.session.commit()
        flash(f'Usuario "{usuario.nombre}" activado', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('users.ver', usuario_id=usuario_id))
