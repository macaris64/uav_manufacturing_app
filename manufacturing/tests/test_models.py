from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from manufacturing.models import Aircraft, Team, Part, AircraftPart, Personnel


class AircraftPartModelTests(TestCase):
    """
    Tests specifically for the AircraftPart model,
    ensuring parts are assigned only to one aircraft and managed correctly.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Given: Predefined team names and descriptions.
        When: Creating teams if they do not already exist.
        """
        teams_data = [
            ('Wing Team', 'Responsible for wing parts'),
            ('Body Team', 'Responsible for body parts'),
            ('Tail Team', 'Responsible for tail parts'),
            ('Avionic Team', 'Responsible for avionic parts'),
            ('Assembly Team', 'Only assembles parts'),
        ]

        for name, description in teams_data:
            if not Team.objects.filter(name=name).exists():
                Team.objects.create(name=name, description=description)

    def setUp(self):
        """
        Given: Setup for each test that initializes an Aircraft and Parts.
        """
        self.aircraft = Aircraft.objects.create(name="TB2", serial_number='123e4567-e89b-12d3-a456-426614174000')
        self.wing_part = Part.objects.create(name='WING', aircraft_type='TB2')
        self.body_part = Part.objects.create(name='BODY', aircraft_type='TB2')

    def test_create_aircraft_part_association(self):
        """
        Test creating an association between Aircraft and Part as AircraftPart.
        """
        # Given: An Aircraft and a Part
        # When: Creating an association
        aircraft_part = AircraftPart.objects.create(aircraft=self.aircraft, part=self.wing_part)

        # Then: The association should be created successfully
        self.assertEqual(aircraft_part.aircraft, self.aircraft)
        self.assertEqual(aircraft_part.part, self.wing_part)
        self.assertEqual(AircraftPart.objects.count(), 1)

    def test_part_cannot_be_reassigned_to_another_aircraft(self):
        """
        Test that a Part cannot be reassigned to a different Aircraft.
        """
        # Given: An AircraftPart associated with the current Aircraft and Part
        AircraftPart.objects.create(aircraft=self.aircraft, part=self.wing_part)
        new_aircraft = Aircraft.objects.create(name='TB3', serial_number='123e4567-e89b-12d3-a456-426614174002')

        # When: Attempting to assign the same Part to a different Aircraft
        aircraft_part = AircraftPart(aircraft=new_aircraft, part=self.wing_part)

        # Then: A ValidationError should be raised
        with self.assertRaises(ValidationError):
            aircraft_part.clean()
            aircraft_part.save()

        self.assertEqual(AircraftPart.objects.count(), 1)

    def test_unique_part_per_aircraft(self):
        """
        Test that parts with the same name can be created for different aircraft types.
        """
        # Given: Two Aircrafts of different types
        aircraft1 = Aircraft.objects.create(name='TB2', serial_number='123e4567-e89b-12d3-a456-426614174001')
        part = Part.objects.create(name='WING', aircraft_type=self.aircraft.name)

        # When: Creating an AircraftPart association
        AircraftPart.objects.create(aircraft=aircraft1, part=part)

        # Then: An IntegrityError should be raised if trying to associate the same part with a different aircraft
        aircraft2 = Aircraft.objects.create(name='TB3', serial_number='123e4567-e89b-12d3-a456-426614174002')
        with self.assertRaises(ValidationError):
            aircraft_part = AircraftPart(aircraft=aircraft2, part=part)
            aircraft_part.clean()

    def test_part_type_constraint(self):
        """
        Test that different part types can be added to the same aircraft.
        """
        # Given: An Aircraft and a Part of a different type associated with it
        AircraftPart.objects.create(aircraft=self.aircraft, part=self.wing_part)

        # When: Adding another part type to the same aircraft
        new_aircraft_part = AircraftPart(aircraft=self.aircraft, part=self.body_part)
        new_aircraft_part.clean()  # This should not raise an error

        # Then: The new part should be allowed and saved
        new_aircraft_part.save()
        self.assertEqual(AircraftPart.objects.filter(aircraft=self.aircraft).count(), 2)

    def test_is_used_set_to_true_when_part_assigned(self):
        """
        Test that the part's is_used field is set to True when assigned to an Aircraft.
        """
        # Given: A new Part and Aircraft
        aircraft = Aircraft.objects.create(name='TB2', serial_number='123e4567-e89b-12d3-a456-426614174003')
        part = Part.objects.create(name='WING', aircraft_type=aircraft.name)

        # When: Part is assigned to an Aircraft
        AircraftPart.objects.create(aircraft=aircraft, part=part)

        # Then: The part's is_used field should be True
        part.refresh_from_db()
        self.assertTrue(part.is_used)


