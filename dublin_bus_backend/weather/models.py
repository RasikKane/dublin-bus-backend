from django.db import models


# Create your models here.
class Weather(models.Model):
    date_entry = models.CharField(max_length=10, blank=False)
    hour_Day = models.IntegerField(blank=False)
    feels_like = models.CharField(max_length=5, blank=False)
    wind_speed = models.CharField(max_length=5, blank=False)
    weather_id = models.CharField(max_length=5, blank=False)

    class Meta:
        managed = True
        db_table = 'weather'
        unique_together = (('date_entry', 'hour_Day'),)
        indexes = [models.Index(fields=['date_entry', 'hour_Day', 'feels_like', 'wind_speed', 'weather_id']),]

