from django.contrib.auth.models import AbstractUser
from django.db import models

class SensorData(models.Model):
    vehicle_id = models.CharField(max_length=20)
    gps_lat = models.FloatField()
    gps_lon = models.FloatField()
    fuel_level = models.FloatField()
    temperature = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vehicle_id} - {self.timestamp}"
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return self.username