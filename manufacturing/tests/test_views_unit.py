from django.test import TestCase
from unittest.mock import Mock, patch
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from manufacturing.models import Aircraft, Part, Team
from manufacturing.views import AircraftViewSet, AircraftPartViewSet


class AircraftViewSetUnitTests(TestCase):
    """
    Unit tests for the AircraftViewSet.
    Verifies the functionality of aircraft management.
    """

    @patch('manufacturing.views.Part.objects.filter')
    def test_check_parts_missing(self, mock_filter):
        """
        Test to ensure the API correctly identifies missing parts for an aircraft.
        """
        # Given: a mock aircraft and required parts
        view = AircraftViewSet()
        view.get_object = Mock(return_value=Mock())
        mock_filter.return_value.values_list.return_value = ['WING', 'TAIL']

        # When: check_parts is called
        response = view.check_parts(request=Mock(), pk=1)

        # Then: it should detect missing parts and return a 400 response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("The following parts are missing", response.data['error'])

    @patch('manufacturing.views.Part.objects.filter')
    def test_check_parts_no_parts_available(self, mock_filter):
        """
        Test to ensure the API returns a response indicating all parts are missing.
        """
        # Given: no parts are available for the aircraft
        view = AircraftViewSet()
        view.get_object = Mock(return_value=Mock())
        mock_filter.return_value.values_list.return_value = []

        # When: check_parts is called
        response = view.check_parts(request=Mock(), pk=1)

        # Then: it should return all parts as missing
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("The following parts are missing", response.data['error'])

    @patch('manufacturing.views.Part.objects.filter')
    def test_check_parts_available(self, mock_filter):
        """
        Test to ensure the API confirms all required parts are present for an aircraft.
        """
        # Given: all parts are available for the aircraft
        view = AircraftViewSet()
        view.get_object = Mock(return_value=Mock())
        mock_filter.return_value.values_list.return_value = ['WING', 'BODY', 'TAIL', 'AVIONICS']

        # When: check_parts is called
        response = view.check_parts(request=Mock(), pk=1)

        # Then: it should confirm all parts are available
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"success": "All parts are available for assembly."})


