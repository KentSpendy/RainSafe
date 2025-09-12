from django.db import models
from django.conf import settings
from weather.models import Station

class AlertRule(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    rain_probability_threshold = models.FloatField(null=True, blank=True, help_text='0-100 percent')
    wind_speed_threshold = models.FloatField(null=True, blank=True, help_text='m/s')
    is_active = models.BooleanField(default=True)
    last_triggered = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Alert {self.id} for {self.user} @ {self.station}"
