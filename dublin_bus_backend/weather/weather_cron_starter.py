from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from weather.weather_cron import weather_cron_job


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(weather_cron_job, 'interval', minutes=60)
    scheduler.start()
