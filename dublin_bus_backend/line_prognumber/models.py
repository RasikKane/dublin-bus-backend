from django.db import models


# Create your models here.
class LinesPrognumbers(models.Model):
    line_id = models.CharField(max_length=10, blank=False)
    direction = models.IntegerField(blank=False)
    first_program_number = models.IntegerField(blank=False)
    last_program_number = models.IntegerField(blank=False)

    class Meta:
        managed = True
        db_table = 'lines_prognumbers'
        unique_together = (('line_id', 'direction'),)
        indexes = [models.Index(fields=['line_id', 'direction', 'first_program_number', 'last_program_number']),]