class AircraftModelTests(TestCase):
    """
    Tests for the Aircraft model.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Given: Predefined team names and descriptions.
        When: Creating teams if they do not already exist.
        """
        Team.objects.all().delete()
        teams_data = [
            ('Wing Team', 'Responsible for wing parts'),
            ('Body Team', 'Responsible for body parts'),
            ('Tail Team', 'Responsible for tail parts'),
            ('Avionics Team', 'Responsible for avionic parts'),
            ('Assembly Team', 'Only assembles parts'),
        ]

        for name, description in teams_data:
            Team.objects.get_or_create(name=name, description=description)

        cls.aircraft = Aircraft.objects.create(name='TB2', serial_number='123e4567-e89b-12d3-a456-426614174000')

    def test_create_aircraft(self):
        """
        Test creating a new Aircraft with a unique name.
        """
        # Given: No additional Aircraft
        # When: Creating a new Aircraft with a unique name
        new_aircraft = Aircraft.objects.create(name='TB3', serial_number='123e4567-e89b-12d3-a456-426614174001')

        # Then: The Aircraft should be created and counted correctly
        self.assertEqual(new_aircraft.name, 'TB3')
        self.assertEqual(Aircraft.objects.count(), 2)  # Including the one created in setUpTestData

    def test_update_aircraft(self):
        """
        Test updating the name of an existing Aircraft.
        """
        # Given: An existing Aircraft
        # When: Updating the Aircraft name
        self.aircraft.name = 'Updated TB2'
        self.aircraft.save()

        # Then: The updated name should be saved correctly
        updated_aircraft = Aircraft.objects.get(id=self.aircraft.id)
        self.assertEqual(updated_aircraft.name, 'Updated TB2')

    def test_aircraft_is_produced_when_all_parts_are_added(self):
        """
        Test that an aircraft is marked as produced when all required parts are added.
        """
        # Given: An aircraft and all required parts
        aircraft = Aircraft.objects.create(name='TB2', serial_number='123e4567-e89b-12d3-a456-426614174003')
        parts = [
            Part.objects.create(name=Part.WING, aircraft_type='TB2'),
            Part.objects.create(name=Part.BODY, aircraft_type='TB2'),
            Part.objects.create(name=Part.TAIL, aircraft_type='TB2'),
            Part.objects.create(name=Part.AVIONICS, aircraft_type='TB2')
        ]

        # When: Each part is added to the aircraft
        for part in parts:
            AircraftPart.objects.create(aircraft=aircraft, part=part)

        # Then: The aircraft should be marked as produced
        aircraft.refresh_from_db()
        self.assertTrue(aircraft.is_produced)

    def test_aircraft_not_produced_with_missing_parts(self):
        """
        Test that an aircraft is not marked as produced when some parts are missing.
        """
        # Given: An aircraft and some of the required parts (missing one)
        aircraft = Aircraft.objects.create(name='TB2', serial_number='123e4567-e89b-12d3-a456-426614174004')
        parts = [
            Part.objects.create(name=Part.WING, aircraft_type='TB2'),
            Part.objects.create(name=Part.BODY, aircraft_type='TB2'),
            Part.objects.create(name=Part.TAIL, aircraft_type='TB2')
            # AVIONICS part is missing
        ]

        # When: Adding only the available parts to the aircraft
        for part in parts:
            AircraftPart.objects.create(aircraft=aircraft, part=part)

        # Then: The aircraft should not be marked as produced
        aircraft.refresh_from_db()
        self.assertFalse(aircraft.is_produced)


