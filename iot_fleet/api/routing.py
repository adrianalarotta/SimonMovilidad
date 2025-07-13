from django.urls import re_path
from .consumers import UbicacionConsumer 

websocket_urlpatterns = [
    re_path(r'ws/ubicacion/$', UbicacionConsumer.as_asgi()),
]
