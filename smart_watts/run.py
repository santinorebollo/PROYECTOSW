# ===============================================
# run.py
# ===============================================
# Script principal para ejecutar Smart Watts
#
# Ejecutar con: python run.py
#
# En desarrollo:
#     python run.py
#
# En producción:
#     gunicorn -w 4 -b 0.0.0.0:5000 'run:app'
# ===============================================

import os
import sys
from pathlib import Path
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app, db, socketio
from app.models import User, Device, Reading, Notification, EnergyRate, Budget


def create_app_instance():
    """
    Crear instancia de la aplicación Flask.
    
    Usa la configuración según la variable de entorno FLASK_ENV.
    """
    
    # Obtener entorno
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Crear aplicación
    app = create_app(config_name)
    
    return app


# Crear instancia de la aplicación
app = create_app_instance()

# Bandera para ejecutar inicialización solo una vez
_initialized = False


def initialize_app():
    """
    Inicializar la aplicación con datos por defecto.
    """
    global _initialized
    
    if _initialized:
        return
    
    _initialized = True
    
    with app.app_context():
        # Crear directorio de base de datos
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        if 'sqlite:///' in db_uri:
            db_path = db_uri.replace('sqlite:///', '')
            db_dir = Path(db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)
        
        # Crear tablas
        db.create_all()
        
        # Crear tarifa energética por defecto si no existe
        if not EnergyRate.query.first():
            tarifa = EnergyRate(
                precio_kwh=50.0,
                impuestos=10.5,
                cargos_fijos=200
            )
            db.session.add(tarifa)
            db.session.commit()
            print('✓ Tarifa energética creada')
        
        # Crear usuario admin por defecto si no existe
        admin = User.query.filter_by(email='admin@smartwatts.com').first()
        if not admin:
            admin = User(
                nombre='Administrador',
                email='admin@smartwatts.com',
                rol='admin',
                activo=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.flush()
            
            # Crear presupuesto para admin
            presupuesto = Budget(
                usuario_id=admin.id,
                presupuesto_mensual=10000,
                mes_año=datetime.utcnow().strftime('%Y-%m')
            )
            db.session.add(presupuesto)
            db.session.commit()
            print('✓ Usuario admin creado (admin@smartwatts.com / admin123)')

        # Crear usuario de prueba
        usuario = User.query.filter_by(email='usuario@smartwatts.com').first()
        if not usuario:
            usuario = User(
                nombre='Usuario Demo',
                email='usuario@smartwatts.com',
                rol='usuario',
                activo=True
            )
            usuario.set_password('usuario123')
            db.session.add(usuario)
            db.session.flush()
            
            presupuesto = Budget(
                usuario_id=usuario.id,
                presupuesto_mensual=5000,
                mes_año=datetime.utcnow().strftime('%Y-%m')
            )
            db.session.add(presupuesto)
            db.session.commit()
            print('✓ Usuario de prueba creado (usuario@smartwatts.com / usuario123)')


@app.shell_context_processor
def make_shell_context():
    """
    Hacer modelos disponibles en la shell interactiva de Flask.
    
    Permite usar los modelos directamente en: flask shell
    """
    return {
        'db': db,
        'User': User,
        'Device': Device,
        'Reading': Reading,
        'Notification': Notification,
        'EnergyRate': EnergyRate,
        'Budget': Budget
    }


if __name__ == '__main__':
    """
    Punto de entrada de la aplicación.
    
    Usar --help para ver opciones disponibles.
    """
    
    print("""
    ╔════════════════════════════════════════╗
    ║     SMART WATTS - Sistema IoT         ║
    ║   Monitoreo Inteligente de Consumo    ║
    ╚════════════════════════════════════════╝
    """)
    
    # Inicializar la aplicación
        if config_name == 'development':
        initialize_app()
    
    # Obtener configuración
    config_name = os.environ.get('FLASK_ENV', 'development')
    debug = config_name == 'development'
    
    print(f"""
    ✓ Entorno: {config_name.upper()}
    ✓ Debug: {debug}
    ✓ URL Base: http://localhost:5000
    ✓ Login: admin@smartwatts.com / admin123
    
    Presiona CTRL+C para detener el servidor
    """)
    
    # Ejecutar la aplicación con Socket.IO
    try:
        socketio.run(
            app,
            host='0.0.0.0',
            port=int(os.environ.get('PORT', 5000)),
            debug=debug,
            allow_unsafe_werkzeug=True
        )
    except KeyboardInterrupt:
        print("\n\n✓ Servidor detenido")
        sys.exit(0)
