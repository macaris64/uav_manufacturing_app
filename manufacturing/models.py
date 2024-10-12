import uuid

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Aircraft(models.Model):
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

    name = models.CharField(max_length=20, choices=AIRCRAFT_TYPES)
    serial_number = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateField(auto_now_add=True)
    is_produced = models.BooleanField(default=False, editable=False)

    def __str__(self):
        return f"{self.name} - {self.serial_number}"

    def check_production_status(self):
        # List of required part names
        required_part_names = {part[0] for part in Part.PART_TYPES}

        # List of current part names associated with this aircraft
        current_part_names = set(self.aircraftpart_set.values_list('part__name', flat=True))

        # Check if all required parts are present
        self.is_produced = required_part_names == current_part_names
        self.save()


class Part(models.Model):
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

    name = models.CharField(max_length=50, choices=[(WING, 'Wing'), (BODY, 'Body'), (TAIL, 'Tail'), (AVIONICS, 'Avionics')])
    aircraft_type = models.CharField(max_length=20, choices=AIRCRAFT_TYPES)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.aircraft_type}"


class Team(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    parts = models.ManyToManyField(Part, related_name='teams')

    def can_produce_part(self, part):
        return part in self.parts.all()

    def add_part(self, part):
        if self.can_produce_part(part):
            self.parts.add(part)
        else:
            raise ValueError(f"{self.name} cannot produce part {part.name}.")

    def __str__(self):
        return self.name


class Personnel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # User model ile birebir ilişki
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name='personnel')
    role = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

    @property
    def is_superuser(self):
        return self.user.is_superuser


class AircraftPart(models.Model):
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE)
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    assembled_at = models.DateField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['part'], name='unique_part_assignment'),
            models.UniqueConstraint(fields=['part', 'aircraft'], name='unique_part_per_aircraft')
        ]

    def __str__(self):
        return f"{self.aircraft.name} - {self.part.name}"

    def clean(self):
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
