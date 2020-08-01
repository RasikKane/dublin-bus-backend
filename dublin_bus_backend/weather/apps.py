from django.apps import AppConfig


class WeatherConfig(AppConfig):
    name = 'weather'

    # def ready(self):
    #     from weather import weather_cron_starter
    #     weather_cron_starter.start()
