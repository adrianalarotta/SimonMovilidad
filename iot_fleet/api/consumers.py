import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import SensorData
from asgiref.sync import sync_to_async
from datetime import datetime

class UbicacionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("ubicacion", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("ubicacion", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        print("Recibido del cliente:", data)

        # 🔢 Extrae y convierte
        fuel_level = data.get("fuel_level", 0.0)
        timestamp_str = data.get("timestamp")
        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00")) if timestamp_str else None

        # Cálculo predictivo: alerta si queda < 1 hora de autonomía
        #consumo de 10 litros/hora
        CONSUMO_PROMEDIO_LPH = 10.0
        autonomia_horas = fuel_level / CONSUMO_PROMEDIO_LPH if fuel_level else 0
        alerta_combustible = autonomia_horas < 1

        #guardar en base de datos
        await sync_to_async(SensorData.objects.create)(
            vehicle_id=data.get("device_id", "UNKNOWN"),
            gps_lat=data.get("lat", 0.0),
            gps_lon=data.get("lon", 0.0),
            fuel_level=fuel_level,
            temperature=data.get("temperature", 0.0),
            timestamp=timestamp,
        )

        #difundir a los clientes
        await self.channel_layer.group_send(
            "ubicacion",
            {
                "type": "enviar_ubicacion",
                "data": {
                    "device_id": data.get("device_id", "UNKNOWN"),
                    "lat": data.get("lat"),
                    "lon": data.get("lon"),
                    "timestamp": timestamp_str,
                    "fuel_level": fuel_level,
                    "temperature": data.get("temperature"),
                    "alerta_combustible": alerta_combustible,
                    "autonomia_horas": round(autonomia_horas, 2)
                }
            }
        )

    async def enviar_ubicacion(self, event):
        print("Enviando a clientes:", event["data"])
        await self.send(text_data=json.dumps(event["data"]))
