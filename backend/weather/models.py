# weather/models.py
from django.db import models

class Station(models.Model):
    name = models.CharField(max_length=128)
    lat = models.FloatField()
    lon = models.FloatField()
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class WeatherLog(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='logs')
    timestamp = models.DateTimeField()
    temp_c = models.FloatField()
    rainfall_mm = models.FloatField(null=True, blank=True)
    wind_mps = models.FloatField(null=True, blank=True)
    pop = models.FloatField(null=True, blank=True)  # probability of precipitation 0..1

    class Meta:
        ordering = ['-timestamp']
