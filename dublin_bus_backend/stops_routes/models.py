from django.db import models


# Create your models here.
class StopsRoutes(models.Model):
    stop_id = models.ForeignKey('bus_stops.BusStops', db_column='stop_id', on_delete=models.PROTECT)
    route = models.CharField(max_length=10, blank=False)
    program_number = models.IntegerField(blank=False)
    direction = models.IntegerField(blank=False)

    class Meta:
        managed = True
        db_table = 'stops_routes'
        unique_together = (('route', 'stop_id','direction'),)
        indexes = [models.Index(fields=['stop_id', 'route', 'program_number', 'direction']),]

