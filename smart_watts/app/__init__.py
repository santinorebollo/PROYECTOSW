# ===============================================
# app/__init__.py
# ===============================================
# Inicializador del paquete principal 'app'
# 
# Este archivo es responsable de:
# 1. Crear la instancia de Flask
# 2. Inicializar todas las extensiones (DB, Login, etc.)
# 3. Registrar blueprints de rutas
# 4. Configurar manejadores de errores
# 5. Registrar filtros y contextos
#
# Sigue el patrón de "application factory" para
# permitir múltiples instancias de la app con
# diferentes configuraciones.
# ===============================================

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_wtf.csrf import CSRFProtect
import os

# ==================== INICIALIZACIÓN DE EXTENSIONES ====================
# Estas extensiones se crean aquí sin la app,
# y se inicializan después en create_app()

# Base de datos SQLAlchemy
db = SQLAlchemy()

# Sistema de autenticación y gestión de sesiones
login_manager = LoginManager()

# Sistema de migraciones de base de datos
migrate = Migrate()

# WebSockets para comunicación en tiempo real
socketio = SocketIO()

# Protección contra ataques CSRF
csrf = CSRFProtect()


def create_app(config_name='development'):
    """
    Factory function que crea y configura la aplicación Flask.
    
    Args:
        config_name (str): Nombre de la configuración a usar
                          ('development', 'testing', 'production')
    
    Returns:
        Flask: Instancia de la aplicación configurada
    
    Este patrón permite:
    - Crear múltiples instancias de app con diferentes configs
    - Facilitar testing
    - Mejor organización del código
    """
    
    # ==================== CREAR APLICACIÓN ====================
    app = Flask(__name__)
    
    # ==================== CARGAR CONFIGURACIÓN ====================
    # Cargar configuración desde config.py según el entorno
    from config import config as config_dict
    
    # Si no se especifica configuración, usar desarrollo
    app.config.from_object(config_dict.get(config_name, config_dict['development']))
    
    # ==================== CREAR DIRECTORIO DE BASE DE DATOS ====================
    # Asegurar que el directorio 'database' existe
    db_dir = os.path.join(os.path.dirname(__file__), '..', 'database')
    os.makedirs(db_dir, exist_ok=True)
    
    # ==================== INICIALIZAR EXTENSIONES ====================
    # Inicializar cada extensión con la app creada
    
    db.init_app(app)  # Base de datos
    login_manager.init_app(app)  # Autenticación
    migrate.init_app(app, db)  # Migraciones de BD
    socketio.init_app(app, cors_allowed_origins="*")  # WebSockets
    csrf.init_app(app)  # Protección CSRF
    
    # ==================== CONFIGURAR LOGIN ====================
    # URL a la que redirigir si usuario no está autenticado
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        """Cargar un usuario a partir del ID almacenado en la sesión"""
        from app.models.user import User
        return User.query.get(int(user_id))

    # ==================== REGISTRAR BLUEPRINTS ====================
    # Los blueprints son módulos de rutas que se registran aquí
    
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.devices import devices_bp
    from app.routes.users import users_bp
    from app.routes.notifications import notifications_bp
    from app.routes.api import api_bp
    from app.routes.reports import reports_bp, settings_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(devices_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)
    
    # ==================== CREAR TABLAS DE BD ====================
    # Crear todas las tablas si no existen
    with app.app_context():
        db.create_all()
    
    # ==================== MANEJADORES DE ERRORES ====================
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Manejar error 404 - Página no encontrada"""
        return {'error': 'Página no encontrada'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Manejar error 500 - Error interno del servidor"""
        db.session.rollback()
        return {'error': 'Error interno del servidor'}, 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """Manejar error 403 - Acceso prohibido"""
        return {'error': 'Acceso prohibido'}, 403
    
    # ==================== CONTEXTOS Y FILTROS ====================
    
    @app.context_processor
    def inject_config():
        """
        Inyectar variables de configuración en contexto global
        Disponibles en todos los templates
        """
        return {
            'APP_NAME': app.config['APP_NAME'],
            'APP_VERSION': app.config['APP_VERSION'],
            'PROJECT_NAME': app.config['PROJECT_NAME']
        }
    
    # ==================== COMANDOS CLI PERSONALIZADOS ====================
    
    @app.cli.command()
    def init_db():
        """Inicializar la base de datos"""
        db.create_all()
        print('Base de datos inicializada.')
    
    @app.cli.command()
    def seed_db():
        """Llenar la base de datos con datos de prueba"""
        from app.models.user import User
        from app.models.energy_rate import EnergyRate
        
        # Crear usuario administrador de prueba
        if not User.query.filter_by(email='admin@smartwatts.com').first():
            admin = User(
                nombre='Administrador',
                email='admin@smartwatts.com',
                rol='admin',
                activo=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Crear usuario normal de prueba
            user = User(
                nombre='Usuario Demo',
                email='usuario@smartwatts.com',
                rol='usuario',
                activo=True
            )
            user.set_password('usuario123')
            db.session.add(user)
            
            # Crear tarifa de energía por defecto
            rate = EnergyRate(
                precio_kwh=50.0,  # 50 ARS por kWh
                impuestos=10.5,   # 10.5%
                cargos_fijos=200  # 200 ARS fijos mensuales
            )
            db.session.add(rate)
            
            db.session.commit()
            print('Base de datos poblada con datos de prueba.')
            print('Admin: admin@smartwatts.com / admin123')
            print('Usuario: usuario@smartwatts.com / usuario123')
        else:
            print('La base de datos ya contiene datos.')
    
    return app
