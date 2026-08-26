# ===============================================
# config.py
# ===============================================
# Archivo de configuración principal de Smart Watts
# Define las configuraciones para diferentes entornos
# (desarrollo, prueba, producción)
#
# Este archivo centraliza todas las variables de
# configuración de la aplicación incluyendo:
# - Base de datos
# - Claves de seguridad
# - Parámetros de aplicación
# ===============================================

import os
from datetime import timedelta

# Obtener la ruta base del proyecto
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    Clase base de configuración con valores compartidos
    por todos los entornos.
    """

    # ==================== FLASK ====================
    # Clave secreta para sesiones y CSRF protection
    # En producción, debe ser una cadena larga y aleatoria
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # ==================== BASE DE DATOS ====================
    # Configuración de SQLite (por defecto)
    # Se puede cambiar a MySQL o PostgreSQL en producción
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'database', 'smart_watts.db')
    
    # Desactivar advertencias de seguimiento de modificaciones
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ==================== SESIONES ====================
    # Tiempo de expiración de sesión (30 minutos)
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    # Cookie segura (solo para HTTPS)
    SESSION_COOKIE_SECURE = False  # Cambiar a True en producción
    
    # Cookie solo HTTP (previene acceso desde JavaScript)
    SESSION_COOKIE_HTTPONLY = True
    
    # Política SAMESITE para CSRF
    SESSION_COOKIE_SAMESITE = 'Lax'

    # ==================== SEGURIDAD ====================
    # Protección CSRF habilitada
    WTF_CSRF_ENABLED = True
    
    # Tiempo de expiración de token CSRF
    WTF_CSRF_TIME_LIMIT = None

    # ==================== LOGGING ====================
    # Nivel de logging
    LOG_LEVEL = 'INFO'

    # ==================== APLICACIÓN ====================
    # Nombre de la aplicación (comercial)
    APP_NAME = 'Smart Watts'
    
    # Nombre interno del proyecto
    PROJECT_NAME = 'smart_watts'
    
    # Versión de la aplicación
    APP_VERSION = '1.0.0'

    # ==================== PARÁMETROS DE NEGOCIO ====================
    # Valores por defecto para nuevos usuarios
    DEFAULT_CURRENCY = 'ARS'  # Peso Argentino
    DEFAULT_POWER_UNIT = 'kWh'
    DEFAULT_VOLTAGE = 220  # Voltios
    
    # Límites de alertas
    DEFAULT_CONSUMPTION_LIMIT = 500  # kWh por período
    DEFAULT_BUDGET = 5000  # ARS por mes

    # ==================== SOCKET.IO ====================
    # Configuración para comunicación en tiempo real
    SOCKETIO_MESSAGE_QUEUE = os.environ.get('SOCKETIO_MESSAGE_QUEUE') or None
    SOCKETIO_CORS_ALLOWED_ORIGINS = "*"

    # ==================== PAGINACIÓN ====================
    # Elementos por página en listados
    ITEMS_PER_PAGE = 10
    
    # ==================== THRESHOLDS DE ALERTAS ====================
    # Porcentaje del presupuesto para alertas
    ALERT_BUDGET_THRESHOLD_1 = 70  # Primera alerta
    ALERT_BUDGET_THRESHOLD_2 = 85  # Segunda alerta
    ALERT_BUDGET_THRESHOLD_3 = 100  # Tercera alerta


class DevelopmentConfig(Config):
    """
    Configuración para entorno de desarrollo.
    Habilita debugging y características útiles para desarrollo.
    """
    DEBUG = True
    TESTING = False
    
    # En desarrollo, mostrar queries SQL
    SQLALCHEMY_ECHO = True
    
    # Cookies sin requerir HTTPS
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    """
    Configuración para pruebas automatizadas.
    Usa base de datos en memoria para rapidez.
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """
    Configuración para producción.
    Máxima seguridad y optimizaciones.
    """
    DEBUG = False
    TESTING = False
    
    # En producción, HTTPS obligatorio
    SESSION_COOKIE_SECURE = True
    
    # Base de datos: usar variable de entorno o SQLite como fallback
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(__file__), 'database', 'smart_watts.db')
    
    # Clave secreta: usar variable de entorno o la del Config base
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'


# ==================== SELECTOR DE CONFIGURACIÓN ====================
# Seleccionar la configuración según el entorno
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
