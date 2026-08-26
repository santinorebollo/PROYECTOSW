# ===============================================
# app/forms/device_forms.py
# ===============================================
# Formularios de Dispositivos
#
# Contiene formularios para:
# - Crear dispositivos
# - Editar dispositivos
# - Eliminar dispositivos
# ===============================================

from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from app.models import User


class CrearDispositivoForm(FlaskForm):
    """
    Formulario para crear un nuevo dispositivo IoT.
    """
    
    # Nombre del dispositivo
    nombre = StringField(
        'Nombre del Dispositivo',
        validators=[
            DataRequired(message='El nombre es requerido'),
            Length(min=3, max=128, message='El nombre debe tener entre 3 y 128 caracteres')
        ],
        render_kw={"class": "form-control", "placeholder": "Ej: Medidor Cocina"}
    )
    
    # Ubicación del dispositivo
    ubicacion = StringField(
        'Ubicación',
        validators=[
            Optional(),
            Length(max=128, message='La ubicación no puede exceder 128 caracteres')
        ],
        render_kw={"class": "form-control", "placeholder": "Ej: Cocina principal"}
    )
    
    # Firmware
    firmware = StringField(
        'Versión de Firmware',
        default='1.0.0',
        validators=[
            Length(max=50, message='El firmware no puede exceder 50 caracteres')
        ],
        render_kw={"class": "form-control", "placeholder": "Ej: 1.0.0"}
    )
    
    # Botón de envío
    enviar = SubmitField(
        'Crear Dispositivo',
        render_kw={"class": "btn btn-success"}
    )


class EditarDispositivoForm(FlaskForm):
    """
    Formulario para editar un dispositivo existente.
    """
    
    # Nombre del dispositivo
    nombre = StringField(
        'Nombre del Dispositivo',
        validators=[
            DataRequired(message='El nombre es requerido'),
            Length(min=3, max=128, message='El nombre debe tener entre 3 y 128 caracteres')
        ],
        render_kw={"class": "form-control"}
    )
    
    # Ubicación del dispositivo
    ubicacion = StringField(
        'Ubicación',
        validators=[
            Optional(),
            Length(max=128, message='La ubicación no puede exceder 128 caracteres')
        ],
        render_kw={"class": "form-control"}
    )
    
    # Estado del dispositivo
    estado = SelectField(
        'Estado',
        choices=[
            ('activo', 'Activo'),
            ('inactivo', 'Inactivo'),
            ('desconectado', 'Desconectado')
        ],
        render_kw={"class": "form-control"}
    )
    
    # Firmware
    firmware = StringField(
        'Versión de Firmware',
        validators=[
            Length(max=50, message='El firmware no puede exceder 50 caracteres')
        ],
        render_kw={"class": "form-control"}
    )
    
    # Botón de envío
    enviar = SubmitField(
        'Actualizar Dispositivo',
        render_kw={"class": "btn btn-primary"}
    )


# ===============================================
# app/forms/user_forms.py
# ===============================================
# Formularios de Gestión de Usuarios
#
# Formularios de administrador para gestionar usuarios
# ===============================================

class CrearUsuarioForm(FlaskForm):
    """
    Formulario para que el administrador cree nuevos usuarios.
    """
    
    # Nombre del usuario
    nombre = StringField(
        'Nombre Completo',
        validators=[
            DataRequired(message='El nombre es requerido'),
            Length(min=3, max=128, message='El nombre debe tener entre 3 y 128 caracteres')
        ],
        render_kw={"class": "form-control", "placeholder": "Nombre del usuario"}
    )
    
    # Email del usuario
    email = StringField(
        'Correo Electrónico',
        validators=[
            DataRequired(message='El email es requerido')
        ],
        render_kw={"class": "form-control", "placeholder": "correo@ejemplo.com"}
    )
    
    # Rol del usuario
    rol = SelectField(
        'Rol',
        choices=[
            ('usuario', 'Usuario Regular'),
            ('admin', 'Administrador')
        ],
        render_kw={"class": "form-control"}
    )
    
    # Contraseña temporal
    password = StringField(
        'Contraseña Temporal',
        validators=[
            DataRequired(message='Debes establecer una contraseña'),
            Length(min=8, message='La contraseña debe tener al menos 8 caracteres')
        ],
        render_kw={"class": "form-control", "placeholder": "Contraseña temporal"}
    )
    
    # Botón de envío
    enviar = SubmitField(
        'Crear Usuario',
        render_kw={"class": "btn btn-success"}
    )


