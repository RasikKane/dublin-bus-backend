from django.db import models


# Create your models here.
class Weather(models.Model):
    date_weather = models.CharField(max_length=10, blank=False)
    hour_of_day = models.IntegerField(blank=False)
    feels_like = models.CharField(max_length=5, blank=False)
    wind_speed = models.CharField(max_length=5, blank=False)
    weather_id = models.CharField(max_length=5, blank=False)
    temp = models.CharField(max_length=5, blank=False)
    temp_min = models.CharField(max_length=5, blank=False)
    temp_max = models.CharField(max_length=5, blank=False)
    humidity = models.IntegerField(blank=False, default= 100)
    weather_main = models.CharField(max_length=10, blank=False)
    weather_description = models.CharField(max_length=50, blank=False)

    class Meta:
        managed = True
        db_table = 'weather'
        unique_together = (('date_weather', 'hour_of_day'),)
        indexes = [models.Index(fields=['date_weather', 'hour_of_day', 'feels_like', 'wind_speed', 'weather_id',
                                        'temp', 'temp_min', 'temp_max', 'humidity', 'weather_main',
                                        'weather_description']
                                ),
                   ]
