from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from manufacturing.models import AircraftPart, Personnel


@receiver(post_save, sender=AircraftPart)
def update_aircraft_production_status_on_save(sender, instance, **kwargs):
    """
    Signal receiver that updates the production status of the aircraft
    when a part is added (created or updated).
    """
    instance.aircraft.check_production_status()  # Call method to update production status


@receiver(post_delete, sender=AircraftPart)
def update_aircraft_production_status_on_delete(sender, instance, **kwargs):
    """
    Signal receiver that updates the production status of the aircraft
    when a part is removed (deleted).
    """
    instance.aircraft.check_production_status()  # Call method to update production status


@receiver(post_save, sender=User)
def create_personnel_for_superuser(sender, instance, created, **kwargs):
    """
    Signal receiver that creates a Personnel record for a superuser
    when a new User is created.
    """
    if created and instance.is_superuser:  # Check if the user is a newly created superuser
        Personnel.objects.create(user=instance, role="Superuser")  # Create Personnel for the superuser
