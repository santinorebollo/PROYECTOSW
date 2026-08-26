# ===============================================
# app/models/reading.py
# ===============================================
# Modelo de Lectura de Energía
#
# Representa una medición instantánea de parámetros
# eléctricos enviada por un dispositivo IoT.
#
# Cada lectura contiene valores como voltaje, corriente,
# potencia y energía consumida en un momento específico.
# ===============================================

from app import db
from datetime import datetime


class Reading(db.Model):
    """
    Modelo de Lectura de Energía.
    
    Representa una medición instantánea de parámetros eléctricos
    enviada por un dispositivo IoT en un momento específico.
    
    Las lecturas se almacenan con alta frecuencia (típicamente cada minuto)
    permitiendo análisis detallados del consumo.
    
    Atributos:
        id (int): Identificador único de la lectura
        device_id (int): ID del dispositivo que envía la lectura
        voltaje (float): Voltaje instantáneo en Voltios (V)
        corriente (float): Corriente instantánea en Amperios (A)
        potencia (float): Potencia instantánea en Watts (W)
        consumo (float): Consumo de energía registrado en kWh
        frecuencia (float): Frecuencia de la red en Hertz (Hz)
        factor_potencia (float): Factor de potencia (0-1)
        fecha_hora (datetime): Timestamp de la lectura
        
    Relaciones:
        dispositivo: Dispositivo que envió esta lectura
    
    Notas:
        - Las lecturas se indexan por fecha para búsquedas rápidas
        - El consumo es un valor acumulado
        - Todos los valores eléctricos son instantáneos en ese momento
    """
    
    # ==================== NOMBRE DE LA TABLA ====================
    __tablename__ = 'reading'
    
    # ==================== COLUMNAS ====================
    
    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)
    
    # Relación con el dispositivo
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), 
                          nullable=False, index=True)
    
    # ==================== PARÁMETROS ELÉCTRICOS ====================
    # Valores instantáneos en el momento de la lectura
    
    # Voltaje en Voltios (V)
    voltaje = db.Column(db.Float, nullable=False)
    # Rango típico: 200-240V en Argentina
    
    # Corriente en Amperios (A)
    corriente = db.Column(db.Float, nullable=False)
    # Calculado como: Potencia / Voltaje
    
    # Potencia instantánea en Watts (W)
    potencia = db.Column(db.Float, nullable=False)
    # Calculado como: Voltaje × Corriente × Factor de Potencia
    
    # Consumo acumulado en kilowatt-hora (kWh)
    # Este es un valor acumulativo desde el inicio del dispositivo
    consumo = db.Column(db.Float, default=0, nullable=False)
    
    # Frecuencia de la red en Hertz (Hz)
    frecuencia = db.Column(db.Float, nullable=False, default=50)
    # En Argentina: 50 Hz
    
    # Factor de potencia (0-1)
    # 1.0 = potencia completamente resistiva (ideal)
    # < 1.0 = hay componente reactiva (dispositivos inductivos/capacitivos)
    factor_potencia = db.Column(db.Float, default=1.0, nullable=False)
    
    # ==================== TIMESTAMP ====================
    # Fecha y hora de la lectura (UTC)
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # ==================== MÉTODOS ====================
    
    @staticmethod
    def calcular_potencia(voltaje, corriente, factor_potencia=1.0):
        """
        Calcular la potencia activa a partir de voltaje y corriente.
        
        Fórmula: P = V × I × cos(φ)
        Donde cos(φ) es el factor de potencia
        
        Args:
            voltaje (float): Voltaje en Voltios
            corriente (float): Corriente en Amperios
            factor_potencia (float): Factor de potencia (0-1)
            
        Returns:
            float: Potencia activa en Watts
        """
        return voltaje * corriente * factor_potencia
    
    def obtener_energia_consumida_desde(self, fecha_inicio):
        """
        Calcular la energía consumida desde una fecha específica.
        
        Suma todas las lecturas posteriores a la fecha especificada.
        
        Args:
            fecha_inicio (datetime): Fecha desde la cual calcular
            
        Returns:
            float: Energía consumida en kWh
        """
        from sqlalchemy import func
        
        resultado = Reading.query.filter(
            Reading.device_id == self.device_id,
            Reading.fecha_hora >= fecha_inicio,
            Reading.fecha_hora <= self.fecha_hora
        ).with_entities(func.sum(Reading.consumo - 
                                (func.lag(Reading.consumo).over(
                                    order_by=Reading.fecha_hora
                                )))
        ).scalar()
        
        return resultado or 0.0
    
    def es_anomalia(self, desviacion_std=3):
        """
        Detectar si esta lectura representa una anomalía.

        Compara la potencia actual con el promedio histórico.
        Si se desvía más de N desviaciones estándar, es anomalía.

        Args:
            desviacion_std (float): Número de desviaciones estándar

        Returns:
            bool: True si es una anomalía
        """
        import statistics

        # Obtener las potencias de las últimas 100 lecturas
        lecturas = Reading.query.filter_by(device_id=self.device_id)\
                                .order_by(Reading.fecha_hora.desc())\
                                .limit(100)\
                                .with_entities(Reading.potencia).all()

        potencias = [p[0] for p in lecturas]

        if len(potencias) < 2:
            return False

        promedio = statistics.mean(potencias)
        desv = statistics.stdev(potencias)

        if desv == 0:
            return False

        # Si la lectura se desvía más de desviacion_std * desv, es anomalía
        return abs(self.potencia - promedio) > (desviacion_std * desv)
    
    def obtener_consumo_desde_ultima_lectura(self):
        """
        Obtener el consumo desde la lectura anterior.
        
        Returns:
            float: Diferencia de consumo en kWh
        """
        lectura_anterior = Reading.query.filter(
            Reading.device_id == self.device_id,
            Reading.fecha_hora < self.fecha_hora
        ).order_by(Reading.fecha_hora.desc()).first()
        
        if not lectura_anterior:
            return self.consumo
        
        return max(0, self.consumo - lectura_anterior.consumo)
    
    # ==================== MÉTODOS DE REPRESENTACIÓN ====================
    
    def __repr__(self):
        """Representación en texto para debugging"""
        return f'<Reading {self.device_id}: {self.potencia}W>'
    
    def to_dict(self):
        """
        Convertir lectura a diccionario para JSON API.
        
        Returns:
            dict: Datos de la lectura en formato diccionario
        """
        return {
            'id': self.id,
            'device_id': self.device_id,
            'voltaje': round(self.voltaje, 2),
            'corriente': round(self.corriente, 2),
            'potencia': round(self.potencia, 2),
            'consumo': round(self.consumo, 3),
            'frecuencia': round(self.frecuencia, 1),
            'factor_potencia': round(self.factor_potencia, 3),
            'fecha_hora': self.fecha_hora.isoformat(),
            'consumo_desde_anterior': round(self.obtener_consumo_desde_ultima_lectura(), 3)
        }
