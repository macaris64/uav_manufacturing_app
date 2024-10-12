from django.db import migrations

def create_teams(apps, schema_editor):
    Team = apps.get_model('manufacturing', 'Team')
    teams = [
        ('Wing Team', 'Responsible for wing parts'),
        ('Body Team', 'Responsible for body parts'),
        ('Tail Team', 'Responsible for tail parts'),
        ('Avionics Team', 'Responsible for avionics parts'),
        ('Assembly Team', 'Only assembles parts, cannot produce parts'),
    ]
    for name, description in teams:
        Team.objects.get_or_create(name=name, description=description)

class Migration(migrations.Migration):

    dependencies = [
        ('manufacturing', '0009_part_is_used'),
    ]

    operations = [
        migrations.RunPython(create_teams),
    ]
