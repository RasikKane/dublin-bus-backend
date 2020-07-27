# Generated by Django 3.0.7 on 2020-07-27 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('routes_history', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='routeshistory',
            index=models.Index(fields=['user_id', 'route', 'direction', 'start_stop_id', 'start_program_number', 'dest_stop_id', 'dest_program_number', 'date_created', 'date_updated'], name='routes_hist_user_id_9e0e1f_idx'),
        ),
    ]
