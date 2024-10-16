# Generated by Django 4.2.5 on 2024-10-11 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manufacturing', '0003_aircraft_serial_number_alter_aircraft_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='part',
            name='team',
        ),
        migrations.AddField(
            model_name='team',
            name='parts',
            field=models.ManyToManyField(related_name='teams', to='manufacturing.part'),
        ),
    ]