class TeamModelTests(TestCase):
    """
    Tests for the Team model.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Given: Predefined team names and descriptions.
        When: Creating teams if they do not already exist.
        """
        Team.objects.all().delete()
        teams_data = [
            ('Wing Team', 'Responsible for wing parts'),
            ('Body Team', 'Responsible for body parts'),
            ('Tail Team', 'Responsible for tail parts'),
            ('Avionics Team', 'Responsible for avionic parts'),
            ('Assembly Team', 'Only assembles parts'),
        ]

        for name, description in teams_data:
            Team.objects.get_or_create(name=name, description=description)

        cls.aircraft = Aircraft.objects.create(name='TB2', serial_number='123e4567-e89b-12d3-a456-426614174000')
        cls.wing_team = Team.objects.get(name='Wing Team')

    def test_create_team(self):
        """
        Test creating a new Team with a unique name.
        """
        # Given: No additional Team with a unique name
        unique_team_name = 'New Unique Team'

        # When: Creating a new Team with a unique name
        new_team = Team.objects.create(name=unique_team_name)

        # Then: The Team should be created successfully and counted correctly
        self.assertEqual(new_team.name, unique_team_name)
        self.assertEqual(Team.objects.count(), 6)

    def test_unique_team_name(self):
        """
        Test that creating a team with a duplicate name raises an IntegrityError.
        """
        # Given: An existing Team with a specific name
        # When: Attempting to create another Team with the same name
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Team.objects.create(name='Wing Team')

    def test_assign_part_to_team(self):
        """
        Test that a team can produce the part it is responsible for.
        """
        # Given: An Aircraft and a Team responsible for a specific part
        wing_part = Part.objects.create(name=Part.WING, aircraft_type=self.aircraft.name)
        wing_part_dict = {'name': wing_part.name}

        # When: Checking if the team can produce the part it is responsible for
        can_produce = self.wing_team.can_produce_part(wing_part_dict)

        # Then: The team should be able to produce the part
        self.assertTrue(can_produce)

    def test_team_can_produce_assigned_part(self):
        """
        Test that a team can produce the part it is responsible for.
        """
        avionics_team = Team.objects.get(name='Avionics Team')
        avionics_part = Part.objects.create(name=Part.AVIONICS, aircraft_type=self.aircraft.name)
        avionics_part_dict = {'name': avionics_part.name}

        # When: Checking if the team can produce the part
        can_produce = avionics_team.can_produce_part(avionics_part_dict)

        # Then: The team should be able to produce the part
        self.assertTrue(can_produce)

    def test_cannot_assign_part_to_non_responsible_team(self):
        """
        Test that a team cannot produce parts it is not responsible for.
        """
        avionic_team = Team.objects.get(name='Avionics Team')
        wing_part = Part.objects.create(name=Part.WING, aircraft_type=self.aircraft.name)
        wing_part_dict = {'name': wing_part.name}

        # When: Checking if the Avionic Team can produce a Wing Part
        can_produce = avionic_team.can_produce_part(wing_part_dict)

        # Then: The Avionic Team should not be able to produce the Wing Part
        self.assertFalse(can_produce)

    def test_team_produce_part_responsibility(self):
        """
        Test that a team can produce only the part it is responsible for.
        """
        tail_team = Team.objects.get(name='Tail Team')
        tail_part = Part.objects.create(name=Part.TAIL, aircraft_type=self.aircraft.name)
        avionics_part = Part.objects.create(name=Part.AVIONICS, aircraft_type=self.aircraft.name)
        tail_part_dict = {'name': tail_part.name}
        avionics_part_dict = {'name': avionics_part.name}

        # Then: Tail team should be able to produce tail parts, but not avionics parts
        self.assertTrue(tail_team.can_produce_part(tail_part_dict))
        self.assertFalse(tail_team.can_produce_part(avionics_part_dict))

    def test_team_description(self):
        """
        Test that a newly created Team's description is set correctly.
        """
        # Given: A newly created Team with a description
        new_team = Team.objects.create(name='New Team', description='This is a new team')

        # Then: The team description should be set correctly
        self.assertEqual(new_team.description, 'This is a new team')

    def test_team_cannot_produce_non_assigned_part(self):
        """
        Test that a team cannot produce a part it is not responsible for.
        """
        avionics_team = Team.objects.get(name='Avionics Team')
        wing_part = Part.objects.create(name=Part.WING, aircraft_type=self.aircraft.name)
        wing_part_dict = {'name': wing_part.name}

        # When: Checking if the team can produce a part it should not be able to
        can_produce = avionics_team.can_produce_part(wing_part_dict)

        # Then: The team should not be able to produce the part
        self.assertFalse(can_produce)


