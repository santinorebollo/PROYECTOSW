# ===============================================
# app/forms/auth_forms.py
# ===============================================
# Formularios de Autenticación
#
# Contiene todos los formularios relacionados con
# autenticación:
# - Login
# - Registro
# - Recuperación de contraseña
# - Cambio de contraseña
#
# Todos incluyen validación del lado del servidor
# ===============================================

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, ValidationError, Regexp
)
from app.models import User


class LoginForm(FlaskForm):
    """
    Formulario de Login.
    
    Permite a los usuarios iniciar sesión con su email y contraseña.
    """
    
    # Campo de email
    email = StringField(
        'Correo Electrónico',
        validators=[
            DataRequired(message='El email es requerido'),
            Email(message='Email inválido')
        ],
        render_kw={"class": "form-control", "placeholder": "tu@email.com"}
    )
    
    # Campo de contraseña
    password = PasswordField(
        'Contraseña',
        validators=[
            DataRequired(message='La contraseña es requerida')
        ],
        render_kw={"class": "form-control", "placeholder": "Tu contraseña"}
    )
    
    # Recordar sesión
    recuerdarme = BooleanField(
        'Recuérdame',
        render_kw={"class": "form-check-input"}
    )
    
    # Botón de envío
    enviar = SubmitField(
        'Iniciar Sesión',
        render_kw={"class": "btn btn-primary w-100"}
    )
    
    def validate_email(self, field):
        """
        Validación personalizada: Verificar que el usuario existe.
        
        Args:
            field: Campo de email a validar
            
        Raises:
            ValidationError: Si el usuario no existe
        """
        usuario = User.query.filter_by(email=field.data).first()
        if not usuario:
            raise ValidationError('Email o contraseña incorrectos')
        if not usuario.activo:
            raise ValidationError('Cuenta desactivada. Contacta al administrador.')


class RegistroForm(FlaskForm):
    """
    Formulario de Registro de nuevos usuarios.
    
    Permite crear una nueva cuenta en el sistema.
    """
    
    # Campo de nombre
    nombre = StringField(
        'Nombre Completo',
        validators=[
            DataRequired(message='El nombre es requerido'),
            Length(min=3, max=128, message='El nombre debe tener entre 3 y 128 caracteres')
        ],
        render_kw={"class": "form-control", "placeholder": "Tu nombre completo"}
    )
    
    # Campo de email
    email = StringField(
        'Correo Electrónico',
        validators=[
            DataRequired(message='El email es requerido'),
            Email(message='Email inválido')
        ],
        render_kw={"class": "form-control", "placeholder": "tu@email.com"}
    )
    
    # Campo de contraseña
    password = PasswordField(
        'Contraseña',
        validators=[
            DataRequired(message='La contraseña es requerida'),
            Length(min=8, message='La contraseña debe tener al menos 8 caracteres'),
            Regexp(
                r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)',
                message='La contraseña debe contener mayúsculas, minúsculas y números'
            )
        ],
        render_kw={"class": "form-control", "placeholder": "Contraseña segura"}
    )
    
    # Confirmación de contraseña
    password_confirm = PasswordField(
        'Confirmar Contraseña',
        validators=[
            DataRequired(message='Debes confirmar la contraseña'),
            EqualTo('password', message='Las contraseñas no coinciden')
        ],
        render_kw={"class": "form-control", "placeholder": "Repite tu contraseña"}
    )
    
    # Aceptar términos
    aceptar_terminos = BooleanField(
        'Acepto los términos y condiciones',
        validators=[
            DataRequired(message='Debes aceptar los términos y condiciones')
        ],
        render_kw={"class": "form-check-input"}
    )
    
    # Botón de envío
    enviar = SubmitField(
        'Crear Cuenta',
        render_kw={"class": "btn btn-primary w-100"}
    )
    
    def validate_email(self, field):
        """
        Validación personalizada: Email no debe existir.
        
        Args:
            field: Campo de email a validar
            
        Raises:
            ValidationError: Si el email ya está registrado
        """
        usuario = User.query.filter_by(email=field.data).first()
        if usuario:
            raise ValidationError('Este email ya está registrado. ¿Quizás quieras iniciar sesión?')


class CambioContraseñaForm(FlaskForm):
    """
    Formulario para cambiar la contraseña del usuario autenticado.
    """
    
    # Contraseña actual
    password_actual = PasswordField(
        'Contraseña Actual',
        validators=[
            DataRequired(message='Debes introducir tu contraseña actual')
        ],
        render_kw={"class": "form-control", "placeholder": "Tu contraseña actual"}
    )
    
    # Nueva contraseña
    password_nueva = PasswordField(
        'Nueva Contraseña',
        validators=[
            DataRequired(message='La nueva contraseña es requerida'),
            Length(min=8, message='La contraseña debe tener al menos 8 caracteres'),
            Regexp(
                r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)',
                message='La contraseña debe contener mayúsculas, minúsculas y números'
            )
        ],
        render_kw={"class": "form-control", "placeholder": "Nueva contraseña"}
    )
    
    # Confirmación de nueva contraseña
    password_nueva_confirm = PasswordField(
        'Confirmar Nueva Contraseña',
        validators=[
            DataRequired(message='Debes confirmar la nueva contraseña'),
            EqualTo('password_nueva', message='Las contraseñas no coinciden')
        ],
        render_kw={"class": "form-control", "placeholder": "Repite la nueva contraseña"}
    )
    
    # Botón de envío
    enviar = SubmitField(
        'Cambiar Contraseña',
        render_kw={"class": "btn btn-primary w-100"}
    )


class RecuperacionContraseñaForm(FlaskForm):
    """
    Formulario para solicitar recuperación de contraseña.
    """
    
    # Campo de email
    email = StringField(
        'Correo Electrónico',
        validators=[
            DataRequired(message='El email es requerido'),
            Email(message='Email inválido')
        ],
        render_kw={"class": "form-control", "placeholder": "tu@email.com"}
    )
    
    # Botón de envío
    enviar = SubmitField(
        'Enviar Instrucciones de Recuperación',
        render_kw={"class": "btn btn-primary w-100"}
    )
    
    def validate_email(self, field):
        """
        Validación personalizada: Email debe existir.
        
        Args:
            field: Campo de email a validar
            
        Raises:
            ValidationError: Si el email no existe
        """
        usuario = User.query.filter_by(email=field.data).first()
        if not usuario:
            raise ValidationError('No existe cuenta con este email')
