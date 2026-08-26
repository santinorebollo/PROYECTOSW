# 📋 Guía de Instalación - Smart Watts

## Requisitos del Sistema

- **Python 3.8+** (recomendado 3.10 o superior)
- **pip** (gestor de paquetes de Python)
- **Git** (opcional, para clonar el repositorio)
- **Navegador moderno** (Chrome, Firefox, Safari, Edge)
- **2 GB de RAM mínimo**
- **500 MB de espacio en disco**

## Instalación Rápida (5 minutos)

### 1. Descargar el proyecto

```bash
# Con Git (recomendado)
git clone <url-del-repositorio>
cd smart_watts

# O descargar ZIP manualmente
# Descargar → Extraer → Abrir terminal en la carpeta
```

### 2. Crear entorno virtual

```bash
# En Windows
python -m venv venv
venv\\Scripts\\activate

# En macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación

```bash
python run.py
```

### 5. Abrir en navegador

```
http://localhost:5000
```

**Credenciales de demostración:**
- Admin: `admin@smartwatts.local` / `admin123`
- Usuario: `usuario@smartwatts.local` / `usuario123`

## Instalación Detallada (Windows)

### Paso 1: Instalar Python

1. Descargar Python desde [python.org](https://www.python.org/downloads/)
2. Ejecutar instalador
3. **IMPORTANTE:** Marcar ✓ "Add Python to PATH"
4. Hacer clic en "Install Now"

Verificar instalación:
```bash
python --version
pip --version
```

### Paso 2: Descargar Smart Watts

1. Descargar desde GitHub o GitLab
2. Extraer en una carpeta (ej: `C:\\Users\\tu_usuario\\smart_watts`)
3. Abrir Command Prompt en esa carpeta

### Paso 3: Crear entorno virtual

```cmd
python -m venv venv
```

Activar:
```cmd
venv\\Scripts\\activate
```

Deberías ver `(venv)` al inicio de la línea de comandos

### Paso 4: Instalar dependencias

```cmd
pip install -r requirements.txt
```

Esperar a que termine (puede tomar 2-3 minutos)

### Paso 5: Ejecutar aplicación

```cmd
python run.py
```

Verás algo como:
```
╔════════════════════════════════════════╗
║     SMART WATTS - Sistema IoT         ║
║   Monitoreo Inteligente de Consumo    ║
╚════════════════════════════════════════╝

✓ Entorno: DEVELOPMENT
✓ Debug: True
✓ URL Base: http://localhost:5000
✓ Login: admin@smartwatts.local / admin123

Presiona CTRL+C para detener el servidor
```

### Paso 6: Acceder a la aplicación

1. Abrir navegador (Chrome, Firefox, etc.)
2. Ir a `http://localhost:5000`
3. Usar credenciales de demostración
4. ¡Disfrutar! 🎉

## Instalación en macOS

### Paso 1: Instalar Homebrew (si no lo tienes)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Paso 2: Instalar Python

```bash
brew install python@3.10
```

### Paso 3: Descargar Smart Watts

```bash
cd ~
git clone <url-del-repositorio>
cd smart_watts
```

### Paso 4-6: Mismo que en Linux

Ver sección "Instalación en Linux"

## Instalación en Linux (Ubuntu/Debian)

### Paso 1: Actualizar sistema

```bash
sudo apt update
sudo apt upgrade -y
```

### Paso 2: Instalar Python y dependencias

```bash
sudo apt install -y python3.10 python3.10-venv python3-pip
```

### Paso 3: Descargar Smart Watts

```bash
cd ~
git clone <url-del-repositorio>
cd smart_watts
```

### Paso 4: Crear entorno virtual

```bash
python3.10 -m venv venv
source venv/bin/activate
```

### Paso 5: Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 6: Ejecutar aplicación

```bash
python3.10 run.py
```

### Paso 7: Acceder

Abrir navegador en `http://localhost:5000`

## Configuración Avanzada

### Variables de Entorno

Crear archivo `.env`:

```bash
# En Windows (Notepad)
# Crear archivo llamado .env en la carpeta smart_watts

# En macOS/Linux
cat > .env << EOF
FLASK_ENV=development
SECRET_KEY=tu-clave-secreta-muy-segura
EOF
```

