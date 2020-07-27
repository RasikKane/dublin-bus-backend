from django.db import models


# Create your models here.
class LinesRouteID(models.Model):
    direction = models.IntegerField(blank=False)
    line_id = models.CharField(max_length=10, blank=False)
    route_id = models.CharField(max_length=10, blank=False)

    class Meta:
        managed = True
        db_table = 'lines_routeids'
        unique_together = (('line_id', 'direction'),)
        indexes = [models.Index(fields=['direction', 'line_id', 'route_id']),]
