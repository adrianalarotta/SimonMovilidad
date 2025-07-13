import asyncio
import websockets
import json
import random
import time

async def enviar_datos(device_id, lat, lon, fuel_level):
    uri = "ws://localhost:8000/ws/ubicacion/"
    async with websockets.connect(uri) as websocket:
        temperature = 25.0

        while True:
            lat += (random.random() - 0.5) * 0.001
            lon += (random.random() - 0.5) * 0.001
            fuel_level -= random.uniform(0.4, 0.6)
            temperature += random.uniform(-0.3, 0.3)
            fuel_level = max(fuel_level, 0.0)

            data = {
                "device_id": device_id,
                "lat": round(lat, 6),
                "lon": round(lon, 6),
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "fuel_level": round(fuel_level, 2),
                "temperature": round(temperature, 2)
            }

            await websocket.send(json.dumps(data))
            print(f"🚗 {device_id} ⏱ Enviado: {data}")
            await asyncio.sleep(2)

async def main():
    tasks = [
        enviar_datos("DEV-1234-XC54", 4.60971, -74.08175, 15),  
        enviar_datos("DEV-5678-YZ89", 4.61100, -74.07700, 12),  
        enviar_datos("DEV-9999-ZZ99", 4.60750, -74.08500, 10)    
    ]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