class EditarUsuarioForm(FlaskForm):
    """
    Formulario para editar datos de un usuario.
    """
    
    # Nombre del usuario
    nombre = StringField(
        'Nombre Completo',
        validators=[
            DataRequired(message='El nombre es requerido'),
            Length(min=3, max=128, message='El nombre debe tener entre 3 y 128 caracteres')
        ],
        render_kw={"class": "form-control"}
    )
    
    # Rol del usuario
    rol = SelectField(
        'Rol',
        choices=[
            ('usuario', 'Usuario Regular'),
            ('admin', 'Administrador')
        ],
        render_kw={"class": "form-control"}
    )
    
    # Estado
    activo = SelectField(
        'Estado',
        choices=[
            ('True', 'Activo'),
            ('False', 'Inactivo')
        ],
        render_kw={"class": "form-control"}
    )
    
    # Botón de envío
    enviar = SubmitField(
        'Actualizar Usuario',
        render_kw={"class": "btn btn-primary"}
    )


# ===============================================
# app/forms/budget_forms.py
# ===============================================
# Formularios de Presupuesto
# ===============================================

class ConfigurarPresupuestoForm(FlaskForm):
    """
    Formulario para configurar el presupuesto mensual.
    """
    
    # Presupuesto mensual
    presupuesto_mensual = StringField(
        'Presupuesto Mensual (ARS)',
        validators=[
            DataRequired(message='El presupuesto es requerido')
        ],
        render_kw={
            "class": "form-control",
            "placeholder": "Ej: 5000",
            "type": "number",
            "step": "100",
            "min": "0"
        }
    )
    
    # Botón de envío
    enviar = SubmitField(
        'Guardar Presupuesto',
        render_kw={"class": "btn btn-primary"}
    )
    
    def validate_presupuesto_mensual(self, field):
        """
        Validación personalizada: Presupuesto debe ser positivo.
        """
        try:
            valor = float(field.data)
            if valor < 0:
                raise ValueError()
        except (ValueError, TypeError):
            raise ValidationError('El presupuesto debe ser un número positivo')


# ===============================================
# app/forms/settings_forms.py
# ===============================================
# Formularios de Configuración
# ===============================================

class ConfiguracionTarifasForm(FlaskForm):
    """
    Formulario para configurar las tarifas energéticas.
    Solo accesible por administradores.
    """
    
    # Precio por kWh
    precio_kwh = StringField(
        'Precio por kWh (ARS)',
        validators=[
            DataRequired(message='El precio es requerido')
        ],
        render_kw={
            "class": "form-control",
            "placeholder": "Ej: 50.00",
            "type": "number",
            "step": "0.01",
            "min": "0"
        }
    )
    
    # Impuestos
    impuestos = StringField(
        'Porcentaje de Impuestos (%)',
        validators=[
            DataRequired(message='El porcentaje de impuesto es requerido')
        ],
        render_kw={
            "class": "form-control",
            "placeholder": "Ej: 10.5",
            "type": "number",
            "step": "0.1",
            "min": "0"
        }
    )
    
    # Cargos fijos
    cargos_fijos = StringField(
        'Cargo Fijo Mensual (ARS)',
        validators=[
            DataRequired(message='El cargo fijo es requerido')
        ],
        render_kw={
            "class": "form-control",
            "placeholder": "Ej: 200.00",
            "type": "number",
            "step": "0.01",
            "min": "0"
        }
    )
    
    # Botón de envío
    enviar = SubmitField(
        'Guardar Configuración',
        render_kw={"class": "btn btn-success"}
    )


class EditarPerfilForm(FlaskForm):
    """
    Formulario para que los usuarios editen su perfil.
    """
    
    # Nombre del usuario
    nombre = StringField(
        'Nombre Completo',
        validators=[
            DataRequired(message='El nombre es requerido'),
            Length(min=3, max=128, message='El nombre debe tener entre 3 y 128 caracteres')
        ],
        render_kw={"class": "form-control"}
    )
    
    # Email del usuario
    email = StringField(
        'Correo Electrónico',
        validators=[
            DataRequired(message='El email es requerido')
        ],
        render_kw={"class": "form-control"}
    )
    
    # Botón de envío
    enviar = SubmitField(
        'Actualizar Perfil',
        render_kw={"class": "btn btn-primary"}
    )

    def validate_email(self, field):
        """
        Validación personalizada: el email no debe pertenecer a otro usuario.
        """
        usuario = User.query.filter_by(email=field.data).first()
        if usuario and usuario.id != current_user.id:
            raise ValidationError('Ese correo electrónico ya está en uso por otro usuario')
