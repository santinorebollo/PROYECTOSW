# 🔌 Smart Watts - Sistema Inteligente de Monitoreo de Consumo Eléctrico

**Smart Watts** es una plataforma web profesional para monitoreo inteligente del consumo eléctrico que integra dispositivos IoT, análisis en tiempo real y gestión de presupuesto energético.

## ✨ Características Principales

### 📊 Dashboard Interactivo
- Visualización en tiempo real del consumo eléctrico
- Gráficos interactivos con Chart.js
- Estadísticas de energía y costos
- Estado de dispositivos conectados

### 🔌 Gestión de Dispositivos IoT
- Crear, editar y eliminar dispositivos
- Monitoreo en tiempo real del estado
- API REST para envío de datos desde dispositivos
- Token de autenticación único por dispositivo
- Historial completo de lecturas

### ⚠️ Sistema de Alertas Inteligentes
- Alertas por exceso de consumo
- Alertas preventivas por tendencia
- Alertas de presupuesto (70%, 85%, 100%)
- Centro de notificaciones con historial
- Notificaciones en tiempo real con Socket.IO

### 💰 Control de Costos y Presupuesto
- Configuración de tarifas energéticas
- Cálculo automático de costos
- Presupuesto mensual configurable
- Proyección de gastos
- Estimación de costos diarios/semanales/mensuales

### 📈 Reportes Avanzados
- Reporte diario con estadísticas detalladas
- Reporte semanal con comparativas
- Reporte mensual con tendencias
- Exportación a PDF y Excel (preparado)
- Análisis de dispositivos con mayor consumo

### 👥 Gestión de Usuarios
- Sistema de autenticación seguro
- Roles: Administrador y Usuario
- Control de acceso por permisos
- Gestión completa de usuarios (admin)
- Recuperación de contraseña

### 📡 Comunicación en Tiempo Real
- Socket.IO para WebSockets
- Actualización automática de datos
- Notificaciones instantáneas
- Sincronización de múltiples pestañas

## 🛠️ Tecnologías Utilizadas

### Backend
- **Python 3.8+**
- **Flask** - Framework web
- **SQLAlchemy** - ORM
- **Flask-Login** - Autenticación
- **Flask-SocketIO** - WebSockets
- **Flask-WTF** - Validación de formularios

### Frontend
- **HTML5**
- **CSS3** (personalizado con diseño moderno)
- **JavaScript (ES6+)**
- **Bootstrap 5** - Responsive design
- **Chart.js** - Gráficos interactivos
- **Font Awesome** - Iconos

### Base de Datos
- **SQLite** (desarrollo)
- **Preparada para MySQL/PostgreSQL** (producción)

## 📦 Instalación

### Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes)
- Git (opcional)

### Pasos de Instalación

1. **Clonar o descargar el proyecto**
```bash
git clone <url-del-repositorio>
cd smart_watts
```

2. **Crear entorno virtual**
```bash
# En Windows
python -m venv venv
venv\Scripts\activate

# En macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno** (opcional)
```bash
# Crear archivo .env
echo "FLASK_ENV=development" > .env
echo "SECRET_KEY=tu-clave-secreta" >> .env
```

5. **Ejecutar la aplicación**
```bash
python run.py
```

6. **Acceder a la aplicación**
```
http://localhost:5000
```

## 🔐 Credenciales de Prueba

Después de instalar, la aplicación crea automáticamente dos usuarios de prueba:

### Administrador
- **Email:** admin@smartwatts.local
- **Contraseña:** admin123
- **Permisos:** Acceso completo, gestión de usuarios y tarifas

### Usuario Regular
- **Email:** usuario@smartwatts.local
- **Contraseña:** usuario123
- **Permisos:** Ver sus dispositivos, consumo y reportes

## 📁 Estructura de Directorios

```
smart_watts/
├── app/
│   ├── models/              # Modelos de BD
│   │   ├── user.py
│   │   ├── device.py
│   │   ├── reading.py
│   │   ├── notification.py
│   │   └── energy_rate.py
│   ├── routes/              # Rutas/Blueprints
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── devices.py
│   │   ├── users.py
│   │   ├── notifications.py
│   │   ├── api.py
│   │   └── reports.py
│   ├── forms/               # Formularios con validación
│   │   ├── auth_forms.py
│   │   └── device_forms.py
│   ├── static/              # Archivos estáticos
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   └── main.js
│   │   └── img/
│   │       └── logo.png
│   ├── templates/           # Templates HTML
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── dashboard/
│   │   ├── devices/
│   │   └── ...
│   └── __init__.py         # Factory de aplicación
├── database/                # Base de datos
├── config.py               # Configuración
├── run.py                 # Punto de entrada
├── requirements.txt        # Dependencias
└── README.md              # Este archivo
```

## 🚀 API REST

Smart Watts proporciona una API REST para que los dispositivos IoT envíen datos.

### Autenticación
Todos los endpoints de API requieren token:
```
Authorization: Bearer <token_api_del_dispositivo>
```

### Endpoints Principales

#### Crear Lectura (POST)
```
POST /api/v1/lecturas
Content-Type: application/json
Authorization: Bearer <token>

