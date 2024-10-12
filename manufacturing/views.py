from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from manufacturing.models import Aircraft, Team, Part, Personnel, AircraftPart
from manufacturing.serializers import AircraftSerializer, TeamSerializer, PartSerializer, PersonnelSerializer, \
    AircraftPartSerializer, UserSerializer
from manufacturing.permissions import CanOnlyCreateAssignedPart, PartIsNotUsedInOtherAircraft, PartBelongsToAircraftType

class AircraftViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Aircraft model operations.
    Provides actions for creating, reading, updating, and deleting Aircraft instances.
    """
    queryset = Aircraft.objects.all()
    serializer_class = AircraftSerializer

    @action(detail=True, methods=['get'])
    def check_parts(self, request, pk=None):
        """
        Custom action to check if all required parts for a given aircraft are available.
        - Retrieves the specific aircraft based on the provided primary key (pk).
        - Defines a list of required parts.
        - Queries for parts associated with this aircraft and identifies any missing parts.
        - Returns a success message if all parts are available or an error message with missing parts.
        """
        aircraft = self.get_object()

        required_parts = ['WING', 'BODY', 'TAIL', 'AVIONICS']
        available_parts = Part.objects.filter(aircraft_type=aircraft.name).values_list('name', flat=True)

        missing_parts = [part for part in required_parts if part not in available_parts]

        if missing_parts:
            return Response(
                {"error": f"The following parts are missing: {', '.join(missing_parts)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"success": "All parts are available for assembly."})


class TeamViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Team instances.
    Provides standard actions (list, retrieve, create, update, and destroy) for the Team model.
    """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]


class PartViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Part instances.
    - Utilizes a custom permission class, CanOnlyCreateAssignedPart, to control part creation
      based on the team’s assigned part type.
    - Provides standard actions for creating, reading, updating, and deleting parts.
    """
    queryset = Part.objects.all()
    serializer_class = PartSerializer
    permission_classes = [CanOnlyCreateAssignedPart]

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        # Limit parts to those that the user is allowed to see based on their teams
        user_teams = self.request.user.team_set.all()  # Adjust based on your user model
        return self.queryset.filter(teams__in=user_teams)


class PersonnelViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Personnel instances.
    Provides standard actions (list, retrieve, create, update, and destroy) for Personnel model.
    """
    queryset = Personnel.objects.all()
    serializer_class = PersonnelSerializer


class AircraftPartViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling AircraftPart instances.
    - Controls creation of parts for specific aircraft.
    - Checks whether the part is already used in another aircraft and if the part belongs to the
      correct aircraft type.
    """
    queryset = AircraftPart.objects.all()
    serializer_class = AircraftPartSerializer


    def perform_create(self, serializer):
        """
        Overridden method to perform custom checks before creating an AircraftPart.
        - Verifies if the part belongs to the correct aircraft type using PartBelongsToAircraftType.
        - Ensures that the part is not already assigned to another aircraft using PartIsNotUsedInOtherAircraft.
        - Raises PermissionDenied if any validation fails.
        """
        if self.request.user.is_staff:
            serializer.save()
            return

        errors = []

        # Check if the part belongs to the correct aircraft type
        if not PartBelongsToAircraftType().has_permission(self.request, self):
            errors.append("This part does not belong to this type of aircraft.")

        # Check if the part is already used in another aircraft
        if not PartIsNotUsedInOtherAircraft().has_permission(self.request, self):
            errors.append("This part is already used in another aircraft.")

        # If there are any errors, raise PermissionDenied with all error messages
        if errors:
            raise PermissionDenied(" ".join(errors))

        # Save the serializer if all checks pass
        serializer.save()


class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        team_id = request.data.get('team')

        # User oluştur
        user = User.objects.create_user(username=username, password=password)

        try:
            team = Team.objects.get(id=team_id)
            personnel = Personnel.objects.create(user=user, team=team)
            personnel_serializer = PersonnelSerializer(personnel)
            return Response(personnel_serializer.data, status=status.HTTP_201_CREATED)
        except Team.DoesNotExist:
            return Response({"error": "Team not found."}, status=status.HTTP_400_BAD_REQUEST)
