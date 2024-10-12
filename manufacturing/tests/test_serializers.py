from unittest import skip

from django.contrib.auth.models import User
from django.test import TestCase
from manufacturing.models import Aircraft, Team, Part, Personnel, AircraftPart
from manufacturing.serializers import (
    AircraftSerializer,
    TeamSerializer,
    PartSerializer,
    PersonnelSerializer,
    AircraftPartSerializer
)


class AircraftSerializerTests(TestCase):
    def setUp(self):
        # Given: An Aircraft object with a unique name
        self.aircraft_data = {'name': 'TB2', 'serial_number': '123e4567-e89b-12d3-a456-426614174000'}
        self.aircraft = Aircraft.objects.create(**self.aircraft_data)

    def test_aircraft_serialization(self):
        # When: Serializing the Aircraft object
        serializer = AircraftSerializer(self.aircraft)

        # Then: The serialized data should match the original object data, including created_at
        self.assertEqual(serializer.data, {
            'id': self.aircraft.id,
            'name': 'TB2',
            'serial_number': '123e4567-e89b-12d3-a456-426614174000',
            'created_at': self.aircraft.created_at.strftime('%Y-%m-%d'),
            'is_produced': False,
        })

    def test_aircraft_deserialization(self):
        # Given: A new Aircraft object with a unique name for deserialization
        unique_aircraft_data = {'name': 'TB3', 'serial_number': '123e4567-e89b-12d3-a456-426614174001'}

        # When: Deserializing the data into an Aircraft object
        serializer = AircraftSerializer(data=unique_aircraft_data)

        # Then: The serializer should be valid, and the object should be saved correctly
        self.assertTrue(serializer.is_valid(), serializer.errors)
        aircraft = serializer.save()
        self.assertEqual(aircraft.name, 'TB3')


class TeamSerializerTests(TestCase):
    def setUp(self):
        # Given: An Aircraft to associate with Part
        self.aircraft = Aircraft.objects.create(name='TB2', serial_number='123e4567-e89b-12d3-a456-426614174000')
        self.part = Part.objects.create(name='WING', aircraft_type=self.aircraft.name)  # Use the valid aircraft
        self.team_data = {
            'name': 'Body Team',
            'description': 'Responsible for wing parts',
            'parts': [self.part.id]  # Ensure parts are included for serialization
        }
        self.team = Team.objects.create(name='Wing Team', description='Responsible for wing parts')
        self.team.parts.add(self.part)

    def test_team_serialization(self):
        # When: Serializing the Team object
        serializer = TeamSerializer(self.team)

        # Then: The serialized data should match the object data
        self.assertEqual(serializer.data, {
            'id': self.team.id,
            'name': 'Wing Team',
            'description': 'Responsible for wing parts',
            'parts': [self.part.id],  # Include parts in the serialized data
        })

    def test_team_deserialization(self):
        # When: Deserializing data into a Team object
        serializer = TeamSerializer(data=self.team_data)

        # Then: The serializer should be valid, and the object should be saved correctly
        self.assertTrue(serializer.is_valid(), serializer.errors)
        team = serializer.save()
        self.assertEqual(team.name, 'Body Team')
        self.assertIn(self.part, team.parts.all())


class PartSerializerTests(TestCase):
    def setUp(self):
        # Given: An Aircraft object for Part association
        self.aircraft = Aircraft.objects.create(name='TB2', serial_number='123e4567-e89b-12d3-a456-426614174000')
        self.part = Part.objects.create(name='WING', aircraft_type=self.aircraft.name)
        self.team = Team.objects.create(name='Wing Team')
        self.team.parts.add(self.part)
        self.part_data = {'name': 'WING', 'aircraft_type': self.aircraft.name}

    def test_part_serialization(self):
        # When: Creating and serializing the Part object
        serializer = PartSerializer(self.part)

        # Then: The serialized data should match the object data
        self.assertEqual(serializer.data, {
            'id': self.part.id,
            'name': 'WING',
            'aircraft_type': self.aircraft.name,
            'created_at': self.part.created_at.strftime('%Y-%m-%d')
        })

    def test_part_deserialization(self):
        # When: Deserializing data into a Part object
        serializer = PartSerializer(data=self.part_data)

        # Then: The serializer should be valid, and the object should be saved correctly
        self.assertTrue(serializer.is_valid(), serializer.errors)
        part = serializer.save()
        self.assertEqual(part.name, 'WING')
        self.assertEqual(part.aircraft_type, self.aircraft.name)


class PersonnelSerializerTests(TestCase):
    def setUp(self):
        # Given: A User and a Team object for Personnel association
        self.team = Team.objects.create(name='Wing Team')
        self.user = User.objects.create_user(username='johndoe', password='password123')
        self.personnel_data = {'user': self.user.id, 'team': self.team.id, 'role': 'Engineer'}

    def test_personnel_serialization(self):
        # When: Creating and serializing the Personnel object
        personnel = Personnel.objects.create(user=self.user, team=self.team, role='Engineer')
        serializer = PersonnelSerializer(personnel)

        # Then: The serialized data should match the object data exactly
        self.assertEqual(serializer.data, {
            'id': personnel.id,
            'user': self.user.id,
            'team': self.team.id,
            'role': 'Engineer'
        })

    def test_personnel_deserialization(self):
        # When: Deserializing data into a Personnel object
        serializer = PersonnelSerializer(data=self.personnel_data)

        # Then: The serializer should be valid, and the object should be saved correctly
        self.assertTrue(serializer.is_valid(), serializer.errors)
        personnel = serializer.save()
        self.assertEqual(personnel.user, self.user)
        self.assertEqual(personnel.team, self.team)
        self.assertEqual(personnel.role, 'Engineer')



class AircraftPartSerializerTests(TestCase):
    def setUp(self):
        # Given: Aircraft, Team, and Part objects for AircraftPart association
        self.aircraft = Aircraft.objects.create(name='TB2', serial_number='123e4567-e89b-12d3-a456-426614174000')
        self.team = Team.objects.create(name='Wing Team')
        self.part = Part.objects.create(name='WING', aircraft_type=self.aircraft.name)
        self.aircraft_part_data = {'aircraft': self.aircraft.id, 'part': self.part.id}

    def test_aircraft_part_serialization(self):
        # When: Creating and serializing the AircraftPart object
        aircraft_part = AircraftPart.objects.create(aircraft=self.aircraft, part=self.part)
        serializer = AircraftPartSerializer(aircraft_part)

        # Then: The serialized data should match the object data, including assembled_at
        self.assertEqual(serializer.data, {
            'id': aircraft_part.id,
            'aircraft': self.aircraft.id,
            'part': self.part.id,
            'assembled_at': aircraft_part.assembled_at.strftime('%Y-%m-%d')
        })

    def test_aircraft_part_deserialization(self):
        # When: Deserializing data into an AircraftPart object
        serializer = AircraftPartSerializer(data=self.aircraft_part_data)

        # Then: The serializer should be valid, and the object should be saved correctly
        self.assertTrue(serializer.is_valid(), serializer.errors)
        aircraft_part = serializer.save()
        self.assertEqual(aircraft_part.aircraft, self.aircraft)
        self.assertEqual(aircraft_part.part, self.part)