class PartModelTests(TestCase):
    """
    Tests for the Part model.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Given: Predefined team names and descriptions.
        When: Creating teams if they do not already exist.
        """
        teams_data = [
            ('Wing Team', 'Responsible for wing parts'),
            ('Body Team', 'Responsible for body parts'),
            ('Tail Team', 'Responsible for tail parts'),
            ('Avionics Team', 'Responsible for avionic parts'),
            ('Assembly Team', 'Only assembles parts'),
        ]

        cls.teams = {}
        for name, description in teams_data:
            try:
                team, _ = Team.objects.get_or_create(name=name, description=description)
                cls.teams[name] = team
            except IntegrityError:
                cls.teams[name] = Team.objects.get(name=name)

        cls.aircraft = Aircraft.objects.create(name='TB2')

    def test_create_part(self):
        """
        Test creating a Part associated with an Aircraft type.
        """
        # Given: An Aircraft
        aircraft = Aircraft.objects.create(name='TB2', serial_number='123e4567-e89b-12d3-a456-426614174001')

        # When: Creating a Part associated with that aircraft type
        new_part = Part.objects.create(name=Part.WING, aircraft_type=aircraft.name)

        # Then: The Part should be created successfully
        self.assertEqual(new_part.name, Part.WING)
        self.assertEqual(new_part.aircraft_type, aircraft.name)
        self.assertEqual(Part.objects.count(), 1)

    def test_part_unique_per_aircraft(self):
        """
        Test that parts with the same name can be created for different aircraft types.
        """
        # Given: Two Aircrafts of different types
        aircraft_tb3 = Aircraft.objects.create(name='TB3')
        Part.objects.create(name='WING', aircraft_type=self.aircraft.name)

        # When: Creating a Part with the same name but for a different aircraft type
        new_part = Part.objects.create(name='WING', aircraft_type=aircraft_tb3.name)

        # Then: The Part should be created successfully for the new aircraft type
        self.assertEqual(Part.objects.count(), 2)
        self.assertEqual(new_part.aircraft_type, 'TB3')

    def test_part_can_be_produced_by_multiple_teams(self):
        """
        Test that a Part type can be associated with multiple responsible Teams based on the team type.
        """
        # Given: Corresponding Parts for each team type
        tail_part = Part.objects.create(name=Part.TAIL, aircraft_type=self.aircraft.name)
        avionics_part = Part.objects.create(name=Part.AVIONICS, aircraft_type=self.aircraft.name)
        tail_part_dict = {'name': tail_part.name}
        avionics_part_dict = {'name': avionics_part.name}

        # When: Checking if each team can produce its respective part
        can_tail_team_produce = self.teams['Tail Team'].can_produce_part(tail_part_dict)
        can_avionics_team_produce = self.teams['Avionics Team'].can_produce_part(avionics_part_dict)

        # Then: Each team should be able to produce its responsible part
        self.assertTrue(can_tail_team_produce)
        self.assertTrue(can_avionics_team_produce)

        # And: They should not produce parts outside of their responsibility
        self.assertFalse(self.teams['Tail Team'].can_produce_part(avionics_part_dict))
        self.assertFalse(self.teams['Avionics Team'].can_produce_part(tail_part_dict))

    def test_part_assignment_limited_to_responsible_team(self):
        """
        Test that a team can only produce parts it is responsible for.
        """
        # Given: A Tail Part
        tail_part = Part.objects.create(name=Part.TAIL, aircraft_type=self.aircraft.name)
        part_dict = {'name': tail_part.name}

        # When: Checking if the Avionics Team can produce a Tail Part
        can_produce = self.teams['Avionics Team'].can_produce_part(part_dict)

        # Then: The team should not be able to produce the part
        self.assertFalse(can_produce)

    def test_assign_responsible_part_to_team(self):
        """
        Test that a Team can produce and assign a compatible Part.
        """
        # Given: A Part the Avionics Team is responsible for
        part = Part.objects.create(name=Part.AVIONICS, aircraft_type=self.aircraft.name)
        part_dict = {'name': part.name}

        # When: Checking if the Avionics Team can produce the Avionic Part
        can_produce = self.teams['Avionics Team'].can_produce_part(part_dict)

        # Then: The team should be able to produce the part
        self.assertTrue(can_produce)
        self.assertTrue(Part.objects.filter(name=Part.AVIONICS, aircraft_type=self.aircraft.name).exists())

    def test_aircraft_part_incompatible_assignment(self):
        """
        Test that a Part cannot be assigned to an incompatible Aircraft type.
        """
        # Given: A Part created for TB2 and an Aircraft of type AKINCI
        part_tb2 = Part.objects.create(name=Part.WING, aircraft_type='TB2')
        aircraft_akinci = Aircraft.objects.create(name='AKINCI')
        aircraft_part = AircraftPart(aircraft=aircraft_akinci, part=part_tb2)

        # When/Then: Validating the assignment should raise a ValidationError
        with self.assertRaises(ValidationError):
            aircraft_part.clean()

    def test_aircraft_part_compatible_assignment(self):
        """
        Test that a compatible Part can be assigned to an Aircraft.
        """
        # Given: A Part compatible with TB2 and an Aircraft of type TB2
        part_tb2 = Part.objects.create(name=Part.WING, aircraft_type=self.aircraft.name)
        aircraft_tb2 = Aircraft.objects.create(name='TB2')

        # When: Assigning the Part to the Aircraft
        aircraft_part = AircraftPart.objects.create(aircraft=aircraft_tb2, part=part_tb2)

        # Then: The Part should be successfully assigned to the Aircraft
        self.assertEqual(aircraft_part.aircraft, aircraft_tb2)
        self.assertEqual(aircraft_part.part, part_tb2)

    def test_different_aircraft_types_for_multiple_parts(self):
        """
        Test that multiple parts with different aircraft types can be created.
        """
        # Given: Multiple Parts for different aircraft types
        part_tb2 = Part.objects.create(name=Part.AVIONICS, aircraft_type=self.aircraft.name)
        part_akinci = Part.objects.create(name=Part.BODY, aircraft_type='AKINCI')

        # Then: Each Part should have its specified aircraft type
        self.assertEqual(part_tb2.aircraft_type, 'TB2')
        self.assertEqual(part_akinci.aircraft_type, 'AKINCI')
        self.assertEqual(Part.objects.count(), 2)


