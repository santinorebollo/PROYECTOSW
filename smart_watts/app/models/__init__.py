# ===============================================
# app/models/__init__.py
# ===============================================
# Inicializador del paquete de modelos
#
# Este archivo importa todos los modelos para que
# sean fácilmente accesibles desde otros módulos.
# ===============================================

from app.models.user import User
from app.models.device import Device
from app.models.reading import Reading
from app.models.notification import Notification
from app.models.energy_rate import EnergyRate, Budget

__all__ = [
    'User',
    'Device',
    'Reading',
    'Notification',
    'EnergyRate',
    'Budget'
]
