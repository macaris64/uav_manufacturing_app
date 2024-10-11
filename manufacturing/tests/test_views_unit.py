from unittest import skip

from django.test import TestCase
from unittest.mock import Mock, patch, MagicMock
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from manufacturing.models import Aircraft, Part, Team
from manufacturing.views import AircraftViewSet, AircraftPartViewSet, PartViewSet


class AircraftViewSetUnitTests(TestCase):

    @patch('manufacturing.views.Part.objects.filter')
    def test_check_parts_missing(self, mock_filter):
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

    @patch('manufacturing.permissions.PartBelongsToAircraftType.has_permission', return_value=True)
    @patch('manufacturing.permissions.PartIsNotUsedInOtherAircraft.has_permission',
           return_value=False)  # Simulate part already used
    def test_perform_create_part_already_used(self, mock_part_is_not_used, mock_part_belongs):
        # Given: a view instance with mock serializer and request
        view = AircraftPartViewSet()
        view.request = Mock()
        view.action = 'create'

        # Create a Team instance for the Part
        aircraft = Aircraft.objects.create(name='TB2', serial_number='123e4567-e89b-12d3-a456-426614174000')
        part = Part.objects.create(name='WING', aircraft=aircraft)

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
        # Given: a view instance where the part belongs to another aircraft
        view = AircraftPartViewSet()
        view.request = Mock()
        view.action = 'create'

        # Create real instances for testing
        aircraft1 = Aircraft.objects.create(name='TB2', serial_number='123e4567-e89b-12d3-a456-426614174000')
        aircraft2 = Aircraft.objects.create(name='TB3', serial_number='123e4567-e89b-12d3-a456-426614174001')
        part = Part.objects.create(name='WING', aircraft=aircraft1)

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
        # Given: a view instance where the part is not used in any other aircraft
        view = AircraftPartViewSet()
        view.request = Mock()
        view.action = 'create'

        # Create real instances for testing
        aircraft = Aircraft.objects.create(name='TB2', serial_number='123e4567-e89b-12d3-a456-426614174000')
        part = Part.objects.create(name='WING', aircraft=aircraft)

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
        # Given: An Aircraft and a Team
        aircraft = Aircraft.objects.create(name='TB2', serial_number='123e4567-e89b-12d3-a456-426614174000')
        team = Team.objects.create(name='Wing Team', description='Responsible for wing parts')

        # When: Creating a new Part and then assigning it to the Team
        part = Part.objects.create(name='WING', aircraft=aircraft)  # Part created without direct team assignment
        team.parts.add(part)  # Assigning the part to the team

        # Then: The team should have the assigned part
        self.assertIn(part, team.parts.all())  # Verify the part is associated with the team

    def test_cannot_assign_part_to_non_responsible_team(self):
        # Given: An Aircraft and a non-responsible Team
        aircraft = Aircraft.objects.create(name='TB2', serial_number='123e4567-e89b-12d3-a456-426614174001')
        avionic_team = Team.objects.create(name='Avionic Team', description='Responsible for avionic parts')
        wing_part = Part.objects.create(name='WING', aircraft=aircraft)

        # When: Attempting to assign the wing part to the avionic team
        can_assign = avionic_team.can_produce_part(wing_part)  # Check if the team can assign the part

        # Then: The team should not be able to assign the wing part
        self.assertFalse(can_assign)

        # Expecting an exception when trying to add the part directly
        with self.assertRaises(ValueError):  # Expect a ValueError for non-responsible team
            avionic_team.add_part(wing_part)
