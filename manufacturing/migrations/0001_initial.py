# Generated by Django 4.2.5 on 2024-10-11 08:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Aircraft',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('TB2', 'TB2'), ('TB3', 'TB3'), ('AKINCI', 'Akıncı'), ('KIZILELMA', 'Kızılelma')], max_length=20, unique=True)),
                ('created_at', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Personnel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('role', models.CharField(max_length=100)),
                ('team', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='personnel', to='manufacturing.team')),
            ],
        ),
        migrations.CreateModel(
            name='Part',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('WING', 'Wing'), ('BODY', 'Body'), ('TAIL', 'Tail'), ('AVIONICS', 'Avionics')], max_length=50)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('aircraft', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manufacturing.aircraft')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parts', to='manufacturing.team')),
            ],
        ),
        migrations.CreateModel(
            name='AircraftPart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assembled_at', models.DateField(auto_now_add=True)),
                ('aircraft', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manufacturing.aircraft')),
                ('part', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manufacturing.part')),
            ],
        ),
    ]
