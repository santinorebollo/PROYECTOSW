# ===============================================
# app/models/user.py
# ===============================================
# Modelo de Usuario
#
# Este modelo representa a un usuario del sistema.
# Gestiona:
# - Datos personales del usuario
# - Credenciales de autenticación
# - Roles y permisos
# - Relaciones con dispositivos y notificaciones
#
# El modelo hereda de UserMixin de Flask-Login para
# integración transparente del sistema de autenticación.
# ===============================================

from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Importar modelos relacionados para relaciones
# (se importan dentro de métodos para evitar importaciones circulares)


class User(UserMixin, db.Model):
    """
    Modelo de Usuario.
    
    Atributos:
        id (int): Identificador único del usuario
        nombre (str): Nombre completo del usuario
        email (str): Email único (utilizado para login)
        password_hash (str): Hash seguro de la contraseña
        rol (str): Rol del usuario ('admin' o 'usuario')
        activo (bool): Indica si el usuario puede acceder al sistema
        fecha_creacion (datetime): Fecha de creación de la cuenta
        ultima_login (datetime): Fecha del último login
        
    Relaciones:
        dispositivos: Dispositivos propiedad de este usuario
        notificaciones: Notificaciones del usuario
        presupuesto: Presupuesto energético del usuario
    """
    
    # ==================== NOMBRE DE LA TABLA ====================
    __tablename__ = 'user'
    
    # ==================== COLUMNAS ====================
    
    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)
    
    # Información del usuario
    nombre = db.Column(db.String(128), nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    
    # Autenticación (almacenar solo el hash, nunca la contraseña en texto plano)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Control de acceso
    rol = db.Column(db.String(20), default='usuario', nullable=False)
    # Roles disponibles: 'admin' (administrador), 'usuario' (usuario normal)
    
    activo = db.Column(db.Boolean, default=True, nullable=False)
    # Si es False, el usuario no puede acceder al sistema
    
    # Auditoría
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ultima_login = db.Column(db.DateTime)
    
    # ==================== RELACIONES ====================
    # Relación uno-a-muchos: Un usuario tiene muchos dispositivos
    dispositivos = db.relationship('Device', backref='usuario', lazy='dynamic', 
                                   cascade='all, delete-orphan')
    
    # Relación uno-a-muchos: Un usuario tiene muchas notificaciones
    notificaciones = db.relationship('Notification', backref='usuario', lazy='dynamic',
                                     cascade='all, delete-orphan')
    
    # Relación uno-a-uno: Un usuario tiene un presupuesto
    presupuesto = db.relationship('Budget', backref='usuario', uselist=False,
                                  cascade='all, delete-orphan')
    
    # ==================== MÉTODOS DE SEGURIDAD ====================
    
    def set_password(self, password):
        """
        Establecer la contraseña del usuario.
        
        Genera un hash seguro de la contraseña usando werkzeug.
        NUNCA se almacena la contraseña en texto plano en la BD.
        
        Args:
            password (str): Contraseña en texto plano
        """
        # generate_password_hash usa algoritmo PBKDF2 por defecto
        # que es seguro contra ataques de fuerza bruta
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """
        Verificar si la contraseña proporcionada es correcta.
        
        Compara el hash almacenado con el hash de la contraseña proporcionada.
        
        Args:
            password (str): Contraseña en texto plano a verificar
            
        Returns:
            bool: True si la contraseña es correcta, False en caso contrario
        """
        return check_password_hash(self.password_hash, password)
    
    # ==================== MÉTODOS DE AUTORIZACIÓN ====================
    
    def es_admin(self):
        """
        Verificar si el usuario es administrador.
        
        Returns:
            bool: True si el usuario tiene rol 'admin'
        """
        return self.rol == 'admin'
    
    def tiene_permiso(self, permiso):
        """
        Verificar si el usuario tiene un permiso específico.
        
        Implementa un sistema básico de permisos basado en roles.
        
        Args:
            permiso (str): Nombre del permiso a verificar
            
        Returns:
            bool: True si el usuario tiene el permiso
        """
        # Los administradores tienen todos los permisos
        if self.es_admin():
            return True
        
        # Permisos específicos por rol
        permisos_usuario = {
            'ver_dispositivos',
            'ver_consumo',
            'ver_graficos',
            'ver_historial',
            'editar_perfil',
            'cambiar_contraseña'
        }
        
        return permiso in permisos_usuario
    
    # ==================== MÉTODOS DE AUDITORÍA ====================
    
    def registrar_login(self):
        """
        Registrar el tiempo del último login del usuario.
        Llamar después de autenticar al usuario.
        """
        self.ultima_login = datetime.utcnow()
        db.session.commit()
    
    # ==================== MÉTODOS DE REPRESENTACIÓN ====================
    
    def __repr__(self):
        """Representación en texto del usuario para debugging"""
        return f'<User {self.email}>'
    
    def to_dict(self):
        """
        Convertir el usuario a diccionario para JSON API.
        
        Returns:
            dict: Datos del usuario en formato diccionario
        """
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'rol': self.rol,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat(),
            'ultima_login': self.ultima_login.isoformat() if self.ultima_login else None
        }
