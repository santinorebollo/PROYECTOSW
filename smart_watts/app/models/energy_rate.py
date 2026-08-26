# ===============================================
# app/models/energy_rate.py y budget.py
# ===============================================
# Modelos de Tarifa Energética y Presupuesto
#
# EnergyRate: Configuración de tarifas eléctricas
# Budget: Presupuesto mensual por usuario
# ===============================================

from app import db
from datetime import datetime


class EnergyRate(db.Model):
    """
    Modelo de Tarifa Energética.
    
    Define los precios y cargos para el cálculo de costos energéticos.
    Normalmente hay una sola tarifa global configurada por el administrador.
    
    Atributos:
        id (int): Identificador único
        precio_kwh (float): Precio por kilowatt-hora en la moneda local
        impuestos (float): Porcentaje de impuestos a aplicar
        cargos_fijos (float): Cargo fijo mensual en la moneda local
        fecha_actualizacion (datetime): Última actualización de la tarifa
    """
    
    # ==================== NOMBRE DE LA TABLA ====================
    __tablename__ = 'energy_rate'
    
    # ==================== COLUMNAS ====================
    
    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)
    
    # Precio base por kWh
    # Ejemplo: 50.0 ARS por kWh
    precio_kwh = db.Column(db.Float, nullable=False)
    
    # Porcentaje de impuestos a agregar
    # Ejemplo: 10.5 = 10.5% de impuesto
    impuestos = db.Column(db.Float, default=0, nullable=False)
    
    # Cargo fijo mensual
    # Algunos proveedores cobran un mínimo mensual
    # Ejemplo: 200 ARS fijos
    cargos_fijos = db.Column(db.Float, default=0, nullable=False)
    
    # Fecha de última actualización
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, 
                                   onupdate=datetime.utcnow, nullable=False)
    
    # ==================== MÉTODOS ====================
    
    def calcular_costo_kwh(self, consumo_kwh):
        """
        Calcular el costo total para un consumo dado.
        
        Fórmula: (consumo × precio_kwh) × (1 + impuestos/100) + cargos_fijos
        
        Args:
            consumo_kwh (float): Consumo en kWh
            
        Returns:
            tuple: (costo_sin_impuesto, impuesto, costo_total)
        """
        # Costo sin impuesto
        costo_base = consumo_kwh * self.precio_kwh
        
        # Impuesto
        monto_impuesto = costo_base * (self.impuestos / 100)
        
        # Total con impuesto y cargo fijo
        costo_total = costo_base + monto_impuesto + self.cargos_fijos
        
        return (costo_base, monto_impuesto, costo_total)
    
    def calcular_costo_estimado_mes(self, consumo_estimado_kwh):
        """
        Calcular el costo estimado mensual.
        
        Args:
            consumo_estimado_kwh (float): Consumo estimado mensual en kWh
            
        Returns:
            float: Costo estimado en la moneda local
        """
        _, _, costo_total = self.calcular_costo_kwh(consumo_estimado_kwh)
        return costo_total
    
    @staticmethod
    def obtener_tarifa_actual():
        """
        Obtener la tarifa energética actual.
        
        Returns:
            EnergyRate: Objeto de tarifa, o None si no existe
        """
        return EnergyRate.query.first()
    
    # ==================== MÉTODOS DE REPRESENTACIÓN ====================
    
    def __repr__(self):
        """Representación en texto para debugging"""
        return f'<EnergyRate {self.precio_kwh} ARS/kWh>'
    
    def to_dict(self):
        """Convertir a diccionario para JSON API"""
        return {
            'id': self.id,
            'precio_kwh': round(self.precio_kwh, 2),
            'impuestos': round(self.impuestos, 2),
            'cargos_fijos': round(self.cargos_fijos, 2),
            'fecha_actualizacion': self.fecha_actualizacion.isoformat()
        }


