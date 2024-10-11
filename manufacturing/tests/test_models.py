from unittest import skip

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from manufacturing.models import Aircraft, Team, Part, AircraftPart, Personnel
from manufacturing.tests.setup_test import ManufacturingTestSetup


class AircraftPartModelTests(ManufacturingTestSetup, TestCase):
    """
    Tests specifically for the AircraftPart model, ensuring parts are assigned only to one aircraft and managed correctly.
    """

    def test_create_aircraft_part_association(self):
        # Given: An Aircraft and a Part
        # When: Creating an association between Aircraft and Part as AircraftPart
        aircraft_part = AircraftPart.objects.create(aircraft=self.aircraft, part=self.wing_part)

        # Then: The association should be created successfully
        self.assertEqual(aircraft_part.aircraft, self.aircraft)
        self.assertEqual(aircraft_part.part, self.wing_part)
        self.assertEqual(AircraftPart.objects.count(), 1)

    def test_part_cannot_be_reassigned_to_another_aircraft(self):
        # Given: An AircraftPart associated with the current Aircraft and Part
        AircraftPart.objects.create(aircraft=self.aircraft, part=self.wing_part)
        new_aircraft = Aircraft.objects.create(name='TB3', serial_number='123e4567-e89b-12d3-a456-426614174002')

        # When: Attempting to assign the same Part to a different Aircraft
        aircraft_part = AircraftPart(aircraft=new_aircraft, part=self.wing_part)

        # Then: A ValidationError should be raised due to the uniqueness constraint in clean()
        with self.assertRaises(ValidationError):
            aircraft_part.clean()
            aircraft_part.save()

        # Confirm only one AircraftPart exists
        self.assertEqual(AircraftPart.objects.count(), 1)

    def test_unique_part_per_aircraft(self):
        # Given: An Aircraft and a Part associated with it
        aircraft1 = Aircraft.objects.create(name='TB2', serial_number='123e4567-e89b-12d3-a456-426614174001')
        part = Part.objects.create(name='WING', aircraft_type='TB2')

        # When: Creating an AircraftPart association
        AircraftPart.objects.create(aircraft=aircraft1, part=part)

        # Then: An IntegrityError should be raised if trying to associate the same part with a different aircraft
        aircraft2 = Aircraft.objects.create(name='TB3', serial_number='123e4567-e89b-12d3-a456-426614174002')
        with self.assertRaises(ValidationError):
            aircraft_part = AircraftPart(aircraft=aircraft2, part=part)
            aircraft_part.clean()

    def test_part_type_constraint(self):
        # Given: An Aircraft and a Part of a different type associated with it
        AircraftPart.objects.create(aircraft=self.aircraft, part=self.wing_part)

        # When: Adding another part type to the same aircraft
        new_aircraft_part = AircraftPart(aircraft=self.aircraft, part=self.body_part)
        new_aircraft_part.clean()  # This should not raise an error

        # Then: The new part should be allowed and saved
        new_aircraft_part.save()
        self.assertEqual(AircraftPart.objects.filter(aircraft=self.aircraft).count(), 2)


class AircraftModelTests(ManufacturingTestSetup, TestCase):
    """
    Tests for the Aircraft model.
    """

    def test_create_aircraft(self):
        # Given: No additional Aircraft
        # When: Creating a new Aircraft with a unique name
        new_aircraft = Aircraft.objects.create(name='TB3', serial_number='123e4567-e89b-12d3-a456-426614174001')

        # Then: The Aircraft should be created and counted correctly
        self.assertEqual(new_aircraft.name, 'TB3')
        self.assertEqual(Aircraft.objects.count(), 2)  # Including the one created in setUp

    def test_update_aircraft(self):
        # Given: An existing Aircraft
        # When: Updating the Aircraft name
        self.aircraft.name = 'Updated TB2'
        self.aircraft.save()

        # Then: The updated name should be saved correctly
        updated_aircraft = Aircraft.objects.get(id=self.aircraft.id)
        self.assertEqual(updated_aircraft.name, 'Updated TB2')

    def test_aircraft_is_produced_when_all_parts_are_added(self):
        """Test that an aircraft is marked as produced when all required parts are added."""
        # Given: An aircraft and all required parts
        aircraft = Aircraft.objects.create(name='TB2')
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
        aircraft.refresh_from_db()  # Refresh the aircraft object from the database
        self.assertTrue(aircraft.is_produced)

    def test_aircraft_not_produced_with_missing_parts(self):
        """Test that an aircraft is not marked as produced when some parts are missing."""
        # Given: An aircraft and some of the required parts (missing one)
        aircraft = Aircraft.objects.create(name='TB2')
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


