from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from manufacturing.models import AircraftPart

@receiver(post_save, sender=AircraftPart)
def update_aircraft_production_status_on_save(sender, instance, **kwargs):
    # Updates the production status when a part is added
    instance.aircraft.check_production_status()

@receiver(post_delete, sender=AircraftPart)
def update_aircraft_production_status_on_delete(sender, instance, **kwargs):
    # Updates the production status when a part is removed
    instance.aircraft.check_production_status()
