# ===============================================
# app/routes/auth.py
# ===============================================
# Rutas de Autenticación
#
# Gestiona el ciclo de vida de sesión del usuario:
# - Login
# - Logout
# - Registro
# - Recuperación de contraseña
# - Cambio de contraseña
# ===============================================

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Budget
from app.forms import (
    LoginForm, RegistroForm, CambioContraseñaForm,
    RecuperacionContraseñaForm
)

# Crear blueprint de autenticación
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Ruta de login.
    
    GET: Mostrar formulario de login
    POST: Procesar intento de login
    
    Valida credenciales y crea sesión de usuario.
    """
    
    # Si el usuario ya está autenticado, redirigir al dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    # Crear formulario
    form = LoginForm()
    
    # Procesar formulario enviado
    if form.validate_on_submit():
        # Buscar usuario por email
        usuario = User.query.filter_by(email=form.email.data).first()
        
        # Verificar contraseña
        if usuario and usuario.check_password(form.password.data):
            # Crear sesión de usuario
            login_user(usuario, remember=form.recuerdarme.data)
            
            # Registrar login
            usuario.registrar_login()
            
            # Flash message
            flash(f'¡Bienvenido {usuario.nombre}!', 'success')
            
            # Redirigir a próxima página o dashboard
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('dashboard.index'))
        else:
            # Credenciales incorrectas
            flash('Email o contraseña incorrectos', 'danger')
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """
    Ruta de logout.
    
    Destruye la sesión del usuario autenticado.
    """
    nombre = current_user.nombre
    logout_user()
    flash(f'¡Hasta pronto, {nombre}!', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    """
    Ruta de registro de nuevos usuarios.
    
    GET: Mostrar formulario de registro
    POST: Crear nuevo usuario en la base de datos
    
    Valida datos y crea cuenta de usuario normal.
    """
    
    # Si ya está autenticado, redirigir
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = RegistroForm()
    
    if form.validate_on_submit():
        try:
            # Crear nuevo usuario
            usuario = User(
                nombre=form.nombre.data,
                email=form.email.data,
                rol='usuario',  # Usuarios nuevos son siempre 'usuario' normal
                activo=True
            )
            
            # Establecer contraseña (genera hash)
            usuario.set_password(form.password.data)
            
            # Agregar a la base de datos
            db.session.add(usuario)
            db.session.flush()  # Obtener el ID asignado
            
            # Crear presupuesto inicial para el usuario
            presupuesto = Budget.obtener_o_crear_para_usuario(
                usuario.id,
                presupuesto_inicial=5000  # ARS por defecto
            )
            
            # Confirmar cambios
            db.session.commit()
            
            flash('¡Cuenta creada exitosamente! Por favor inicia sesión', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la cuenta: {str(e)}', 'danger')
    
    return render_template('auth/registro.html', form=form)


@auth_bp.route('/cambiar-contraseña', methods=['GET', 'POST'])
@login_required
def cambiar_contraseña():
    """
    Ruta para cambiar contraseña (usuario autenticado).
    
    GET: Mostrar formulario de cambio de contraseña
    POST: Procesar cambio de contraseña
    
    Requiere autenticación y verifica contraseña actual.
    """
    
    form = CambioContraseñaForm()
    
    if form.validate_on_submit():
        # Verificar que la contraseña actual sea correcta
        if not current_user.check_password(form.password_actual.data):
            flash('La contraseña actual es incorrecta', 'danger')
            return redirect(url_for('auth.cambiar_contraseña'))
        
        # Cambiar a nueva contraseña
        current_user.set_password(form.password_nueva.data)
        db.session.commit()
        
        flash('Contraseña actualizada correctamente', 'success')
        return redirect(url_for('dashboard.index'))
    
    return render_template('auth/cambiar_contraseña.html', form=form)


@auth_bp.route('/recuperar-contraseña', methods=['GET', 'POST'])
def recuperar_contraseña():
    """
    Ruta para solicitar recuperación de contraseña.
    
    GET: Mostrar formulario
    POST: Enviar instrucciones de recuperación
    
    Nota: En producción, enviaría email con token de reset.
    """
    
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = RecuperacionContraseñaForm()
    
    if form.validate_on_submit():
        usuario = User.query.filter_by(email=form.email.data).first()
        
        if usuario:
            # En producción, aquí se enviaría un email
            # con un token de recuperación seguro
            
            flash(
                'Se han enviado instrucciones de recuperación a tu email. '
                '(En modo desarrollo, contacta al administrador)',
                'info'
            )
        else:
            # No revelar si el email existe o no (seguridad)
            flash(
                'Si el email está registrado, recibirás instrucciones de recuperación',
                'info'
            )
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/recuperar_contraseña.html', form=form)


@auth_bp.before_request
def check_user_active():
    """
    Verificar que usuarios autenticados sigan activos.
    
    Si un usuario fue desactivado mientras tenía sesión activa,
    será desconectado.
    """
    
    if current_user.is_authenticated:
        # Recargar usuario de la BD para obtener estado actual
        usuario = User.query.get(current_user.id)
        
        if usuario and not usuario.activo:
            logout_user()
            flash('Tu cuenta ha sido desactivada', 'warning')
            return redirect(url_for('auth.login'))
