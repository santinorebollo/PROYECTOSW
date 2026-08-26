# ===============================================
# app/models/notification.py
# ===============================================
# Modelo de Notificación
#
# Representa una notificación o alerta en el sistema.
# Las notificaciones se generan por eventos como:
# - Exceso de consumo
# - Alertas preventivas
# - Alcanzar presupuesto
# - Dispositivos desconectados
# ===============================================

from app import db
from datetime import datetime


class Notification(db.Model):
    """
    Modelo de Notificación.
    
    Representa una notificación o alerta generada por el sistema.
    Permite a los usuarios estar informados sobre eventos importantes.
    
    Atributos:
        id (int): Identificador único de la notificación
        usuario_id (int): ID del usuario que recibe la notificación
        tipo (str): Tipo de notificación (alerta, advertencia, info)
        mensaje (str): Texto de la notificación
        leida (bool): Indica si el usuario ha visto la notificación
        fecha (datetime): Fecha de creación de la notificación
        device_id (int): ID del dispositivo relacionado (opcional)
        
    Tipos de notificaciones:
        - 'consumo': Alerta por exceso de consumo
        - 'preventiva': Alerta preventiva de presupuesto
        - 'presupuesto': Alerta por hito de presupuesto
        - 'dispositivo': Alerta sobre dispositivos
        - 'sistema': Notificaciones del sistema
        
    Relaciones:
        usuario: Usuario que recibe la notificación
    """
    
    # ==================== NOMBRE DE LA TABLA ====================
    __tablename__ = 'notification'
    
    # ==================== COLUMNAS ====================
    
    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)
    
    # Relación con el usuario
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), 
                          nullable=False, index=True)
    
    # Tipo de notificación
    tipo = db.Column(db.String(50), nullable=False, index=True)
    # Tipos: 'consumo', 'preventiva', 'presupuesto', 'dispositivo', 'sistema'
    
    # Contenido de la notificación
    mensaje = db.Column(db.Text, nullable=False)
    
    # Estado de lectura
    leida = db.Column(db.Boolean, default=False, nullable=False, index=True)
    
    # Timestamp
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Referencia opcional a un dispositivo
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=True)
    
    # ==================== MÉTODOS ====================
    
    def marcar_como_leida(self):
        """
        Marcar la notificación como leída por el usuario.
        """
        self.leida = True
        db.session.commit()
    
    def marcar_como_no_leida(self):
        """
        Marcar la notificación como no leída.
        """
        self.leida = False
        db.session.commit()
    
    @staticmethod
    def crear_alerta_consumo(usuario_id, device_id, consumo_actual, limite):
        """
        Crear una notificación de alerta por exceso de consumo.
        
        Args:
            usuario_id (int): ID del usuario
            device_id (int): ID del dispositivo
            consumo_actual (float): Consumo actual en kWh
            limite (float): Límite configurado en kWh
        """
        mensaje = f'⚠️ Se ha superado el límite de consumo. Consumo: {consumo_actual:.2f} kWh / Límite: {limite:.2f} kWh'
        
        notificacion = Notification(
            usuario_id=usuario_id,
            tipo='consumo',
            mensaje=mensaje,
            device_id=device_id
        )
        
        db.session.add(notificacion)
        db.session.commit()
        
        return notificacion
    
    @staticmethod
    def crear_alerta_preventiva(usuario_id, porcentaje_consumido):
        """
        Crear una notificación de alerta preventiva.
        
        Args:
            usuario_id (int): ID del usuario
            porcentaje_consumido (float): Porcentaje del presupuesto consumido
        """
        mensaje = f'⚠️ Según la tendencia actual, superarás el límite de consumo este mes. ({porcentaje_consumido:.1f}% consumido)'
        
        notificacion = Notification(
            usuario_id=usuario_id,
            tipo='preventiva',
            mensaje=mensaje
        )
        
        db.session.add(notificacion)
        db.session.commit()
        
        return notificacion
    
    @staticmethod
    def crear_alerta_presupuesto(usuario_id, porcentaje_usado, hito):
        """
        Crear una notificación por hito de presupuesto.
        
        Args:
            usuario_id (int): ID del usuario
            porcentaje_usado (float): Porcentaje del presupuesto utilizado
            hito (int): Hito alcanzado (70, 85, 100)
        """
        iconos = {70: '⚠️', 85: '🔴', 100: '❌'}
        icono = iconos.get(hito, '⚠️')
        
        mensaje = f'{icono} Has utilizado el {porcentaje_usado:.1f}% de tu presupuesto mensual'
        
        notificacion = Notification(
            usuario_id=usuario_id,
            tipo='presupuesto',
            mensaje=mensaje
        )
        
        db.session.add(notificacion)
        db.session.commit()
        
        return notificacion
    
    @staticmethod
    def crear_alerta_dispositivo(usuario_id, device_id, estado_nuevo):
        """
        Crear una notificación sobre el estado de un dispositivo.
        
        Args:
            usuario_id (int): ID del usuario
            device_id (int): ID del dispositivo
            estado_nuevo (str): Nuevo estado del dispositivo
        """
        from app.models.device import Device
        dispositivo = Device.query.get(device_id)
        
        if estado_nuevo == 'desconectado':
            mensaje = f'📡 El dispositivo "{dispositivo.nombre}" se ha desconectado'
        elif estado_nuevo == 'activo':
            mensaje = f'✅ El dispositivo "{dispositivo.nombre}" está activo nuevamente'
        else:
            mensaje = f'ℹ️ El dispositivo "{dispositivo.nombre}" cambió de estado a {estado_nuevo}'
        
        notificacion = Notification(
            usuario_id=usuario_id,
            tipo='dispositivo',
            mensaje=mensaje,
            device_id=device_id
        )
        
        db.session.add(notificacion)
        db.session.commit()
        
        return notificacion
    
    @staticmethod
    def obtener_no_leidas(usuario_id):
        """
        Obtener todas las notificaciones no leídas de un usuario.
        
        Args:
            usuario_id (int): ID del usuario
            
        Returns:
            list: Lista de notificaciones no leídas
        """
        return Notification.query.filter_by(
            usuario_id=usuario_id,
            leida=False
        ).order_by(Notification.fecha.desc()).all()
    
    @staticmethod
    def contar_no_leidas(usuario_id):
        """
        Contar las notificaciones no leídas de un usuario.
        
        Args:
            usuario_id (int): ID del usuario
            
        Returns:
            int: Cantidad de notificaciones no leídas
        """
        return Notification.query.filter_by(
            usuario_id=usuario_id,
            leida=False
        ).count()
    
    # ==================== MÉTODOS DE REPRESENTACIÓN ====================
    
    def __repr__(self):
        """Representación en texto para debugging"""
        return f'<Notification {self.tipo}: {self.usuario_id}>'
    
    def to_dict(self):
        """
        Convertir notificación a diccionario para JSON API.
        
        Returns:
            dict: Datos de la notificación en formato diccionario
        """
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'tipo': self.tipo,
            'mensaje': self.mensaje,
            'leida': self.leida,
            'fecha': self.fecha.isoformat(),
            'device_id': self.device_id
        }
