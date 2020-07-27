from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


# Create your models here.
class RoutesHistory(models.Model):
    user_id = models.ForeignKey(User, db_column='user_id', on_delete=models.PROTECT)
    route = models.CharField(max_length=10, blank=False)
    direction = models.IntegerField(blank=False)
    start_stop_id = models.IntegerField(blank=False)
    start_program_number = models.IntegerField(blank=False)
    dest_stop_id = models.IntegerField(blank=False)
    dest_program_number = models.IntegerField(blank=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'routes_history'
        indexes = [models.Index(fields=['user_id', 'route', 'direction', 'start_stop_id', 'start_program_number',
                                        'dest_stop_id', 'dest_program_number', 'date_created', 'date_updated']),]

