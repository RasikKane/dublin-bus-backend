# Generated by Django 3.0.7 on 2020-07-30 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Weather',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_entry', models.CharField(max_length=10)),
                ('hour_Day', models.IntegerField()),
                ('feels_like', models.CharField(max_length=5)),
                ('wind_speed', models.CharField(max_length=5)),
                ('weather_id', models.CharField(max_length=5)),
                ('temp', models.CharField(max_length=5)),
                ('temp_min', models.CharField(max_length=5)),
                ('temp_max', models.CharField(max_length=5)),
                ('humidity', models.IntegerField(default=100)),
                ('weather_main', models.CharField(max_length=10)),
                ('weather_description', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'weather',
                'managed': True,
            },
        ),
        migrations.AddIndex(
            model_name='weather',
            index=models.Index(fields=['date_entry', 'hour_Day', 'feels_like', 'wind_speed', 'weather_id', 'temp', 'temp_min', 'temp_max', 'humidity', 'weather_main', 'weather_description'], name='weather_date_en_cb0dff_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='weather',
            unique_together={('date_entry', 'hour_Day')},
        ),
    ]
