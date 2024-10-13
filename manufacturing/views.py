from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets, status
from rest_framework.decorators import action
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

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # Uçak parçalarını da ekleyin
        parts = instance.aircraftpart_set.select_related('part').all()  # 'part' ile ilişkilendirilmiş parçaları seçin
        serialized_parts = PartSerializer([part.part for part in parts], many=True).data  # part nesnelerini al

        data = serializer.data
        data['parts'] = serialized_parts  # Parçaları yanıt verisine ekleyin
        return Response(data)


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
        """
        Overridden method to handle custom part creation logic.
        - Retrieves the user's associated team and checks if they can produce the requested part.
        - Raises ValidationError if the team is not authorized to create the specified part.
        """
        user_team = self.request.user.personnel.team
        part_name = serializer.validated_data['name']
        if user_team.can_produce_part({'name': part_name}):
            serializer.save()
        else:
            raise ValidationError("You are not authorized to produce this type of part.")

    def get_queryset(self):
        """
        Retrieves the queryset of parts based on the user's team.
        - If the user's team is the Assembly Team, returns all parts.
        - Otherwise, filters parts to only include those that the user's team can produce.
        """
        user_team = self.request.user.personnel.team

        # If the user's team is Assembly Team, return all parts
        if user_team.name == Team.ASSEMBLY_TEAM:
            return self.queryset

        # Otherwise, filter based on team
        return self.queryset.filter(name__in=[
            Part.WING if user_team.name == Team.WING_TEAM else None,
            Part.BODY if user_team.name == Team.BODY_TEAM else None,
            Part.TAIL if user_team.name == Team.TAIL_TEAM else None,
            Part.AVIONICS if user_team.name == Team.AVIONICS_TEAM else None,
        ]).exclude(name=None)

    @action(detail=False, methods=['post'], url_path='bulk-delete')
    def bulk_delete(self, request):
        """
        Custom action to handle bulk deletion of parts.
        - Accepts a list of part IDs and ensures that only unused parts can be deleted.
        - Raises ValidationError if any parts are in use.
        """
        part_ids = request.data.get('ids', [])

        parts_to_delete = Part.objects.filter(id__in=part_ids, is_used=False)
        used_parts = Part.objects.filter(id__in=part_ids, is_used=True)

        if used_parts.exists():
            used_names = ", ".join([part.name for part in used_parts])
            raise ValidationError(f"Cannot delete parts in use: {used_names}")

        parts_to_delete.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
    """
    View for retrieving the current user's information.
    Requires authentication.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Handles GET requests for the current user's information.
        - Serializes the user object and returns it in the response.
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class RegisterView(APIView):
    """
    View for handling user registration.
    Allows unauthenticated users to create a new user account.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handles POST requests for user registration.
        - Creates a new User object and associates it with Personnel.
        - Returns the created Personnel object or an error if the team is not found.
        """
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
