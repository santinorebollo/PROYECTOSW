# 📱 Guía de Integración de Dispositivos IoT

Esta guía explica cómo conectar tus dispositivos IoT a Smart Watts para enviar lecturas de energía.

## Requisitos

- **URL de Smart Watts**: `http://servidor:5000` (ej: `http://192.168.1.100:5000`)
- **Token API del dispositivo**: Se obtiene al crear el dispositivo en el panel
- **Conexión a Internet**: El dispositivo debe poder conectar al servidor

## Obtener Token API

### 1. Crear dispositivo en Smart Watts

1. Ir a **Dispositivos** → **Nuevo Dispositivo**
2. Llenar formulario:
   - **Nombre**: "Medidor Cocina"
   - **Ubicación**: "Cocina principal"
   - **Firmware**: "1.0.0"
3. Hacer clic en **Crear Dispositivo**
4. Copiar el **Token API** que aparece (algo como: `eyJ0eXAiOiJKV1QiLCJhbGc...`)

## Ejemplos de Código

### Python (Recomendado)

```python
import requests
import json
from datetime import datetime

# Configuración
SMART_WATTS_URL = "http://192.168.1.100:5000"
DEVICE_TOKEN = "tu-token-api-aqui"

# Headers con token
headers = {
    "Authorization": f"Bearer {DEVICE_TOKEN}",
    "Content-Type": "application/json"
}

# Datos de lectura (ejemplo)
lectura = {
    "voltaje": 220.5,      # Voltios
    "corriente": 5.2,      # Amperios
    "potencia": 1100,      # Watts
    "consumo": 0.5,        # kWh (energía acumulada)
    "frecuencia": 50,      # Hertz
    "factor_potencia": 0.95 # 0-1
}

# Enviar lectura
response = requests.post(
    f"{SMART_WATTS_URL}/api/v1/lecturas",
    json=lectura,
    headers=headers
)

# Verificar respuesta
if response.status_code == 201:
    print("✓ Lectura enviada exitosamente")
    print(response.json())
else:
    print("✗ Error:", response.status_code, response.text)
```

### Arduino/ESP32 (C++)

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// Configuración WiFi
const char* ssid = "TU_RED_WIFI";
const char* password = "TU_PASSWORD_WIFI";
const char* serverUrl = "http://192.168.1.100:5000/api/v1/lecturas";
const char* deviceToken = "tu-token-api-aqui";

WiFiClient client;
HTTPClient http;

void setup() {
    Serial.begin(115200);
    WiFi.begin(ssid, password);
    
    // Esperar conexión WiFi
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("WiFi conectado");
}

void enviarLectura(float voltaje, float corriente, float potencia, float consumo) {
    // Crear JSON
    DynamicJsonDocument doc(200);
    doc["voltaje"] = voltaje;
    doc["corriente"] = corriente;
    doc["potencia"] = potencia;
    doc["consumo"] = consumo;
    doc["frecuencia"] = 50;
    doc["factor_potencia"] = 0.95;
    
    // Serializar
    String json;
    serializeJson(doc, json);
    
    // Enviar HTTP POST
    http.begin(client, serverUrl);
    http.addHeader("Authorization", String("Bearer ") + deviceToken);
    http.addHeader("Content-Type", "application/json");
    
    int httpCode = http.POST(json);
    
    if (httpCode == 201) {
        Serial.println("✓ Lectura enviada");
    } else {
        Serial.print("✗ Error: ");
        Serial.println(httpCode);
    }
    
    http.end();
}

void loop() {
    // Leer sensores
    float voltaje = analogRead(A0) * (220.0 / 1023.0);  // Ejemplo
    float corriente = analogRead(A1) * (30.0 / 1023.0);  // Ejemplo
    float potencia = voltaje * corriente;
    float consumo = potencia / 1000.0 / 3600.0;  // kWh
    
    // Enviar cada 60 segundos
    enviarLectura(voltaje, corriente, potencia, consumo);
    delay(60000);
}
```

### Node.js (JavaScript)

```javascript
const http = require('http');

const options = {
    hostname: '192.168.1.100',
    port: 5000,
    path: '/api/v1/lecturas',
    method: 'POST',
    headers: {
        'Authorization': 'Bearer tu-token-api-aqui',
        'Content-Type': 'application/json'
    }
};

const lectura = {
    voltaje: 220.5,
    corriente: 5.2,
    potencia: 1100,
    consumo: 0.5,
    frecuencia: 50,
    factor_potencia: 0.95
};

const req = http.request(options, (res) => {
    console.log(`Status: ${res.statusCode}`);
    
    let data = '';
    res.on('data', (chunk) => {
        data += chunk;
    });
    
    res.on('end', () => {
        console.log('Respuesta:', JSON.parse(data));
    });
});

req.on('error', (error) => {
    console.error('Error:', error);
});