class PersonnelModelTests(TestCase):
    """
    Tests for the Personnel model.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Given: Predefined team names and descriptions.
        When: Creating teams if they do not already exist.
        """
        teams_data = [
            ('Wing Team', 'Responsible for wing parts'),
            ('Body Team', 'Responsible for body parts'),
            ('Tail Team', 'Responsible for tail parts'),
            ('Avionics Team', 'Responsible for avionic parts'),
            ('Assembly Team', 'Only assembles parts'),
        ]

        cls.teams = {}
        for name, description in teams_data:
            team = Team.objects.filter(name=name).first()
            if not team:
                team = Team.objects.create(name=name, description=description)
            cls.teams[name] = team

        cls.wing_team = cls.teams['Wing Team']
        cls.body_team = cls.teams['Body Team']

        # Create a default aircraft and personnel for testing
        cls.aircraft = Aircraft.objects.create(name='TB2')
        user = User.objects.create_user(username='johndoe', password='password123')
        cls.personnel = Personnel.objects.create(user=user, team=cls.body_team, role='Technician')

    def test_create_personnel(self):
        """
        Test creating a new Personnel associated with a Team.
        """
        # Given: An existing team from setUp
        team = self.body_team

        # When: Creating a new User and linking it to Personnel associated with the Team
        user = User.objects.create_user(username='janedoe', password='password123')
        new_personnel = Personnel.objects.create(user=user, team=team, role='Technician')

        # Then: The Personnel should be created successfully and counted correctly
        self.assertEqual(new_personnel.user.username, 'janedoe')
        self.assertEqual(new_personnel.team, team)
        self.assertEqual(Personnel.objects.count(), 2)  # Including the one created in setUp

    def test_personnel_update_role(self):
        """
        Test updating the role of an existing Personnel.
        """
        # Given: An existing Personnel
        # When: Updating the role of the Personnel
        self.personnel.role = 'Senior Engineer'
        self.personnel.save()

        # Then: The updated role should be saved correctly
        updated_personnel = Personnel.objects.get(id=self.personnel.id)
        self.assertEqual(updated_personnel.role, 'Senior Engineer')

    def test_is_superuser_property(self):
        """
        Test that the is_superuser property reflects the user's superuser status.
        """
        # Given: A superuser User and a regular User
        superuser, _ = User.objects.get_or_create(username='adminuser',
                                                  defaults={'password': 'password123', 'is_superuser': True})
        regular_user, _ = User.objects.get_or_create(username='regularuser', defaults={'password': 'password123'})

        # Create Personnel for both users if they don't exist
        if not Personnel.objects.filter(user=superuser).exists():
            superuser_personnel = Personnel.objects.create(user=superuser, team=self.body_team, role='Admin')
        else:
            superuser_personnel = Personnel.objects.get(user=superuser)

        if not Personnel.objects.filter(user=regular_user).exists():
            regular_personnel = Personnel.objects.create(user=regular_user, team=self.teams['Wing Team'],
                                                         role='Technician')
        else:
            regular_personnel = Personnel.objects.get(user=regular_user)

        # Then: superuser_personnel should have is_superuser True, regular_personnel should have it False
        self.assertTrue(superuser_personnel.is_superuser)
        self.assertFalse(regular_personnel.is_superuser)

    def test_update_team(self):
        """
        Test updating the team of an existing Personnel.
        """
        # Given: An existing Personnel with a team
        new_team, _ = Team.objects.get_or_create(name='New Team')

        # When: Updating the Personnel's team
        self.personnel.team = new_team
        self.personnel.save()

        # Then: The Personnel's team should be updated successfully
        updated_personnel = Personnel.objects.get(id=self.personnel.id)
        self.assertEqual(updated_personnel.team, new_team)

    def test_delete_user_also_deletes_personnel(self):
        """
        Test that deleting a User also deletes the linked Personnel.
        """
        # Given: A Personnel linked to a User
        user = User.objects.create_user(username='deletetestuser', password='password123')
        personnel = Personnel.objects.create(user=user, team=self.body_team, role='Test Role')

        # When: Deleting the User
        user.delete()

        # Then: The linked Personnel should also be deleted
        with self.assertRaises(Personnel.DoesNotExist):
            Personnel.objects.get(user=user)
