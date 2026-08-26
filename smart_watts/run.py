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
import eventlet
eventlet.monkey_patch()

from app import create_app
# o si tenés __init__.py: from . import create_app
# probá primero con "from app import create_app"

app = create_app()

if __name__ == "__main__":
    app.run()
