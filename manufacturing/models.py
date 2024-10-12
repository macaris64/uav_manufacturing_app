import uuid

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Aircraft(models.Model):
    """
    Model representing an aircraft with various attributes such as name, serial number, and production status.
    """
    TB2 = 'TB2'
    TB3 = 'TB3'
    AKINCI = 'AKINCI'
    KIZILELMA = 'KIZILELMA'
    AIRCRAFT_TYPES = [
        (TB2, 'TB2'),
        (TB3, 'TB3'),
        (AKINCI, 'Akıncı'),
        (KIZILELMA, 'Kızılelma'),
    ]

    name = models.CharField(max_length=20, choices=AIRCRAFT_TYPES)  # Aircraft type name
    serial_number = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # Unique identifier
    created_at = models.DateField(auto_now_add=True)  # Date when the aircraft was created
    is_produced = models.BooleanField(default=False, editable=False)  # Indicates if the aircraft is produced

    def __str__(self):
        return f"{self.name} - {self.serial_number}"

    def check_production_status(self):
        """
        Checks if all required parts are present for the aircraft and updates the production status.
        """
        # List of required part names
        required_part_names = {part[0] for part in Part.PART_TYPES}

        # List of current part names associated with this aircraft
        current_part_names = set(self.aircraftpart_set.values_list('part__name', flat=True))

        # Check if all required parts are present
        self.is_produced = required_part_names == current_part_names
        self.save()


class Part(models.Model):
    """
    Model representing a part of an aircraft, including attributes like type and usage status.
    """
    WING = 'WING'
    BODY = 'BODY'
    TAIL = 'TAIL'
    AVIONICS = 'AVIONICS'
    AIRCRAFT_TYPES = [
        ('AKINCI', 'AKINCI'),
        ('TB2', 'TB2'),
        ('TB3', 'TB3'),
        ('KIZILELMA', 'KIZILELMA'),
    ]
    PART_TYPES = [
        (WING, 'Wing'),
        (BODY, 'Body'),
        (TAIL, 'Tail'),
        (AVIONICS, 'Avionics'),
    ]

    name = models.CharField(max_length=50, choices=[(WING, 'Wing'), (BODY, 'Body'), (TAIL, 'Tail'), (AVIONICS, 'Avionics')])  # Part type name
    aircraft_type = models.CharField(max_length=20, choices=AIRCRAFT_TYPES)  # Associated aircraft type
    created_at = models.DateField(auto_now_add=True)  # Date when the part was created
    is_used = models.BooleanField(default=False)  # Indicates if the part is currently used

    def __str__(self):
        return f"{self.name} - {self.aircraft_type}"


class Team(models.Model):
    """
    Model representing a team responsible for producing specific aircraft parts.
    """
    WING_TEAM = 'Wing Team'
    BODY_TEAM = 'Body Team'
    TAIL_TEAM = 'Tail Team'
    AVIONICS_TEAM = 'Avionics Team'
    ASSEMBLY_TEAM = 'Assembly Team'

    TEAM_TYPES = [
        (WING_TEAM, 'Wing Team'),
        (BODY_TEAM, 'Body Team'),
        (TAIL_TEAM, 'Tail Team'),
        (AVIONICS_TEAM, 'Avionics Team'),
        (ASSEMBLY_TEAM, 'Assembly Team'),
    ]

    name = models.CharField(max_length=50, choices=TEAM_TYPES, unique=True)  # Team name
    description = models.TextField(blank=True, null=True)  # Description of the team

    def can_produce_part(self, part):
        """
        Checks if the team can produce a specified part based on its name.
        """
        part_name = part['name']  # Extract part name from the dictionary
        if self.name == self.WING_TEAM and part_name == Part.WING:
            return True
        if self.name == self.BODY_TEAM and part_name == Part.BODY:
            return True
        if self.name == self.TAIL_TEAM and part_name == Part.TAIL:
            return True
        if self.name == self.AVIONICS_TEAM and part_name == Part.AVIONICS:
            return True
        return False

    def can_attach_parts(self):
        """
        Determines if the team can attach parts (specific to assembly team).
        """
        return self.name == self.ASSEMBLY_TEAM

    def __str__(self):
        return self.name


class Personnel(models.Model):
    """
    Model representing personnel associated with a team and their roles.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # User model with a one-to-one relationship
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name='personnel')  # Team association
    role = models.CharField(max_length=100, blank=True, null=True)  # Role of the personnel

    def __str__(self):
        return f"{self.user.username} - {self.role}"

    @property
    def is_superuser(self):
        """
        Property to check if the associated user is a superuser.
        """
        return self.user.is_superuser


class AircraftPart(models.Model):
    """
    Model representing the association between an aircraft and its parts.
    """
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE)  # Association with the Aircraft
    part = models.ForeignKey(Part, on_delete=models.CASCADE)  # Association with the Part
    assembled_at = models.DateField(auto_now_add=True)  # Date when the part was assembled

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['part'], name='unique_part_assignment'),  # Prevent duplicate parts
            models.UniqueConstraint(fields=['part', 'aircraft'], name='unique_part_per_aircraft')  # Prevent duplicate parts for the same aircraft
        ]

    def save(self, *args, **kwargs):
        """
        Override the save method to mark the part as used when it is assigned.
        """
        self.part.is_used = True  # Mark part as used
        self.part.save(update_fields=['is_used'])  # Save the updated state
        super().save(*args, **kwargs)  # Call the parent class's save method

    def __str__(self):
        return f"{self.aircraft.name} - {self.part.name}"

    def clean(self):
        """
        Validates that the part is not already assigned to another aircraft and is compatible with the aircraft type.
        """
        # Check if this part is already assigned to another aircraft
        if AircraftPart.objects.filter(part=self.part).exclude(aircraft=self.aircraft).exists():
            raise ValidationError(_("This part is already assigned to another aircraft."))

        # Check if the part is compatible with the aircraft type
        if self.part.aircraft_type != self.aircraft.name:
            raise ValidationError(
                _(f"The part {self.part.name} is not compatible with the aircraft type {self.aircraft.name}.")
            )

        # Check if this aircraft already has a part of this type
        if AircraftPart.objects.filter(
                aircraft=self.aircraft,
                part__name=self.part.name  # Ensure only one part type is added
        ).exclude(id=self.id).exists():
            raise ValidationError(
                _(f"The aircraft {self.aircraft.name} already has a part of type {self.part.name}.")
            )