req.write(JSON.stringify(lectura));
req.end();
```

### cURL (Terminal)

```bash
#!/bin/bash

# Variables
SERVER="http://192.168.1.100:5000"
TOKEN="tu-token-api-aqui"

# Datos
DATA='{
  "voltaje": 220.5,
  "corriente": 5.2,
  "potencia": 1100,
  "consumo": 0.5,
  "frecuencia": 50,
  "factor_potencia": 0.95
}'

# Enviar
curl -X POST "$SERVER/api/v1/lecturas" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$DATA"
```

## Campos de Lectura

| Campo | Tipo | Rango | Descripción |
|-------|------|-------|-------------|
| `voltaje` | Float | 0-500 V | Voltaje instantáneo |
| `corriente` | Float | 0-100 A | Corriente instantánea |
| `potencia` | Float | 0+ W | Potencia activa |
| `consumo` | Float | 0+ kWh | Energía acumulada |
| `frecuencia` | Float | 40-60 Hz | Frecuencia de red |
| `factor_potencia` | Float | 0-1 | Factor de potencia |

## Respuestas de API

### Éxito (201)

```json
{
    "success": true,
    "lectura_id": 12345,
    "mensaje": "Lectura guardada exitosamente"
}
```

### Error (400)

```json
{
    "error": "Campo requerido: voltaje"
}
```

### No Autorizado (401)

```json
{
    "error": "Token inválido"
}
```

## Patrones de Envío

### Envío Periódico

Enviar cada 60 segundos (recomendado):

```python
import time
import requests

while True:
    enviar_lectura()
    time.sleep(60)  # Esperar 60 segundos
```

### Envío por Cambio

Enviar solo si hay cambio significativo:

```python
lectura_anterior = None

while True:
    lectura_actual = leer_sensores()
    
    # Enviar si hay cambio > 10%
    if not lectura_anterior or \
       abs(lectura_actual - lectura_anterior) / lectura_anterior > 0.1:
        enviar_lectura(lectura_actual)
        lectura_anterior = lectura_actual
    
    time.sleep(10)
```

### Envío en Lote

Enviar múltiples lecturas:

```python
lecturas = [
    {"voltaje": 220, "corriente": 5, ...},
    {"voltaje": 221, "corriente": 5.1, ...},
    {"voltaje": 219, "corriente": 4.9, ...},
]

for lectura in lecturas:
    enviar_lectura(lectura)
    time.sleep(1)  # Espaciado entre envíos
```

## Manejo de Errores

```python
try:
    response = requests.post(
        f"{SERVER}/api/v1/lecturas",
        json=lectura,
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 201:
        print("Éxito")
    elif response.status_code == 401:
        print("Token inválido")
    elif response.status_code == 400:
        print("Datos inválidos:", response.json()['error'])
    else:
        print(f"Error {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("No se pudo conectar al servidor")
except requests.exceptions.Timeout:
    print("Tiempo de conexión agotado")
except Exception as e:
    print(f"Error: {e}")
```

## Solución de Problemas

### Error 401: Token no válido
- Verificar que el token sea correcto
- Verificar formato: `Authorization: Bearer <token>`
- Crear nuevo dispositivo y token

### Error 400: Campo requerido
- Verificar que todos los campos estén presentes
- Verificar que sean números válidos
- Ver respuesta de error: `response.json()['error']`

### Connection Refused
- Verificar que Smart Watts esté ejecutándose
- Verificar dirección IP del servidor
- Verificar puerto (5000)
- Probar conectividad: `ping 192.168.1.100`

### Timeout
- Aumentar timeout en cliente
- Verificar latencia de red
- Reducir frecuencia de envíos

## Monitoreo

Verificar que las lecturas llegan:

1. Ir a **Dispositivos**
2. Hacer clic en el dispositivo
3. Ver **Últimas Lecturas**
4. Ver consumo en **Dashboard**

## Optimizaciones

### Compresión

```python
import gzip
import json

data = json.dumps(lectura).encode()
compressed = gzip.compress(data)

requests.post(url, data=compressed, headers={
    'Content-Encoding': 'gzip'
})
```

### Batching

Enviar 10 lecturas cada 10 minutos en lugar de 1 cada minuto:

```python
import time
import requests

lectura_buffer = []

while True:
    lectura_buffer.append(leer_sensores())
    
    if len(lectura_buffer) >= 10:
        for lectura in lectura_buffer:
            enviar_lectura(lectura)
        lectura_buffer = []
    
    time.sleep(60)
```

## Seguridad

- ✅ Usar HTTPS en producción
- ✅ Cambiar token si se compromete
- ✅ No compartir token públicamente
- ✅ Usar contraseña fuerte en Smart Watts

## Apoyo

¿Necesitas ayuda?

- 📖 Ver README.md
- 🐛 Reportar en Issues
- 📧 Contactar: support@smartwatts.local

¡Feliz integración! 🚀
