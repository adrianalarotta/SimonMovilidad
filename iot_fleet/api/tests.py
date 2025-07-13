from django.test import TestCase, RequestFactory
from django.http import JsonResponse
from datetime import datetime, timedelta
import time
import json
import base64
import hmac
import hashlib
from django.contrib.auth.models import User
from django.urls import reverse
from api.auth import generate_jwt
from api.models import SensorData
import time


from .auth import verify_jwt, generate_jwt, jwt_required, SECRET_KEY

# -----------------------------
# TESTS PARA COMBUSTIBLE
# -----------------------------

class CombustibleTestCase(TestCase):
    def test_alerta_bajo_combustible(self):
        consumo_lph = 10.0
        fuel_bajo = 5.0
        fuel_alto = 20.0

        autonomia_baja = fuel_bajo / consumo_lph
        autonomia_alta = fuel_alto / consumo_lph

        self.assertTrue(autonomia_baja < 1)
        self.assertFalse(autonomia_alta < 1)


# -----------------------------
#  TESTS PARA JWT
# -----------------------------

class JWTAuthTestCase(TestCase):
    def setUp(self):
        self.payload = {
            'user_id': 123,
            'role': 'admin',
            'exp': int(time.time()) + 3600,
            'iat': int(time.time())
        }
        self.token = generate_jwt(self.payload)

    def test_token_valido(self):
        payload, error = verify_jwt(self.token)
        self.assertIsNone(error)
        self.assertEqual(payload['user_id'], self.payload['user_id'])

    def test_token_firma_invalida(self):
        # Manipulamos la firma para invalidarla
        partes = self.token.split('.')
        token_mal = f"{partes[0]}.{partes[1]}.firma_invalida"

        payload, error = verify_jwt(token_mal)
        self.assertIsNone(payload)
        self.assertEqual(error, "Firma inválida")

    def test_token_expirado(self):
        expired_payload = {
            'user_id': 456,
            'role': 'admin',
            'exp': int(time.time()) - 10,  # 10 segundos en el pasado
            'iat': int(time.time()) - 20
        }
        expired_token = generate_jwt(expired_payload)

        payload, error = verify_jwt(expired_token)
        self.assertIsNone(payload)
        self.assertEqual(error, "Token expirado")


# -----------------------------
# TEST PARA DECORADOR jwt_required
# -----------------------------

class JWTRequiredDecoratorTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.payload = {
            'user_id': 1,
            'role': 'admin',
            'exp': int(time.time()) + 3600,
            'iat': int(time.time())
        }
        self.token = generate_jwt(self.payload)

    def dummy_view(self, request):
        return JsonResponse({'ok': True, 'user_id': request.user_id})

    def test_decorador_jwt_valido(self):
        request = self.factory.get('/dummy')
        request.headers = {'Authorization': f'Bearer {self.token}'}

        view = jwt_required(self.dummy_view)
        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'ok': True, 'user_id': 1})

    def test_decorador_jwt_faltante(self):
        request = self.factory.get('/dummy')
        request.headers = {}

        view = jwt_required(self.dummy_view)
        response = view(request)

        self.assertEqual(response.status_code, 401)
        self.assertIn('Token requerido', response.content.decode())

    def test_decorador_jwt_invalido(self):
        request = self.factory.get('/dummy')
        # Creamos un token válido
        token_parts = generate_jwt(self.payload).split('.')
       
        token_mal_firmado = f"{token_parts[0]}.{token_parts[1]}.firma_invalida"

        request.headers = {'Authorization': f'Bearer {token_mal_firmado}'}

        view = jwt_required(self.dummy_view)
        response = view(request)

        self.assertEqual(response.status_code, 401)
        error_msg = json.loads(response.content.decode())['error']
        self.assertIn('Firma inválida', error_msg)

