from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from django.test import TestCase, TransactionTestCase
from unittest.mock import Mock
from manufacturing.permissions import CanOnlyCreateAssignedPart, PartIsNotUsedInOtherAircraft, PartBelongsToAircraftType
from manufacturing.models import Aircraft, Part, Team, AircraftPart


class CanOnlyCreateAssignedPartTests(TestCase):
    def setUp(self):
        # Given: Setup mock data and initialize permission class
        self.permission = CanOnlyCreateAssignedPart()
        self.aircraft = Aircraft.objects.create(name="TB2")
        self.team = Team.objects.create(name='Wing Team')

    def test_team_can_create_assigned_part(self):
        # Given: A request with a part that the team is authorized to create
        request = Mock()
        request.data = {'name': 'WING', 'team': self.team.id}
        view = Mock(action='create')

        # When: Checking if the team has permission to create the part
        result = self.permission.has_permission(request, view)

        # Then: Permission should be granted
        self.assertTrue(result)

    def test_team_cannot_create_unassigned_part(self):
        # Given: A request with a part that the team is not authorized to create
        request = Mock()
        request.data = {'name': 'BODY', 'team': self.team.id}
        view = Mock(action='create')

        # When: Checking if the team has permission to create the part
        result = self.permission.has_permission(request, view)

        # Then: Permission should be denied
        self.assertFalse(result)


class PartIsNotUsedInOtherAircraftTests(TransactionTestCase):
    def setUp(self):
        # Given: Initialize permission class and setup test data
        self.permission = PartIsNotUsedInOtherAircraft()
        self.aircraft = Aircraft.objects.create(name="TB2", serial_number='123e4567-e89b-12d3-a456-426614174000')
        self.team = Team.objects.create(name='Wing Team')
        self.part = Part.objects.create(name='WING', aircraft_type=self.aircraft.name)
        self.aircraft_part = AircraftPart.objects.create(aircraft=self.aircraft, part=self.part)

    def test_part_is_not_used_in_another_aircraft(self):
        # Given: A new part that is not used in any other aircraft
        new_part = Part.objects.create(name='BODY', aircraft_type=self.aircraft.name)
        request = Mock()
        request.data = {'part': new_part.id}
        view = Mock(action='create')

        # When: Checking if the part can be used in an aircraft
        result = self.permission.has_permission(request, view)

        # Then: Permission should be granted as the part is not used elsewhere
        self.assertTrue(result)

    def test_part_already_used_in_another_aircraft(self):
        # Given: A part already used in another aircraft
        new_aircraft = Aircraft.objects.create(name='TB3')

        # When: Attempting to reuse the part in another aircraft, a ValidationError is expected
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                aircraft_part = AircraftPart(aircraft=new_aircraft, part=self.part)
                aircraft_part.clean()  # ValidationError expected
                aircraft_part.save()

        # Given: Reuse the part in the permission check request
        request = Mock()
        request.data = {'part': self.part.id}
        view = Mock(action='create')

        # When: Checking if the part can be reused in another aircraft
        result = self.permission.has_permission(request, view)

        # Then: Permission should be denied as the part is already in use
        self.assertFalse(result)


class PartBelongsToAircraftTypeTests(TestCase):
    def setUp(self):
        # Given: Initialize permission class and create necessary mock data
        self.permission = PartBelongsToAircraftType()
        self.aircraft = Aircraft.objects.create(name="TB2", serial_number='123e4567-e89b-12d3-a456-426614174000')
        self.team = Team.objects.create(name='Wing Team')
        self.part = Part.objects.create(name='WING', aircraft_type=self.aircraft.name)

    def test_part_belongs_to_correct_aircraft(self):
        # Given: A request with a part that belongs to the correct aircraft type
        request = Mock()
        request.data = {'part': self.part.id, 'aircraft': self.aircraft.id}
        view = Mock(action='create')

        # When: Checking if the part can be used for the specified aircraft
        result = self.permission.has_permission(request, view)

        # Then: Permission should be granted as the part matches the aircraft type
        self.assertTrue(result)

    def test_part_does_not_belong_to_aircraft_type(self):
        # Given: A request with a part that does not belong to the specified aircraft type
        new_aircraft = Aircraft.objects.create(name='TB3')
        request = Mock()
        request.data = {'part': self.part.id, 'aircraft': new_aircraft.id}
        view = Mock(action='create')

        # When: Checking if the part can be used for the specified aircraft
        result = self.permission.has_permission(request, view)

        # Then: Permission should be denied as the part does not match the aircraft type
        self.assertFalse(result)
