import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.utils.timezone import now
from .models import SensorData
from django.contrib.auth.models import User
from django.core.serializers import serialize
from django.forms.models import model_to_dict
from django.utils.timezone import now, timedelta
from .auth import jwt_required
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.views.decorators.csrf import csrf_exempt
from .auth import generate_jwt
import time 

SECRET_KEY = 'clave-secreta-supersegura'  # puedes mover esto a settings.py luego

@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user = authenticate(username=data.get('username'), password=data.get('password'))

        if user is not None:
            payload = {
                'user_id': user.id,
                'role': user.role,
                'exp': int(time.time()) + 2 * 3600,
                'iat': int(time.time())
            }

            token = generate_jwt(payload)

            return JsonResponse({'token': token, 'role': user.role})
        return JsonResponse({'error': 'Credenciales inválidas'}, status=401)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
@jwt_required
def ingest_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Guardar los datos primero
            sensor = SensorData.objects.create(
                vehicle_id = data['vehicle_id'],
                gps_lat = data['gps_lat'],
                gps_lon = data['gps_lon'],
                fuel_level = data['fuel_level'],
                temperature = data['temperature']
            )

            # Enviar mensaje por WebSocket DESPUÉS de crear el sensor
            layer = get_channel_layer()
            async_to_sync(layer.group_send)(
                "ubicacion",
                {
                    "type": "enviar_ubicacion",
                    "data": {
                        "vehicle_id": sensor.vehicle_id,
                        "gps_lat": sensor.gps_lat,
                        "gps_lon": sensor.gps_lon,
                        "fuel_level": sensor.fuel_level,
                        "timestamp": str(sensor.timestamp)
                    }
                }
            )

            # Alerta por bajo combustible
            alerta = check_low_fuel(sensor.fuel_level)

            return JsonResponse({
                'status': 'ok',
                'alerta_bajo_combustible': alerta
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

# Lógica para predecir si queda < 1 hora de autonomía
def check_low_fuel(fuel_level):
    consumo_por_hora = 5  # litros por hora (ejemplo)
    return fuel_level < consumo_por_hora


def is_admin(user_id):
    try:
        user = User.objects.get(id=user_id)
        return user.is_superuser or user.is_staff
    except User.DoesNotExist:
        return False
    
def mask_id(vid):
    return vid[:3] + "-****-" + vid[-4:]


@csrf_exempt
@jwt_required
def sensor_history(request):
    if request.method == 'GET':
        last_hours = int(request.GET.get('hours', 1))
        since = now() - timedelta(hours=last_hours)
        data = SensorData.objects.filter(timestamp__gte=since).order_by('-timestamp')[:100]

        result = []
        for row in data:
            result.append({
                "vehicle_id": row.vehicle_id if is_admin(request.user_id) else mask_id(row.vehicle_id),
                "gps_lat": row.gps_lat,
                "gps_lon": row.gps_lon,
                "fuel_level": row.fuel_level,
                "temperature": row.temperature,
                "timestamp": row.timestamp
            })
        return JsonResponse(result, safe=False)
    
@csrf_exempt
@jwt_required
def active_alerts(request):
    if request.method == 'GET':
        low_fuel_records = SensorData.objects.filter(fuel_level__lt=5).order_by('-timestamp')[:50]
        result = []
        for row in low_fuel_records:
            result.append({
                "vehicle_id": row.vehicle_id if is_admin(request.user_id) else mask_id(row.vehicle_id),
                "fuel_level": row.fuel_level,
                "timestamp": row.timestamp
            })
        return JsonResponse(result, safe=False)

@csrf_exempt
def historico(request):
    data = {}

    dispositivos = SensorData.objects.values_list('vehicle_id', flat=True).distinct()

    for device_id in dispositivos:
        registros = (
            SensorData.objects
            .filter(vehicle_id=device_id)
            .order_by('-timestamp')[:10]
            .values('timestamp', 'temperature', 'fuel_level')  
        )
        data[device_id] = list(registros)[::-1]  # Invertir para que esté en orden ascendente

    return JsonResponse(data)