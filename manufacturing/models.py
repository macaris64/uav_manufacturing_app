import uuid

from django.db import models

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

    def __str__(self):
        return f"{self.name} - {self.serial_number}"


class Part(models.Model):
    WING = 'WING'
    BODY = 'BODY'
    TAIL = 'TAIL'
    AVIONICS = 'AVIONICS'
    PART_TYPES = [
        (WING, 'Wing'),
        (BODY, 'Body'),
        (TAIL, 'Tail'),
        (AVIONICS, 'Avionics'),
    ]

    name = models.CharField(max_length=50, choices=PART_TYPES)
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.aircraft.name}"


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
    name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name='personnel')
    role = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class AircraftPart(models.Model):
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE)
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    assembled_at = models.DateField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['part'], name='unique_part_per_aircraft')
        ]

    def __str__(self):
        return f"{self.aircraft.name} - {self.part.name}"
