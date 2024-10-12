from collections import OrderedDict

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
    """
    Tests for the AircraftSerializer.
    Verifies the serialization and deserialization of Aircraft objects.
    """

    def setUp(self):
        # Given: An Aircraft object with a unique name
        self.aircraft_data = {'name': 'TB2', 'serial_number': '123e4567-e89b-12d3-a456-426614174000'}
        self.aircraft = Aircraft.objects.create(**self.aircraft_data)

    def test_aircraft_serialization(self):
        """
        Test that the Aircraft object is serialized correctly.
        """
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
        """
        Test that new Aircraft data is deserialized correctly into an object.
        """
        # Given: A new Aircraft object with a unique name for deserialization
        unique_aircraft_data = {'name': 'TB3', 'serial_number': '123e4567-e89b-12d3-a456-426614174001'}

        # When: Deserializing the data into an Aircraft object
        serializer = AircraftSerializer(data=unique_aircraft_data)

        # Then: The serializer should be valid, and the object should be saved correctly
        self.assertTrue(serializer.is_valid(), serializer.errors)
        aircraft = serializer.save()
        self.assertEqual(aircraft.name, 'TB3')


class TeamSerializerTests(TestCase):
    """
    Tests for the TeamSerializer.
    Verifies the serialization and deserialization of Team objects.
    """

    @classmethod
    def setUpTestData(cls):
        # Given: An Aircraft and a Team object for testing
        cls.aircraft = Aircraft.objects.create(name='TB2', serial_number='123e4567-e89b-12d3-a456-426614174000')
        cls.part = Part.objects.create(name='BODY', aircraft_type=cls.aircraft.name)
        cls.team_data = {
            'name': 'Body Team',
            'description': 'Responsible for body parts'
        }
        cls.team, _ = Team.objects.get_or_create(name='Wing Team', description='Responsible for wing parts')

    def test_team_serialization(self):
        """
        Test that the Team object is serialized correctly.
        """
        # When: Serializing the Team object
        serializer = TeamSerializer(self.team)

        # Then: The serialized data should match the object data
        self.assertEqual(serializer.data, {
            'id': self.team.id,
            'name': 'Wing Team',
            'description': 'Responsible for wing parts',
        })

    def test_team_deserialization(self):
        """
        Test that new Team data is deserialized correctly into an object.
        """
        # When: Deserializing data into a Team object
        serializer = TeamSerializer(data=self.team_data)

        # Then: The serializer should be valid, and the object should be saved correctly
        self.assertTrue(serializer.is_valid(), serializer.errors)
        team = Team.objects.get(name=self.team_data['name'])
        self.assertEqual(team.name, 'Body Team')
        self.assertTrue(team.can_produce_part({'name': self.part.name}))


class PartSerializerTests(TestCase):
    """
    Tests for the PartSerializer.
    Verifies the serialization and deserialization of Part objects.
    """

    def setUp(self):
        # Given: An Aircraft object for Part association
        self.aircraft = Aircraft.objects.create(name='TB2', serial_number='123e4567-e89b-12d3-a456-426614174000')
        self.part = Part.objects.create(name='WING', aircraft_type=self.aircraft.name)
        self.team, _ = Team.objects.get_or_create(name=Team.WING_TEAM, description="Responsible for wing parts")

        self.part_data = {'name': 'WING', 'aircraft_type': self.aircraft.name}

    def test_part_serialization(self):
        """
        Test that the Part object is serialized correctly.
        """
        # When: Creating and serializing the Part object
        serializer = PartSerializer(self.part)

        # Then: The serialized data should match the object data
        self.assertEqual(serializer.data, {
            'id': self.part.id,
            'name': 'WING',
            'aircraft_type': self.aircraft.name,
            'created_at': self.part.created_at.strftime('%Y-%m-%d'),
            'is_used': False,
        })

    def test_part_deserialization(self):
        """
        Test that new Part data is deserialized correctly into an object.
        """
        # When: Deserializing data into a Part object
        serializer = PartSerializer(data=self.part_data)

        # Then: The serializer should be valid, and the object should be saved correctly
        self.assertTrue(serializer.is_valid(), serializer.errors)
        part = serializer.save()
        self.assertEqual(part.name, 'WING')
        self.assertEqual(part.aircraft_type, self.aircraft.name)

        # Check if the team can produce this part
        can_produce = self.team.can_produce_part({'name': part.name})
        self.assertTrue(can_produce)


class PersonnelSerializerTests(TestCase):
    """
    Tests for the PersonnelSerializer.
    Verifies the serialization and deserialization of Personnel objects.
    """

    def setUp(self):
        # Given: A User and a Team object for Personnel association
        self.team, _ = Team.objects.get_or_create(name=Team.WING_TEAM, description="Responsible for wing parts")
        self.user = User.objects.create_user(username='johndoe', password='password123')
        self.personnel_data = {
            'user': self.user.id,
            'team': self.team.id,
            'role': 'Engineer'
        }

    def test_personnel_serialization(self):
        """
        Test that the Personnel object is serialized correctly.
        """
        personnel = Personnel.objects.create(user=self.user, team=self.team, role='Engineer')
        serializer = PersonnelSerializer(personnel)

        expected_data = {
            'id': personnel.id,
            'user': self.user.id,
            'team': OrderedDict([
                ('id', self.team.id),
                ('name', self.team.name),
                ('description', self.team.description)
            ]),
            'role': 'Engineer'
        }

        self.assertEqual(serializer.data, expected_data)

    def test_personnel_deserialization(self):
        """
        Test that new Personnel data is deserialized correctly into an object.
        """
        # When: Deserializing data into a Personnel object
        serializer = PersonnelSerializer(data=self.personnel_data)

        # Then: The serializer should be valid, and the object should be saved correctly
        self.assertTrue(serializer.is_valid(), serializer.errors)
        personnel = Personnel.objects.create(user=self.user, team=self.team, role='Engineer')

        self.assertEqual(personnel.user, self.user)
        self.assertEqual(personnel.team, self.team)
        self.assertEqual(personnel.role, 'Engineer')


class AircraftPartSerializerTests(TestCase):
    """
    Tests for the AircraftPartSerializer.
    Verifies the serialization and deserialization of AircraftPart objects.
    """

    def setUp(self):
        # Given: Aircraft, Team, and Part objects for AircraftPart association
        self.aircraft = Aircraft.objects.create(name='TB2', serial_number='123e4567-e89b-12d3-a456-426614174000')
        self.part = Part.objects.create(name='WING', aircraft_type=self.aircraft.name)
        self.aircraft_part_data = {'aircraft': self.aircraft.id, 'part': self.part.id}

    def test_aircraft_part_serialization(self):
        """
        Test that the AircraftPart object is serialized correctly.
        """
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
        """
        Test that new AircraftPart data is deserialized correctly into an object.
        """
        # When: Deserializing data into an AircraftPart object
        serializer = AircraftPartSerializer(data=self.aircraft_part_data)

        # Then: The serializer should be valid, and the object should be saved correctly
        self.assertTrue(serializer.is_valid(), serializer.errors)
        aircraft_part = serializer.save()
        self.assertEqual(aircraft_part.aircraft, self.aircraft)
        self.assertEqual(aircraft_part.part, self.part)
