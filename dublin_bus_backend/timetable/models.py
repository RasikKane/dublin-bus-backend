from django.db import models


# Create your models here.
class Timetable(models.Model):
    stop_id = models.ForeignKey('bus_stops.BusStops', db_column='stop_id', on_delete=models.PROTECT)
    line_id = models.CharField(max_length=10, blank=False)
    direction = models.IntegerField(blank=False)
    program_number = models.IntegerField(blank=False)
    planned_arrival = models.IntegerField(blank=False)

    class Meta:
        managed = True
        db_table = 'timetable'
        unique_together = (('line_id', 'direction', 'program_number', 'planned_arrival', 'stop_id'),)
        indexes = [models.Index(fields=['stop_id', 'line_id', 'direction', 'program_number', 'planned_arrival']),]
