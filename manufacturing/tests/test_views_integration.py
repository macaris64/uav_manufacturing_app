from unittest import skip

from rest_framework import status
from django.urls import reverse
from manufacturing.models import AircraftPart, Part, Aircraft
from manufacturing.tests.setup_test import ManufacturingTestSetup


class AircraftViewSetIntegrationTests(ManufacturingTestSetup):

    def test_check_parts_missing(self):
        """
        Test to ensure the API correctly identifies missing parts for an aircraft.
        """
        # Given: Only 'WING' and 'BODY' are available; 'TAIL' and 'AVIONICS' are missing.
        response = self.client.get(reverse('aircraft-check-parts', kwargs={'pk': self.aircraft.pk}))

        # When: Checking parts for the specified aircraft.
        # Then: Expect a 400 BAD REQUEST response due to missing parts.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("The following parts are missing", response.data['error'])

    def test_check_parts_all_available(self):
        """
        Test to ensure the API confirms all required parts are present for an aircraft.
        """
        # Given: All required parts are added to the aircraft.
        Part.objects.create(name='TAIL', aircraft_type=self.aircraft.name)
        Part.objects.create(name='AVIONICS', aircraft_type=self.aircraft.name)

        # When: Checking parts for the specified aircraft.
        response = self.client.get(reverse('aircraft-check-parts', kwargs={'pk': self.aircraft.pk}))

        # Then: Expect a 200 OK response since no parts are missing.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"success": "All parts are available for assembly."})

    def test_check_parts_invalid_aircraft_id(self):
        """
        Test to ensure the API returns a 404 NOT FOUND response for an invalid aircraft ID.
        """
        # Given: A non-existent aircraft ID.
        response = self.client.get(reverse('aircraft-check-parts', kwargs={'pk': 9999}))

        # When: Attempting to check parts for this invalid aircraft ID.
        # Then: Expect a 404 NOT FOUND response.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_aircraft_success(self):
        """
        Test to ensure a new Aircraft can be created successfully.
        """
        # Given: Data for a new Aircraft creation.
        data = {'name': 'AKINCI'}

        # When: Sending a POST request to create a new Aircraft.
        response = self.client.post(reverse('aircraft-list'), data)

        # Then: Expect a 201 CREATED response and verify the aircraft exists.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Aircraft.objects.filter(name='AKINCI').exists())

    def test_create_aircraft_missing_name(self):
        """
        Test to ensure the API requires a name when creating an Aircraft.
        """
        # Given: Data without the 'name' field.
        data = {}

        # When: Attempting to create an Aircraft.
        response = self.client.post(reverse('aircraft-list'), data)

        # Then: Expect a 400 BAD REQUEST response due to missing 'name'.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This field is required.", str(response.data))

    def test_update_aircraft_name(self):
        """
        Test to ensure the API allows updating an existing Aircraft's name.
        """
        # Given: An existing aircraft.
        data = {'name': 'AKINCI'}

        # When: Sending a PUT request to update the aircraft name.
        response = self.client.put(reverse('aircraft-detail', kwargs={'pk': self.aircraft.pk}), data)

        # Then: Expect a 200 OK response and verify the update.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.aircraft.refresh_from_db()
        self.assertEqual(self.aircraft.name, 'AKINCI')

    def test_update_aircraft_missing_name(self):
        """
        Test to ensure the API rejects updates when the name field is missing.
        """
        # Given: Data without the 'name' field.
        data = {}

        # When: Attempting to update an aircraft.
        response = self.client.put(reverse('aircraft-detail', kwargs={'pk': self.aircraft.pk}), data)

        # Then: Expect a 400 BAD REQUEST response.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This field is required.", str(response.data))

    def test_delete_aircraft_success(self):
        """
        Test to ensure the API successfully deletes an existing aircraft.
        """
        # Given: An existing aircraft.
        response = self.client.delete(reverse('aircraft-detail', kwargs={'pk': self.aircraft.pk}))

        # When: Sending a DELETE request to remove the aircraft.
        # Then: Expect a 204 NO CONTENT response and ensure the aircraft no longer exists.
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Aircraft.objects.filter(pk=self.aircraft.pk).exists())

    def test_delete_aircraft_not_found(self):
        """
        Test to ensure the API returns a 404 NOT FOUND response for a non-existent aircraft ID.
        """
        # Given: A non-existent aircraft ID.
        response = self.client.delete(reverse('aircraft-detail', kwargs={'pk': 9999}))

        # When: Attempting to delete this aircraft.
        # Then: Expect a 404 NOT FOUND response.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_aircraft_details(self):
        """
        Test to ensure the API retrieves details of an existing aircraft.
        """
        # Given: An existing aircraft.
        response = self.client.get(reverse('aircraft-detail', kwargs={'pk': self.aircraft.pk}))

        # When: Performing a GET request to retrieve the aircraft details.
        # Then: Expect a 200 OK response and verify the details.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.aircraft.name)

    def test_get_aircraft_not_found(self):
        """
        Test to ensure the API returns a 404 NOT FOUND response for a non-existent aircraft ID.
        """
        # Given: A non-existent aircraft ID.
        response = self.client.get(reverse('aircraft-detail', kwargs={'pk': 9999}))

        # When: Attempting to retrieve this aircraft.
        # Then: Expect a 404 NOT FOUND response.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_aircraft(self):
        """
        Test to ensure the API lists all existing aircraft.
        """
        # Given: An existing aircraft in the system.
        response = self.client.get(reverse('aircraft-list'))

        # When: Making a GET request to list all aircraft.
        # Then: Expect a 200 OK response and verify the aircraft is included in the response data.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], self.aircraft.name)


