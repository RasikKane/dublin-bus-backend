# Generated by Django 3.0.7 on 2020-07-30 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weather', '0002_auto_20200730_1147'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='weather',
            name='weather_date_we_2da8c3_idx',
        ),
        migrations.RenameField(
            model_name='weather',
            old_name='hour_of_Day',
            new_name='hour_of_day',
        ),
        migrations.AlterUniqueTogether(
            name='weather',
            unique_together={('date_weather', 'hour_of_day')},
        ),
        migrations.AddIndex(
            model_name='weather',
            index=models.Index(fields=['date_weather', 'hour_of_day', 'feels_like', 'wind_speed', 'weather_id', 'temp', 'temp_min', 'temp_max', 'humidity', 'weather_main', 'weather_description'], name='weather_date_we_4d3b6e_idx'),
        ),
    ]