class TeamModelTests(ManufacturingTestSetup, TestCase):
    """
    Tests for the Team model.
    """

    def test_create_team(self):
        # Given: No additional Team
        # When: Creating a new Team
        new_team = Team.objects.create(name='Tail Team')

        # Then: The Team should be created successfully and counted correctly
        self.assertEqual(new_team.name, 'Tail Team')
        self.assertEqual(Team.objects.count(), 3)  # Including the ones created in setUp

    def test_unique_team_name(self):
        # Given: An existing Team with a specific name
        # When: Attempting to create another Team with the same name
        # Then: An IntegrityError should be raised due to the unique constraint
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Team.objects.create(name='Wing Team')

    def test_assign_part_to_team(self):
        # Given: An existing Part and Team
        # When: Assigning the part to the team
        self.wing_team.parts.add(self.wing_part)

        # Then: The part should be associated with the team
        self.assertIn(self.wing_part, self.wing_team.parts.all())

    def test_create_team_with_assigned_part(self):
        # Given: A Part and a new Team
        new_team = Team.objects.create(name='Avionic Team', description='Responsible for avionic parts')
        avionic_part = Part.objects.create(name='AVIONICS', aircraft_type=self.aircraft.name)

        # When: Assigning the part to the new team
        new_team.parts.add(avionic_part)

        # Then: The new team should have the assigned part
        self.assertIn(avionic_part, new_team.parts.all())

    def test_cannot_assign_part_to_non_responsible_team(self):
        # Given: An existing Avionic Team
        avionic_team = Team.objects.create(name='Avionic Team', description='Responsible for avionic parts')

        # Ensure the wing team is responsible for wing parts
        self.wing_team.parts.add(self.wing_part)

        # When: Attempting to assign a part that the avionic team is not responsible for
        # Then: The part cannot be assigned and should raise an exception if checked
        can_assign = avionic_team.can_produce_part(self.wing_part)
        self.assertFalse(can_assign)  # Avionic Team should not be able to produce wing parts

        # Directly adding the part should not work in application logic
        self.assertNotIn(self.wing_part, avionic_team.parts.all())

    def test_team_has_no_parts_initially(self):
        # Given: A newly created Team
        new_team = Team.objects.create(name='New Team')

        # Then: The team should have no parts assigned
        self.assertEqual(new_team.parts.count(), 0)

    def test_team_description(self):
        # Given: A newly created Team with a description
        new_team = Team.objects.create(name='New Team', description='This is a new team')

        # Then: The team description should be set correctly
        self.assertEqual(new_team.description, 'This is a new team')

    def test_remove_part_from_team(self):
        # Given: An existing Team and Part
        self.wing_team.parts.add(self.wing_part)

        # When: Removing the part from the team
        self.wing_team.parts.remove(self.wing_part)

        # Then: The part should no longer be associated with the team
        self.assertNotIn(self.wing_part, self.wing_team.parts.all())

    def test_team_can_produce_multiple_parts(self):
        # Given: A new Team and multiple Parts
        new_team = Team.objects.create(name='Multi Part Team')
        part1 = Part.objects.create(name='WING', aircraft_type=self.aircraft.name)
        part2 = Part.objects.create(name='TAIL', aircraft_type=self.aircraft.name)

        # When: Assigning multiple parts to the team
        new_team.parts.add(part1, part2)

        # Then: The team should have both assigned parts
        self.assertIn(part1, new_team.parts.all())
        self.assertIn(part2, new_team.parts.all())


