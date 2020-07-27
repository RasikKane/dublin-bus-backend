from django.db import models


# Create your models here.
class BusStops(models.Model):
    stop_id = models.IntegerField(primary_key=True)
    stop_name = models.CharField(max_length=50, blank=False)
    stop_lat = models.CharField(max_length=15, blank=False)
    stop_lng = models.CharField(max_length=15, blank=False)

    class Meta:
        db_table = 'bus_stops'
        indexes = [models.Index(fields=['stop_id', 'stop_name', 'stop_lat', 'stop_lng']),]
