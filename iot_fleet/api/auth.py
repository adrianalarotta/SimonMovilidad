import base64
import json
import hmac
import hashlib
import time
from django.http import JsonResponse
from functools import wraps

SECRET_KEY = b'clave-secreta-supersegura'

def decode_base64url(data):
    """Agrega relleno si falta y decodifica base64url"""
    rem = len(data) % 4
    if rem > 0:
        data += '=' * (4 - rem)
    return base64.urlsafe_b64decode(data)

def verify_jwt(token):
    try:
        header_b64, payload_b64, signature_b64 = token.split('.')

        signing_input = f'{header_b64}.{payload_b64}'.encode()
        expected_signature = base64.urlsafe_b64encode(
            hmac.new(SECRET_KEY, signing_input, hashlib.sha256).digest()
        ).decode().rstrip('=')

        if signature_b64 != expected_signature:
            return None, 'Firma inválida'

        payload_json = decode_base64url(payload_b64)
        payload = json.loads(payload_json)

        if 'exp' in payload and time.time() > payload['exp']:
            return None, 'Token expirado'

        return payload, None
    except Exception as e:
        return None, f'Error al verificar el token: {str(e)}'

def jwt_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Token requerido'}, status=401)

        token = auth_header.split(' ')[1]
        payload, error = verify_jwt(token)

        if error:
            return JsonResponse({'error': error}, status=401)

        request.user_id = payload['user_id']
        return view_func(request, *args, **kwargs)

    return wrapper
def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip('=')

def generate_jwt(payload: dict) -> str:
    header = {
        "alg": "HS256",
        "typ": "JWT"
    }

    header_b64 = base64url_encode(json.dumps(header).encode())
    payload_b64 = base64url_encode(json.dumps(payload).encode())

    signing_input = f"{header_b64}.{payload_b64}".encode()
    signature = hmac.new(SECRET_KEY, signing_input, hashlib.sha256).digest()
    signature_b64 = base64url_encode(signature)

    token = f"{header_b64}.{payload_b64}.{signature_b64}"
    return token