from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from django.urls import reverse
from manufacturing.models import Aircraft, Team, Part, Personnel

class ManufacturingTestSetup(APITestCase):
    """
    Base setup for Manufacturing app tests.
    Creates common data such as User, Token, Aircraft, Team, and Part.
    """

    def setUp(self):
        """
        Given: Setup method to create common objects required for tests.
        Creates a User, Token, Aircraft, Teams, Personnel, and Parts.
        """
        # Create User and Get Token for authentication
        self.user = User.objects.create_user(username='testuser', password='password')
        self.token, created = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create an Aircraft for the parts
        self.aircraft = Aircraft.objects.create(name='TB2', serial_number='123e4567-e89b-12d3-a456-426614174000')

        # Create Teams responsible for specific parts
        self.wing_team, _ = Team.objects.get_or_create(name=Team.WING_TEAM, description="Responsible for wing parts")
        self.body_team, _ = Team.objects.get_or_create(name=Team.BODY_TEAM, description="Responsible for body parts")

        # Create Personnel and assign to the Wing Team
        self.personnel_user = User.objects.create_user(username='john_doe', password='password123')
        self.personnel = Personnel.objects.create(user=self.personnel_user, team=self.wing_team, role='Engineer')

        # Create Parts and assign to the respective teams
        self.wing_part = Part.objects.create(name=Part.WING, aircraft_type='TB2')
        self.body_part = Part.objects.create(name=Part.BODY, aircraft_type='TB2')

        # URL for Aircraft Part API endpoint
        self.aircraft_part_url = reverse('aircraftpart-list')
