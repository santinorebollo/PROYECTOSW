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

from __init__ import create_app

app = create_app()

if __name__ == "__main__":
    app.run()