class PartModelTests(TestCase):
    """
    Tests for the Part model.
    """

    def test_create_part(self):
        """Test creating a Part associated with an Aircraft type."""
        # Given: An Aircraft
        aircraft = Aircraft.objects.create(name='TB2')

        # When: Creating a Part associated with that aircraft type
        new_part = Part.objects.create(name=Part.WING, aircraft_type=aircraft.name)

        # Then: The Part should be created successfully
        self.assertEqual(new_part.name, Part.WING)
        self.assertEqual(new_part.aircraft_type, aircraft.name)
        self.assertEqual(Part.objects.count(), 1)

    def test_part_unique_per_aircraft(self):
        """Test that parts with the same name can be created for different aircraft types."""
        # Given: Two Aircrafts of different types
        aircraft_tb2 = Aircraft.objects.create(name='TB2')
        aircraft_tb3 = Aircraft.objects.create(name='TB3')
        Part.objects.create(name='WING', aircraft_type=aircraft_tb2.name)

        # When: Creating a Part with the same name but for a different aircraft type
        new_part = Part.objects.create(name='WING', aircraft_type=aircraft_tb3.name)

        # Then: The Part should be created successfully for the new aircraft type
        self.assertEqual(Part.objects.count(), 2)
        self.assertEqual(new_part.aircraft_type, 'TB3')

    def test_create_part_with_team_association(self):
        """Test associating a Part with a Team."""
        # Given: An Aircraft and a Team
        aircraft = Aircraft.objects.create(name='TB2')
        team = Team.objects.create(name='Avionic Team', description='Responsible for avionic parts')
        part = Part.objects.create(name='WING', aircraft_type=aircraft.name)

        # When: Assigning the Part to the Team
        team.parts.add(part)

        # Then: The team should have the assigned Part
        self.assertIn(part, team.parts.all())

    def test_part_assigned_to_multiple_teams(self):
        """Test a Part being assigned to multiple Teams."""
        # Given: An Aircraft and two Teams
        aircraft = Aircraft.objects.create(name='TB2')
        team1 = Team.objects.create(name='Tail Team', description='Responsible for tail parts')
        team2 = Team.objects.create(name='Avionic Team', description='Responsible for avionic parts')
        part = Part.objects.create(name='TAIL', aircraft_type=aircraft.name)

        # When: Assigning the Part to both Teams
        team1.parts.add(part)
        team2.parts.add(part)

        # Then: Both Teams should have the assigned Part
        self.assertIn(part, team1.parts.all())
        self.assertIn(part, team2.parts.all())

    def test_part_assignment_limited_to_responsible_team(self):
        """Test that a team can only be assigned parts it is responsible for."""
        # Given: An Aircraft and a Team
        aircraft = Aircraft.objects.create(name='TB2')
        team = Team.objects.create(name='Avionic Team', description='Responsible for avionic parts')
        part = Part.objects.create(name='TAIL', aircraft_type=aircraft.name)

        # When: Attempting to assign a non-responsible Part to the Team
        if not team.can_produce_part(part):
            # Then: The Part should not be assignable to the Team
            self.assertNotIn(part, team.parts.all())
        else:
            team.parts.add(part)
            self.fail("The team should not be able to assign this part.")

    def test_assign_responsible_part_to_team(self):
        """Test that a Team can produce and assign a compatible Part."""
        # Given: A Team and a Part that it is responsible for
        team = Team.objects.create(name='Avionic Team', description='Responsible for avionic parts')
        part = Part.objects.create(name='AVIONICS', aircraft_type='TB2')

        # When: Assigning the responsible Part to the Team
        team.parts.add(part)

        # Then: The Part should be assigned to the Team
        self.assertTrue(team.can_produce_part(part))
        self.assertIn(part, team.parts.all())

    def test_aircraft_part_incompatible_assignment(self):
        """Test that a Part cannot be assigned to an incompatible Aircraft type."""
        # Given: A Part created for TB2 and an Aircraft of type AKINCI
        part_tb2 = Part.objects.create(name=Part.WING, aircraft_type='TB2')
        aircraft_akinci = Aircraft.objects.create(name='AKINCI')
        aircraft_part = AircraftPart(aircraft=aircraft_akinci, part=part_tb2)

        # When/Then: Validating the assignment should raise a ValidationError
        with self.assertRaises(ValidationError):
            aircraft_part.clean()

    def test_aircraft_part_compatible_assignment(self):
        """Test that a compatible Part can be assigned to an Aircraft."""
        # Given: A Part compatible with TB2 and an Aircraft of type TB2
        part_tb2 = Part.objects.create(name=Part.WING, aircraft_type='TB2')
        aircraft_tb2 = Aircraft.objects.create(name='TB2')

        # When: Assigning the Part to the Aircraft
        aircraft_part = AircraftPart.objects.create(aircraft=aircraft_tb2, part=part_tb2)

        # Then: The Part should be successfully assigned to the Aircraft
        self.assertEqual(aircraft_part.aircraft, aircraft_tb2)
        self.assertEqual(aircraft_part.part, part_tb2)

    def test_different_aircraft_types_for_multiple_parts(self):
        """Test that multiple parts with different aircraft types can be created."""
        # Given: Multiple Parts for different aircraft types
        part_tb2 = Part.objects.create(name=Part.AVIONICS, aircraft_type='TB2')
        part_akinci = Part.objects.create(name=Part.BODY, aircraft_type='AKINCI')

        # Then: Each Part should have its specified aircraft type
        self.assertEqual(part_tb2.aircraft_type, 'TB2')
        self.assertEqual(part_akinci.aircraft_type, 'AKINCI')
        self.assertEqual(Part.objects.count(), 2)


class PersonnelModelTests(ManufacturingTestSetup, TestCase):
    """
    Tests for the Personnel model.
    """

    def test_create_personnel(self):
        # Given: A Team
        # When: Creating a new Personnel associated with the Team
        new_personnel = Personnel.objects.create(name='Jane Doe', team=self.body_team, role='Technician')

        # Then: The Personnel should be created successfully and counted correctly
        self.assertEqual(new_personnel.name, 'Jane Doe')
        self.assertEqual(new_personnel.team, self.body_team)
        self.assertEqual(Personnel.objects.count(), 2)  # Including the one created in setUp

    def test_personnel_update_role(self):
        # Given: An existing Personnel
        # When: Updating the role of the Personnel
        self.personnel.role = 'Senior Engineer'
        self.personnel.save()

        # Then: The updated role should be saved correctly
        updated_personnel = Personnel.objects.get(id=self.personnel.id)
        self.assertEqual(updated_personnel.role, 'Senior Engineer')