class AircraftPartViewSetIntegrationTests(ManufacturingTestSetup):

    def test_create_aircraft_part_success(self):
        """
        Test to ensure an AircraftPart can be created successfully.
        """
        # Given: Data for a successful AircraftPart creation.
        part = Part.objects.create(name='WING', aircraft_type='TB2')  # Part creation with aircraft type
        data = {
            'aircraft': self.aircraft.id,  # Uçak ID'si
            'part': part.id  # Parça ID'si
        }

        # When: Sending a POST request to create AircraftPart.
        response = self.client.post(self.aircraft_part_url, data)

        # Then: Expect a 201 CREATED response and verify the AircraftPart exists.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(AircraftPart.objects.filter(aircraft=self.aircraft, part=part).exists())

    def test_create_aircraft_part_without_required_fields(self):
        """
        Test to ensure the API rejects creation of AircraftPart without required fields.
        """
        # Given: Missing 'part' field in the request data.
        data = {
            'aircraft': self.aircraft.id
        }

        # When: Attempting to create an AircraftPart.
        response = self.client.post(self.aircraft_part_url, data)

        # Then: Expect a 400 BAD REQUEST response.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This field is required.", str(response.data))

    def test_create_aircraft_part_part_already_used(self):
        """
        Test to ensure the API prevents re-assigning a part already in use to another aircraft.
        """
        # Given: An existing AircraftPart association.
        AircraftPart.objects.create(aircraft=self.aircraft, part=self.wing_part)

        # When: Attempting to re-assign the same part to another aircraft.
        new_aircraft = Aircraft.objects.create(name='TB3')
        data = {
            'aircraft': new_aircraft.id,
            'part': self.wing_part.id
        }
        response = self.client.post(self.aircraft_part_url, data)

        # Then: Expect a 403 FORBIDDEN response due to part already in use.
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("This part is already used in another aircraft.", str(response.data))

    def test_create_aircraft_part_part_belongs_to_different_aircraft(self):
        """
        Test to ensure the API prevents using a part that does not belong to the specified aircraft.
        """
        # Given: A part that does not belong to the specified aircraft.
        new_aircraft = Aircraft.objects.create(name='TB3')
        data = {
            'aircraft': new_aircraft.id,
            'part': self.wing_part.id
        }

        # When: Attempting to create an AircraftPart.
        response = self.client.post(self.aircraft_part_url, data)

        # Then: Expect a 403 FORBIDDEN response.
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("This part does not belong to this type of aircraft.", str(response.data))

    def test_create_duplicate_aircraft_part(self):
        """
        Test to ensure the API prevents creating a duplicate AircraftPart association.
        """
        # Given: An initial AircraftPart association.
        AircraftPart.objects.create(aircraft=self.aircraft, part=self.wing_part)

        # When: Attempting to create the same AircraftPart again.
        data = {
            'aircraft': self.aircraft.id,
            'part': self.wing_part.id
        }
        response = self.client.post(self.aircraft_part_url, data)

        # Then: Expect a 403 FORBIDDEN response due to duplicate entry constraint.
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("This part is already used in another aircraft.", str(response.data))

    def test_create_aircraft_part_invalid_part(self):
        """
        Test to ensure the API rejects creation of AircraftPart with a non-existing part.
        """
        # Given: A non-existing part ID.
        data = {
            'aircraft': self.aircraft.id,
            'part': 9999  # Invalid Part ID
        }

        # When: Attempting to create an AircraftPart.
        response = self.client.post(self.aircraft_part_url, data)

        # Then: Expect a 400 BAD REQUEST response for invalid part.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid pk", str(response.data))
        self.assertIn("object does not exist", str(response.data))

    def test_update_aircraft_part_success(self):
        """
        Test to ensure the API allows updating an existing AircraftPart association.
        """
        # Given: An initial AircraftPart association.
        aircraft_part = AircraftPart.objects.create(aircraft=self.aircraft, part=self.wing_part)

        # Create a new aircraft and data for updating the AircraftPart association.
        new_aircraft = Aircraft.objects.create(name='TB3')
        data = {
            'aircraft': new_aircraft.id,
            'part': self.wing_part.id
        }

        # When: Sending a PUT request to update the AircraftPart.
        response = self.client.put(reverse('aircraftpart-detail', kwargs={'pk': aircraft_part.pk}), data)

        # Then: Expect a 200 OK response and verify the update.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(AircraftPart.objects.get(pk=aircraft_part.pk).aircraft, new_aircraft)

    def test_update_aircraft_part_invalid_aircraft(self):
        """
        Test to ensure the API rejects updates when the aircraft ID is invalid.
        """
        # Given: An initial AircraftPart association.
        aircraft_part = AircraftPart.objects.create(aircraft=self.aircraft, part=self.wing_part)

        # Data with an invalid aircraft ID.
        data = {
            'aircraft': 9999,  # Invalid Aircraft ID
            'part': self.wing_part.id
        }

        # When: Attempting to update the AircraftPart with an invalid aircraft.
        response = self.client.put(reverse('aircraftpart-detail', kwargs={'pk': aircraft_part.pk}), data)

        # Then: Expect a 400 BAD REQUEST response.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid pk", str(response.data))

    def test_delete_aircraft_part_success(self):
        """
        Test to ensure the API successfully deletes an existing AircraftPart.
        """
        # Given: An initial AircraftPart association.
        aircraft_part = AircraftPart.objects.create(aircraft=self.aircraft, part=self.wing_part)

        # When: Sending a DELETE request to remove the AircraftPart.
        response = self.client.delete(reverse('aircraftpart-detail', kwargs={'pk': aircraft_part.pk}))

        # Then: Expect a 204 NO CONTENT response and ensure the AircraftPart no longer exists.
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(AircraftPart.objects.filter(pk=aircraft_part.pk).exists())

    def test_delete_aircraft_part_not_found(self):
        """
        Test to ensure the API returns a 404 NOT FOUND response for a non-existent AircraftPart ID.
        """
        # When: Attempting to delete an AircraftPart with a non-existent ID.
        response = self.client.delete(reverse('aircraftpart-detail', kwargs={'pk': 9999}))

        # Then: Expect a 404 NOT FOUND response.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_aircraft_part_details_success(self):
        """
        Test to ensure the API retrieves details of an existing AircraftPart.
        """
        # Given: An initial AircraftPart association.
        aircraft_part = AircraftPart.objects.create(aircraft=self.aircraft, part=self.wing_part)

        # When: Sending a GET request to retrieve the AircraftPart details.
        response = self.client.get(reverse('aircraftpart-detail', kwargs={'pk': aircraft_part.pk}))

        # Then: Expect a 200 OK response with correct aircraft and part IDs.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['aircraft'], self.aircraft.id)
        self.assertEqual(response.data['part'], self.wing_part.id)

    def test_get_aircraft_part_not_found(self):
        """
        Test to ensure the API returns a 404 NOT FOUND response for a non-existent AircraftPart ID.
        """
        # When: Attempting to retrieve an AircraftPart with a non-existent ID.
        response = self.client.get(reverse('aircraftpart-detail', kwargs={'pk': 9999}))

        # Then: Expect a 404 NOT FOUND response.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