class Budget(db.Model):
    """
    Modelo de Presupuesto Energético.
    
    Define el presupuesto mensual de cada usuario para control de gastos.
    
    Atributos:
        id (int): Identificador único
        usuario_id (int): ID del usuario propietario del presupuesto
        presupuesto_mensual (float): Presupuesto mensual en la moneda local
        fecha (datetime): Fecha de creación/actualización del presupuesto
        mes_año (str): Mes y año al que aplica (YYYY-MM)
    """
    
    # ==================== NOMBRE DE LA TABLA ====================
    __tablename__ = 'budget'
    
    # ==================== COLUMNAS ====================
    
    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)
    
    # Relación con el usuario
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), 
                          nullable=False, index=True, unique=True)
    
    # Presupuesto mensual en la moneda local
    presupuesto_mensual = db.Column(db.Float, nullable=False)
    # Ejemplo: 5000 ARS por mes
    
    # Fecha de creación/actualización
    fecha = db.Column(db.DateTime, default=datetime.utcnow, 
                     onupdate=datetime.utcnow, nullable=False)
    
    # Mes y año al que aplica (para histórico)
    mes_año = db.Column(db.String(7), nullable=False)
    # Formato: YYYY-MM (ejemplo: 2024-01)
    
    # ==================== MÉTODOS ====================
    
    def obtener_gasto_actual(self):
        """
        Obtener el gasto energético actual del mes.
        
        Returns:
            float: Gasto en la moneda local
        """
        from app.models.user import User
        from datetime import datetime, timedelta
        
        # Obtener primer día del mes actual
        hoy = datetime.utcnow()
        primer_dia = datetime(hoy.year, hoy.month, 1)
        
        usuario = User.query.get(self.usuario_id)
        consumo_total = 0
        
        # Sumar consumo de todos los dispositivos
        for dispositivo in usuario.dispositivos:
            consumo_total += dispositivo.obtener_consumo_total(primer_dia)
        
        # Calcular costo
        tarifa = EnergyRate.obtener_tarifa_actual()
        if tarifa:
            _, _, costo = tarifa.calcular_costo_kwh(consumo_total)
            return costo
        
        return 0
    
    def obtener_porcentaje_usado(self):
        """
        Obtener el porcentaje del presupuesto utilizado.
        
        Returns:
            float: Porcentaje (0-100)
        """
        gasto = self.obtener_gasto_actual()
        if self.presupuesto_mensual == 0:
            return 0
        return (gasto / self.presupuesto_mensual) * 100
    
    def obtener_dinero_restante(self):
        """
        Obtener el dinero restante del presupuesto.
        
        Returns:
            float: Dinero disponible en la moneda local
        """
        gasto = self.obtener_gasto_actual()
        return max(0, self.presupuesto_mensual - gasto)
    
    def obtener_alerta_necesaria(self):
        """
        Obtener si se necesita generar una alerta de presupuesto.
        
        Returns:
            int: Hito de alerta (70, 85, 100) o None si no se necesita
        """
        from config import Config
        
        porcentaje = self.obtener_porcentaje_usado()
        
        # Verificar en orden inverso para obtener el hito más reciente
        for hito in [100, 85, 70]:
            if porcentaje >= hito:
                return hito
        
        return None
    
    @staticmethod
    def obtener_o_crear_para_usuario(usuario_id, presupuesto_inicial=5000):
        """
        Obtener o crear el presupuesto del usuario.
        
        Args:
            usuario_id (int): ID del usuario
            presupuesto_inicial (float): Presupuesto por defecto
            
        Returns:
            Budget: Objeto del presupuesto
        """
        from datetime import datetime
        
        # Obtener mes y año actual
        ahora = datetime.utcnow()
        mes_año = ahora.strftime('%Y-%m')
        
        # Buscar presupuesto existente
        presupuesto = Budget.query.filter_by(
            usuario_id=usuario_id,
            mes_año=mes_año
        ).first()
        
        if not presupuesto:
            # Crear nuevo presupuesto para este mes
            presupuesto = Budget(
                usuario_id=usuario_id,
                presupuesto_mensual=presupuesto_inicial,
                mes_año=mes_año
            )
            db.session.add(presupuesto)
            db.session.commit()
        
        return presupuesto
    
    # ==================== MÉTODOS DE REPRESENTACIÓN ====================
    
    def __repr__(self):
        """Representación en texto para debugging"""
        return f'<Budget {self.usuario_id}: {self.presupuesto_mensual}>'
    
    def to_dict(self):
        """Convertir a diccionario para JSON API"""
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'presupuesto_mensual': round(self.presupuesto_mensual, 2),
            'gasto_actual': round(self.obtener_gasto_actual(), 2),
            'dinero_restante': round(self.obtener_dinero_restante(), 2),
            'porcentaje_usado': round(self.obtener_porcentaje_usado(), 1),
            'fecha': self.fecha.isoformat(),
            'mes_año': self.mes_año
        }
