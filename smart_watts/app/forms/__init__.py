# ===============================================
# app/forms/__init__.py
# ===============================================
# Inicializador del paquete de formularios
# ===============================================

from app.forms.auth_forms import (
    LoginForm,
    RegistroForm,
    CambioContraseñaForm,
    RecuperacionContraseñaForm
)

from app.forms.device_forms import (
    CrearDispositivoForm,
    EditarDispositivoForm,
    CrearUsuarioForm,
    EditarUsuarioForm,
    ConfigurarPresupuestoForm,
    ConfiguracionTarifasForm,
    EditarPerfilForm
)

__all__ = [
    'LoginForm',
    'RegistroForm',
    'CambioContraseñaForm',
    'RecuperacionContraseñaForm',
    'CrearDispositivoForm',
    'EditarDispositivoForm',
    'CrearUsuarioForm',
    'EditarUsuarioForm',
    'ConfigurarPresupuestoForm',
    'ConfiguracionTarifasForm',
    'EditarPerfilForm'
]
