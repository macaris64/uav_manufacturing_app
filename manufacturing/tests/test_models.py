from unittest import skip

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
        new_aircraft = Aircraft.objects.create(name='TB3')

        # When: Attempting to assign the same Part to a different Aircraft
        # Then: An IntegrityError should be raised due to the uniqueness constraint
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                AircraftPart.objects.create(aircraft=new_aircraft, part=self.wing_part)
        self.assertEqual(AircraftPart.objects.count(), 1)


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
        avionic_part = Part.objects.create(name='AVIONICS', aircraft=self.aircraft)

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
        part1 = Part.objects.create(name='WING', aircraft=self.aircraft)
        part2 = Part.objects.create(name='TAIL', aircraft=self.aircraft)

        # When: Assigning multiple parts to the team
        new_team.parts.add(part1, part2)

        # Then: The team should have both assigned parts
        self.assertIn(part1, new_team.parts.all())
        self.assertIn(part2, new_team.parts.all())


class PartModelTests(ManufacturingTestSetup, TestCase):
    """
    Tests for the Part model.
    """

    def test_create_part(self):
        # Given: An Aircraft and a Team
        # When: Creating a new Part associated with both
        new_part = Part.objects.create(name='TAIL', aircraft=self.aircraft)

        # Then: The Part should be created successfully and counted correctly
        self.assertEqual(new_part.name, 'TAIL')
        self.assertEqual(new_part.aircraft, self.aircraft)
        self.assertEqual(Part.objects.count(), 3)  # Including the ones created in setUp

    def test_part_unique_per_aircraft(self):
        # Given: An Aircraft and a Part associated with it
        new_aircraft = Aircraft.objects.create(name='TB3')

        # When: Creating a Part with the same name but associated with a different Aircraft
        new_part = Part.objects.create(name='WING', aircraft=new_aircraft)

        # Then: The Part should be created successfully since the uniqueness constraint applies per Aircraft
        self.assertEqual(new_part.name, 'WING')
        self.assertEqual(new_part.aircraft, new_aircraft)

    def test_create_part_with_team_association(self):
        # Given: An Aircraft and a Team
        aircraft = Aircraft.objects.create(name='TB2', serial_number='123e4567-e89b-12d3-a456-426614174001')
        team = Team.objects.create(name='Avionic Team', description='Responsible for avionic parts')

        # When: Creating a Part and then assigning it to the Team
        part = Part.objects.create(name='WING', aircraft=aircraft)
        team.parts.add(part)  # Assigning the part to the team

        # Then: The team should have the assigned part
        self.assertIn(part, team.parts.all())

    def test_part_assigned_to_multiple_teams(self):
        # Given: An Aircraft and two Teams
        aircraft = Aircraft.objects.create(name='TB2', serial_number='123e4567-e89b-12d3-a456-426614174001')
        team1 = Team.objects.create(name='Tail Team', description='Responsible for tail parts')
        team2 = Team.objects.create(name='Avionic Team', description='Responsible for avionics parts')

        # When: Creating a Part and assigning it to both teams
        part = Part.objects.create(name='TAIL', aircraft=aircraft)
        team1.parts.add(part)
        team2.parts.add(part)  # Assigning the same part to another team

        # Then: Both teams should have the assigned part
        self.assertIn(part, team1.parts.all())
        self.assertIn(part, team2.parts.all())

    def test_part_can_only_be_assigned_to_responsible_team(self):
        # Given: An Aircraft and a Part
        aircraft = Aircraft.objects.create(name='TB2', serial_number='123e4567-e89b-12d3-a456-426614174001')
        team = Team.objects.create(name='Avionic Team', description='Responsible for avionic parts')
        part = Part.objects.create(name='TAIL', aircraft=aircraft)

        # When: Attempting to assign a part to a non-responsible team
        if not team.can_produce_part(part):  # Check if the team can assign the part
            # Then: The part should not be assigned to the team
            self.assertNotIn(part, team.parts.all())
        else:
            team.parts.add(part)  # Only add if it is a responsible team
            self.fail("The team should not be able to assign this part.")


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