{
    "voltaje": 220.5,
    "corriente": 5.2,
    "potencia": 1000,
    "consumo": 0.5,
    "frecuencia": 50,
    "factor_potencia": 0.95
}
```

#### Obtener Lecturas (GET)
```
GET /api/v1/lecturas?dispositivo_id=1&minutos=60&limite=100
Authorization: Bearer <token>
```

#### Obtener Dispositivos (GET)
```
GET /api/v1/dispositivos
Authorization: Bearer <token>
```

#### Estado API (GET)
```
GET /api/v1/estado
```

## 🔧 Configuración

### Variables de Entorno
```bash
# Entorno
FLASK_ENV=development  # development, testing, production

# Seguridad
SECRET_KEY=tu-clave-secreta

# Base de datos
DATABASE_URL=sqlite:///database/smart_watts.db

# Socket.IO
SOCKETIO_MESSAGE_QUEUE=None
```

### Configuración de Aplicación
Ver `config.py` para parámetros configurables:
- Precio por kWh
- Impuestos
- Cargos fijos
- Límites de alertas
- Temas de colores

## 📊 Modelos de Datos

### User (Usuario)
```python
- id: Identificador único
- nombre: Nombre completo
- email: Correo electrónico único
- password_hash: Contraseña hasheada
- rol: 'admin' o 'usuario'
- activo: Boolean
- fecha_creacion: DateTime
```

### Device (Dispositivo IoT)
```python
- id: Identificador único
- nombre: Nombre descriptivo
- ubicacion: Ubicación física
- estado: 'activo', 'inactivo', 'desconectado'
- usuario_id: FK del propietario
- ultima_conexion: DateTime
- firmware: Versión del firmware
- token_api: Token de autenticación única
```

### Reading (Lectura de Energía)
```python
- id: Identificador único
- device_id: FK del dispositivo
- voltaje: En Voltios (V)
- corriente: En Amperios (A)
- potencia: En Watts (W)
- consumo: En kWh
- frecuencia: En Hertz (Hz)
- factor_potencia: 0-1
- fecha_hora: Timestamp
```

### Notification (Notificación)
```python
- id: Identificador único
- usuario_id: FK del usuario
- tipo: 'consumo', 'preventiva', 'presupuesto', 'dispositivo'
- mensaje: Texto de la notificación
- leida: Boolean
- fecha: DateTime
- device_id: FK del dispositivo (opcional)
```

### Budget (Presupuesto)
```python
- id: Identificador único
- usuario_id: FK del usuario
- presupuesto_mensual: Cantidad en moneda local
- fecha: DateTime
- mes_año: YYYY-MM
```

### EnergyRate (Tarifa Energética)
```python
- id: Identificador único
- precio_kwh: Precio por kWh
- impuestos: Porcentaje de impuesto
- cargos_fijos: Cargo fijo mensual
- fecha_actualizacion: DateTime
```

## 🔑 Seguridad

- ✅ Hash seguro de contraseñas (PBKDF2)
- ✅ Protección CSRF en formularios
- ✅ Validación de entradas
- ✅ Control de acceso por roles
- ✅ Sesiones seguras con cookies HttpOnly
- ✅ Autenticación de dispositivos por token

## 🧪 Testing

Para ejecutar pruebas:
```bash
# Con pytest
pytest

# Con coverage
pytest --cov=app
```

## 📚 Documentación Adicional

### Para Desarrolladores
- Código comentado detalladamente
- Docstrings en todas las funciones
- Arquitectura modular y escalable
- Patrones de diseño SOLID

### Para Usuarios
- Manual de usuario (próximamente)
- Video tutorial (próximamente)
- Guía de integración IoT (próximamente)

## 🤝 Contribuir

Las contribuciones son bienvenidas. Para cambios mayores:
1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 📞 Soporte

¿Tienes preguntas o sugerencias?
- 📧 Email: support@smartwatts.local
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions

## 🎯 Roadmap

### v1.1 (Próximo)
- [ ] Exportación a PDF
- [ ] Exportación a Excel
- [ ] Gráficos comparativos
- [ ] Dashboard personalizable
- [ ] Temas oscuro/claro

### v1.2
- [ ] Soporte multi-idioma
- [ ] API de terceros
- [ ] Integración con plataformas IoT
- [ ] Predicción de consumo con IA
- [ ] Móvil app nativa

### v2.0
- [ ] Escalabilidad horizontal
- [ ] Microservicios
- [ ] Analytics avanzado
- [ ] Machine Learning
- [ ] Blockchain para auditoría

## 👨‍💻 Autor

**Smart Watts Development Team**

## 🙏 Agradecimientos

- Flask y su comunidad
- Socket.IO por WebSockets
- Chart.js por gráficos
- Bootstrap por diseño responsivo

---

**Smart Watts v1.0.0** | Hecho con ❤️ para IoT
