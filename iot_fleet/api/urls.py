from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login),
    path('ingest/', views.ingest_data),
    path('history/', views.sensor_history),
    path('alerts/', views.active_alerts),
    path('historico/', views.historico),
]
