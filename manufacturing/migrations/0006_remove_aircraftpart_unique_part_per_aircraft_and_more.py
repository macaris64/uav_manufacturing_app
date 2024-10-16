# Generated by Django 4.2.5 on 2024-10-11 23:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manufacturing', '0005_remove_part_aircraft_part_aircraft_type'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='aircraftpart',
            name='unique_part_per_aircraft',
        ),
        migrations.AddField(
            model_name='aircraft',
            name='is_produced',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AddConstraint(
            model_name='aircraftpart',
            constraint=models.UniqueConstraint(fields=('part', 'aircraft'), name='unique_part_per_aircraft'),
        ),
    ]
