# Generated by Django 3.0.7 on 2020-07-27 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stops_routes', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='stopsroutes',
            index=models.Index(fields=['stop_id', 'route', 'program_number', 'direction'], name='stops_route_stop_id_6d9d52_idx'),
        ),
    ]
