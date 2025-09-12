# alerts/utils.py
from django.conf import settings
from django.core.mail import send_mail
import requests

def send_email_alert(user, subject, message):
    if not user.email:
        return False
    from_email = settings.EMAIL_HOST_USER
    send_mail(subject, message, from_email, [user.email], fail_silently=False)
    return True

def send_telegram_message(chat_id, text):
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", None)
    if not token or not chat_id:
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    resp = requests.post(url, data={"chat_id": chat_id, "text": text})
    return resp.status_code == 200

def send_alert_to_user(user, station, weather_log, reason):
    subject = f"[RainSafe CMU] Alert for {station.name}"
    message = (
        f"Alert for station {station.name} at {weather_log.timestamp} UTC\n"
        f"Temp: {weather_log.temp_c} °C\n"
        f"Rain(mm): {weather_log.rainfall_mm}\n"
        f"Wind(m/s): {weather_log.wind_mps}\n"
        f"Reason: {reason}\n"
    )
    # Try email
    try:
        send_email_alert(user, subject, message)
    except Exception:
        # log but don't crash
        pass
    # Try Telegram
    if user.telegram_chat_id:
        send_telegram_message(user.telegram_chat_id, message)