Ejemplo de `.env`:
```
FLASK_ENV=development
SECRET_KEY=mi-clave-secreta-super-segura-12345
DATABASE_URL=sqlite:///database/smart_watts.db
FLASK_RUN_PORT=5000
```

### Base de Datos en PostgreSQL

Para producción, cambiar a PostgreSQL:

```bash
# Instalar driver
pip install psycopg2-binary

# Actualizar .env
DATABASE_URL=postgresql://usuario:contraseña@localhost/smart_watts

# Crear base de datos
createdb smart_watts
```

### Usar puerto diferente

```bash
# En Windows
set FLASK_RUN_PORT=8000
python run.py

# En macOS/Linux
export FLASK_RUN_PORT=8000
python run.py
```

Luego acceder a `http://localhost:8000`

## Solución de Problemas

### Error: `python: command not found`

**Windows:**
- Python no está en el PATH
- Reinstalar Python y marcar "Add to PATH"

**macOS/Linux:**
- Usar `python3` en lugar de `python`

### Error: `ModuleNotFoundError: No module named 'flask'`

Asegurarse de que el entorno virtual está activado:

```bash
# Verificar que veas (venv) al inicio
# Si no, activar:
source venv/bin/activate  # macOS/Linux
venv\\Scripts\\activate  # Windows
```

### Error: `Port 5000 already in use`

Cambiar puerto:
```bash
export FLASK_RUN_PORT=5001
python run.py
```

### Base de datos bloqueada

Eliminar archivo de BD y recrearlo:
```bash
rm database/smart_watts.db
python run.py
```

### Error al conectar dispositivo IoT

Verificar:
1. Dispositivo en la misma red
2. Token API correcto
3. Formato JSON válido

Ejemplo de lectura correcta:
```json
{
    "voltaje": 220.5,
    "corriente": 5.2,
    "potencia": 1000,
    "consumo": 0.5,
    "frecuencia": 50,
    "factor_potencia": 0.95
}
```

## Desarrollo Local

### Modo Debug

Ya está habilitado en desarrollo. Los cambios en código se recargan automáticamente.

### Crear datos de prueba

```bash
python run.py seed_db
```

Esto crea usuarios y tarifas de demostración.

### Acceder a BD

```bash
python run.py shell
>>> from app.models import *
>>> users = User.query.all()
>>> print(users)
```

### Resetear BD completamente

```bash
# Eliminar base de datos
rm database/smart_watts.db

# Ejecutar app nuevamente
python run.py
```

## Producción (Guía Rápida)

### Con Gunicorn

```bash
# Instalar
pip install gunicorn

# Ejecutar (4 workers)
gunicorn -w 4 -b 0.0.0.0:5000 'run:app'
```

### Con Nginx (recomendado)

Ver documentación de [Nginx + Gunicorn](https://docs.nginx.com/nginx/admin-guide/)

### Variables de producción

```bash
export FLASK_ENV=production
export SECRET_KEY=clave-super-segura-aleatoria
export DATABASE_URL=postgresql://...
```

## Actualizar dependencias

```bash
pip install --upgrade -r requirements.txt
```

## Desinstalar

### Windows

```cmd
# Desactivar entorno
deactivate

# Eliminar carpeta venv
rmdir /s venv

# Eliminar carpeta del proyecto
rmdir /s smart_watts
```

### macOS/Linux

```bash
# Desactivar entorno
deactivate

# Eliminar carpeta
rm -rf venv smart_watts
```

## Soporte Técnico

¿Problemas en la instalación?

1. Verificar **Python 3.8+**: `python --version`
2. Verificar **pip**: `pip --version`
3. Revisar **requirements.txt**
4. Leer mensajes de error completamente
5. Buscar error en [Google](https://google.com)
6. Contactar soporte: support@smartwatts.local

## Próximos Pasos

Después de instalar:

1. ✅ Cambiar credenciales de demostración
2. ✅ Configurar tarifas energéticas
3. ✅ Crear presupuesto personal
4. ✅ Conectar dispositivos IoT
5. ✅ Ver primeras lecturas

¡Bienvenido a Smart Watts! 🚀
