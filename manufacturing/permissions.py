from django.utils.formats import number_format
from rest_framework.permissions import BasePermission
from manufacturing.models import Part, Team, AircraftPart


class CanOnlyCreateAssignedPart(BasePermission):
    """
    Restricts the creation of parts to those that a specific team is authorized to create.
    """

    def has_permission(self, request, view):
        # Only applies to the 'create' action
        if view.action == 'create':
            part_type = request.data.get('name')
            team_id = request.data.get('team')

            # Define part types allowed for each team
            allowed_parts = {
                'Wing Team': 'WING',
                'Body Team': 'BODY',
                'Tail Team': 'TAIL',
                'Avionics Team': 'AVIONICS'
            }

            # Retrieve the team based on the provided team_id
            team = Team.objects.filter(id=team_id).first()
            # If the team is found and its assigned part does not match the requested part type, deny permission
            if team and team.name in allowed_parts and allowed_parts[team.name] != part_type:
                return False  # Permission denied
        return True  # Permission granted if conditions are met


class PartIsNotUsedInOtherAircraft(BasePermission):
    """
    Prevents a part from being reused in another aircraft.
    """

    def has_permission(self, request, view):
        # Only applies to the 'create' action
        if view.action == 'create':
            part_id = request.data.get('part')
            # Check if the part already has an association with any aircraft
            return not AircraftPart.objects.filter(part_id=part_id).exists()  # True if unused, False if used
        return True  # Permission granted if not a 'create' action


class PartBelongsToAircraftType(BasePermission):
    """
    Ensures that a part is being assigned to the correct type of aircraft.
    """

    def has_permission(self, request, view):
        # Only applies to the 'create' action
        if view.action == 'create':
            part_id = request.data.get('part')
            aircraft_id = request.data.get('aircraft')

            # Retrieve the part based on part_id
            part = Part.objects.filter(id=part_id).first()

            # Deny permission if the part's aircraft type does not match the requested aircraft
            if part and number_format(part.aircraft.id) != number_format(aircraft_id):
                return False
        return True  # Permission granted if conditions are met
