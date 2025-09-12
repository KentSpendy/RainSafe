# weather/management/commands/fetch_weather.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from weather.models import Station, WeatherLog
from alerts.models import AlertRule
from django.conf import settings
import requests
from django.db import transaction
from alerts.utils import send_alert_to_user

class Command(BaseCommand):
    help = "Fetch weather for all stations and evaluate alert rules."

    def handle(self, *args, **options):
        key = getattr(settings, 'OPENWEATHER_API_KEY', None)
        if not key:
            self.stdout.write(self.style.ERROR("Set OPENWEATHER_API_KEY in settings or env"))
            return

        for station in Station.objects.all():
            params = {
                'lat': station.lat,
                'lon': station.lon,
                'appid': key,
                'units': 'metric',
                'exclude': 'minutely,alerts'
            }
            # Using OneCall endpoint (classic): /data/2.5/onecall
            url = "https://api.openweathermap.org/data/2.5/onecall"
            r = requests.get(url, params=params, timeout=10)
            if r.status_code != 200:
                self.stdout.write(self.style.ERROR(f"Failed fetch for {station}: {r.text}"))
                continue
            data = r.json()

            # pick current or nearest hourly
            current = data.get('current', {})
            timestamp = timezone.datetime.fromtimestamp(current.get('dt', timezone.now().timestamp()), tz=timezone.utc)
            temp = current.get('temp')
            wind = current.get('wind_speed')
            # rainfall in 'rain' -> {'1h': value} possibly
            rainfall = None
            rain = current.get('rain')
            if isinstance(rain, dict):
                rainfall = rain.get('1h') or rain.get('3h') or 0.0

            # probability of precipitation: use hourly[0].pop if available
            pop = 0.0
            hourly = data.get('hourly', [])
            if hourly:
                pop = hourly[0].get('pop', 0.0)

            with transaction.atomic():
                w = WeatherLog.objects.create(
                    station=station,
                    timestamp=timestamp,
                    temp_c=temp or 0.0,
                    rainfall_mm=rainfall or 0.0,
                    wind_mps=wind or 0.0,
                    pop=pop
                )
                self.stdout.write(self.style.SUCCESS(f"Saved weather for {station} at {timestamp}"))
            # Evaluate alerts
            rules = AlertRule.objects.filter(station=station, is_active=True)
            for rule in rules:
                triggered = False
                reason_parts = []
                if rule.rain_probability_threshold is not None:
                    # rule stores percent (0-100) but pop is 0..1
                    if (pop * 100) >= rule.rain_probability_threshold:
                        triggered = True
                        reason_parts.append(f"rain {pop*100:.0f}% >= {rule.rain_probability_threshold}%")
                if rule.wind_speed_threshold is not None:
                    if (wind or 0.0) >= rule.wind_speed_threshold:
                        triggered = True
                        reason_parts.append(f"wind {(wind or 0.0):.1f} m/s >= {rule.wind_speed_threshold} m/s")

                if triggered:
                    reason = "; ".join(reason_parts)
                    send_alert_to_user(rule.user, station, w, reason)
                    rule.last_triggered = timezone.now()
                    rule.save()
