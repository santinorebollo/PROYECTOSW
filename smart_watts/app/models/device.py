# ===============================================
# app/models/device.py
# ===============================================
# Modelo de Dispositivo IoT
#
# Este modelo representa a un dispositivo inteligente
# de monitoreo de consumo eléctrico.
#
# Gestiona:
# - Información del dispositivo (nombre, ubicación, etc.)
# - Estado y conectividad
# - Relaciones con lecturas de energía
# ===============================================

from app import db
from datetime import datetime, timedelta


class Device(db.Model):
    """
    Modelo de Dispositivo IoT.
    
    Representa a un medidor inteligente conectado a la red.
    Cada dispositivo pertenece a un usuario y registra
    lecturas periódicas de consumo eléctrico.
    
    Atributos:
        id (int): Identificador único del dispositivo
        nombre (str): Nombre descriptivo (ej: "Medidor Cocina")
        ubicacion (str): Ubicación física (ej: "Cocina principal")
        estado (str): Estado del dispositivo ('activo', 'inactivo', 'desconectado')
        usuario_id (int): ID del usuario propietario
        ultima_conexion (datetime): Última conexión del dispositivo
        firmware (str): Versión del firmware del dispositivo
        fecha_registro (datetime): Fecha de registro en el sistema
        token_api (str): Token único para autenticar lecturas del dispositivo
        
    Relaciones:
        usuario: Usuario propietario del dispositivo
        lecturas: Lecturas de energía registradas por este dispositivo
    """
    
    # ==================== NOMBRE DE LA TABLA ====================
    __tablename__ = 'device'
    
    # ==================== COLUMNAS ====================
    
    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)
    
    # Información básica del dispositivo
    nombre = db.Column(db.String(128), nullable=False, index=True)
    ubicacion = db.Column(db.String(128), nullable=True)
    
    # Estado y conectividad
    estado = db.Column(db.String(20), default='inactivo', nullable=False)
    # Estados: 'activo' (enviando datos), 'inactivo' (no envía datos)
    
    # Clave foránea hacia el propietario
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    # Conectividad
    ultima_conexion = db.Column(db.DateTime)
    # Se actualiza cada vez que el dispositivo envía datos
    
    # Información técnica
    firmware = db.Column(db.String(50), default='1.0.0')
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Token de autenticación para API REST
    token_api = db.Column(db.String(64), unique=True, nullable=False, index=True)
    
    # ==================== RELACIONES ====================
    
    # Relación uno-a-muchos: Un dispositivo tiene muchas lecturas
    lecturas = db.relationship('Reading', backref='dispositivo', lazy='dynamic',
                               cascade='all, delete-orphan')
    
    # ==================== MÉTODOS ====================
    
    def actualizar_ultima_conexion(self):
        """
        Actualizar el timestamp de última conexión.
        Se llama cada vez que el dispositivo envía datos.
        """
        self.ultima_conexion = datetime.utcnow()
        
        # Si el dispositivo está inactivo, marcarlo como activo
        if self.estado == 'inactivo':
            self.estado = 'activo'
        
        db.session.commit()
    
    def obtener_estado_conexion(self):
        """
        Obtener el estado actual de conexión del dispositivo.
        
        Determina si el dispositivo está 'activo', 'inactivo' o 'desconectado'
        basándose en la última conexión.
        
        Returns:
            str: 'activo', 'inactivo' o 'desconectado'
        """
        if not self.ultima_conexion:
            return 'desconectado'
        
        # Si no ha conectado en más de 1 hora, considerarlo desconectado
        ahora = datetime.utcnow()
        diferencia = ahora - self.ultima_conexion
        
        if diferencia > timedelta(hours=1):
            return 'desconectado'
        elif diferencia > timedelta(minutes=5):
            return 'inactivo'
        else:
            return 'activo'
    
    def obtener_ultima_lectura(self):
        """
        Obtener la lectura más reciente de este dispositivo.
        
        Returns:
            Reading: Objeto de la lectura más reciente, o None si no hay lecturas
        """
        from app.models.reading import Reading
        return Reading.query.filter_by(device_id=self.id)\
                            .order_by(Reading.fecha_hora.desc())\
                            .first()
    
    def obtener_lecturas_recientes(self, minutos=60):
        """
        Obtener las lecturas de los últimos N minutos.
        
        Args:
            minutos (int): Número de minutos hacia atrás
            
        Returns:
            list: Lista de lecturas recientes
        """
        from app.models.reading import Reading
        
        hace = datetime.utcnow() - timedelta(minutes=minutos)
        return Reading.query.filter(
            Reading.device_id == self.id,
            Reading.fecha_hora >= hace
        ).order_by(Reading.fecha_hora).all()
    
    def obtener_consumo_total(self, fecha_inicio=None, fecha_fin=None):
        """
        Obtener el consumo acumulado en un período.
        
        Si no se especifican fechas, calcula desde el registro del dispositivo.
        
        Args:
            fecha_inicio (datetime): Fecha inicial
            fecha_fin (datetime): Fecha final
            
        Returns:
            float: Consumo total en kWh
        """
        from app.models.reading import Reading
        from sqlalchemy import func
        
        query = Reading.query.filter_by(device_id=self.id)
        
        if fecha_inicio:
            query = query.filter(Reading.fecha_hora >= fecha_inicio)
        if fecha_fin:
            query = query.filter(Reading.fecha_hora <= fecha_fin)
        
        resultado = query.with_entities(func.sum(Reading.consumo)).scalar()
        return resultado or 0.0
    
    def obtener_potencia_actual(self):
        """
        Obtener la potencia instantánea actual.
        
        Returns:
            float: Potencia en Watts, o None si no hay datos
        """
        lectura = self.obtener_ultima_lectura()
        return lectura.potencia if lectura else None
    
    def marcar_desconectado(self):
        """
        Marcar el dispositivo como desconectado.
        Se llama cuando el dispositivo no responde por mucho tiempo.
        """
        self.estado = 'desconectado'
        db.session.commit()
    
    # ==================== MÉTODOS DE REPRESENTACIÓN ====================
    
    def __repr__(self):
        """Representación en texto para debugging"""
        return f'<Device {self.nombre} ({self.usuario_id})>'
    
    def to_dict(self):
        """
        Convertir dispositivo a diccionario para JSON API.
        
        Returns:
            dict: Datos del dispositivo en formato diccionario
        """
        ultima_lectura = self.obtener_ultima_lectura()
        
        return {
            'id': self.id,
            'nombre': self.nombre,
            'ubicacion': self.ubicacion,
            'estado': self.obtener_estado_conexion(),
            'usuario_id': self.usuario_id,
            'ultima_conexion': self.ultima_conexion.isoformat() if self.ultima_conexion else None,
            'firmware': self.firmware,
            'fecha_registro': self.fecha_registro.isoformat(),
            'potencia_actual': ultima_lectura.potencia if ultima_lectura else None,
            'consumo_total': self.obtener_consumo_total()
        }
