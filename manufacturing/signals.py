# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from manufacturing.models import AircraftPart

@receiver(post_save, sender=AircraftPart)
def update_aircraft_production_status(sender, instance, **kwargs):
    # Updates the production status of the related aircraft when a new part is added
    instance.aircraft.check_production_status()