class AircraftPartViewSetUnitTests(TestCase):
    """
    Unit tests for the AircraftPartViewSet.
    Verifies the functionality of managing AircraftPart associations.
    """

    @patch('manufacturing.permissions.PartBelongsToAircraftType.has_permission', return_value=True)
    @patch('manufacturing.permissions.PartIsNotUsedInOtherAircraft.has_permission', return_value=False)
    def test_perform_create_part_already_used(self, mock_part_is_not_used, mock_part_belongs):
        """
        Test to ensure the API prevents re-assigning a part already in use to another aircraft.
        """
        # Given: a view instance with mock serializer and request
        view = AircraftPartViewSet()
        view.request = Mock()
        view.request.user = Mock(is_staff=False)  # Ensure user is not staff
        view.action = 'create'

        # Create an Aircraft instance and a Part instance
        aircraft = Aircraft.objects.create(name='TB2', serial_number='123e4567-e89b-12d3-a456-426614174000')
        part = Part.objects.create(name='WING', aircraft_type=aircraft.name)

        # Mock serializer with validated data as dictionary
        serializer = Mock()
        serializer.validated_data = {'aircraft': aircraft, 'part': part}

        # When/Then: PermissionDenied should be raised for part already used
        with self.assertRaises(PermissionDenied):
            view.perform_create(serializer)

        # Ensure permission checks were called
        mock_part_is_not_used.assert_called_once()
        mock_part_belongs.assert_called_once()

    @patch('manufacturing.permissions.PartBelongsToAircraftType.has_permission', return_value=False)
    @patch('manufacturing.permissions.PartIsNotUsedInOtherAircraft.has_permission', return_value=True)
    @patch('manufacturing.views.AircraftPart.objects.filter')
    def test_perform_create_part_belongs_to_another_aircraft(self, mock_filter, mock_part_is_not_used, mock_part_belongs):
        """
        Test to ensure the API prevents using a part that does not belong to the specified aircraft.
        """
        # Given: a view instance where the part belongs to another aircraft
        view = AircraftPartViewSet()
        view.request = Mock()
        view.request.user = Mock(is_staff=False)
        view.action = 'create'

        # Create real instances for testing
        aircraft1 = Aircraft.objects.create(name='TB2', serial_number='123e4567-e89b-12d3-a456-426614174000')
        aircraft2 = Aircraft.objects.create(name='TB3', serial_number='123e4567-e89b-12d3-a456-426614174001')
        part = Part.objects.create(name='WING', aircraft_type=aircraft1.name)

        # Mock serializer with validated data
        serializer = Mock()
        serializer.validated_data = {'aircraft': aircraft2, 'part': part}

        # When/Then: PermissionDenied should be raised if part belongs to another aircraft
        with self.assertRaises(PermissionDenied):
            view.perform_create(serializer)

    @patch('manufacturing.permissions.PartBelongsToAircraftType.has_permission', return_value=True)
    @patch('manufacturing.permissions.PartIsNotUsedInOtherAircraft.has_permission', return_value=True)
    @patch('manufacturing.views.AircraftPart.objects.filter')
    def test_perform_create_success(self, mock_filter, mock_part_is_not_used, mock_part_belongs):
        """
        Test to ensure the API allows creating an AircraftPart association successfully.
        """
        # Given: a view instance where the part is not used in any other aircraft
        view = AircraftPartViewSet()
        view.request = Mock()
        view.action = 'create'

        # Create real instances for testing
        aircraft = Aircraft.objects.create(name='TB2', serial_number='123e4567-e89b-12d3-a456-426614174000')
        part = Part.objects.create(name='WING', aircraft_type=aircraft.name)

        # Mock serializer and filter to allow creation
        serializer = Mock()
        serializer.validated_data = {'aircraft': aircraft, 'part': part}

        # Mock filter to return no matches, so part is not in use
        mock_filter.return_value.exists.return_value = False

        # Ensure the part belongs to the correct aircraft
        serializer.validated_data['part'].aircraft = serializer.validated_data['aircraft']

        # When: perform_create is called, it should not raise an error
        view.perform_create(serializer)

        # Then: serializer.save should be called once
        serializer.save.assert_called_once()

    def test_create_part_with_team_association(self):
        """
        Test to ensure a Part can be created with the correct team association.
        """
        # Given: An Aircraft and a Team
        aircraft = Aircraft.objects.create(name='TB2', serial_number='123e4567-e89b-12d3-a456-426614174000')
        team, _ = Team.objects.get_or_create(name=Team.WING_TEAM, description="Responsible for wing parts")

        # When: Creating a new Part
        part = Part.objects.create(name='WING', aircraft_type=aircraft.name)
        part_dict = {'name': part.name}

        # Check if the team can produce the part
        can_produce = team.can_produce_part(part_dict)

        # Then: The team should be able to produce the assigned part
        self.assertTrue(can_produce)

    def test_cannot_assign_part_to_non_responsible_team(self):
        """
        Test to ensure that a Team cannot assign a part it is not responsible for.
        """
        # Given: An Aircraft and a non-responsible Team
        aircraft = Aircraft.objects.create(name='TB2', serial_number='123e4567-e89b-12d3-a456-426614174001')
        avionic_team = Team.objects.create(name='Avionic Team', description='Responsible for avionic parts')
        wing_part = Part.objects.create(name='WING', aircraft_type=aircraft.name)
        wing_part_dict = {'name': wing_part.name}

        # When: Checking if the avionic team can produce a wing part
        can_assign = avionic_team.can_produce_part(wing_part_dict)

        # Then: The team should not be able to assign the wing part
        self.assertFalse(can_assign)
