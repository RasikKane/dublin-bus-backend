# Generated by Django 3.0.7 on 2020-07-27 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weather', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='weather',
            index=models.Index(fields=['date_entry', 'hour_Day', 'feels_like', 'wind_speed', 'weather_id'], name='weather_date_en_210a8f_idx'),
        ),
    ]