# ===============================================
# app/routes/__init__.py
# ===============================================
# Inicializador del paquete de rutas
#
# Este archivo importa todos los blueprints
# Los blueprints se registran en app/__init__.py
# ===============================================

from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.devices import devices_bp
from app.routes.users import users_bp
from app.routes.notifications import notifications_bp
from app.routes.api import api_bp
from app.routes.reports import reports_bp, settings_bp

__all__ = [
    'auth_bp',
    'dashboard_bp',
    'devices_bp',
    'users_bp',
    'notifications_bp',
    'api_bp',
    'reports_bp',
    'settings_bp'
]
