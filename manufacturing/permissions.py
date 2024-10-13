from rest_framework.permissions import BasePermission
from manufacturing.models import Part, Team, AircraftPart, Aircraft


class CanOnlyCreateAssignedPart(BasePermission):
    """
    Restricts the creation of parts to those that a specific team is authorized to create.
    """

    def has_permission(self, request, view):
        """
        Determines if the user has permission to create a part based on the team and part type.
        """
        # Only applies to the 'create' action
        if view.action == 'create':
            part_type = request.data.get('name')  # Retrieve the part type from the request data
            team_id = request.data.get('team')  # Retrieve the team ID from the request data

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
        """
        Checks if a part is already used in any aircraft to determine permission for creating an AircraftPart.
        """
        # Only applies to the 'create' action
        if view.action == 'create':
            part_id = request.data.get('part')  # Retrieve the part ID from the request data
            # Check if the part already has an association with any aircraft
            part_in_use = AircraftPart.objects.filter(part_id=part_id).exists()
            part_is_used = Part.objects.filter(id=part_id, is_used=True).exists()
            return not (part_in_use and part_is_used)  # True if unused, False if used
        return True  # Permission granted if not a 'create' action


class PartBelongsToAircraftType(BasePermission):
    """
    Ensures that a part is being assigned to the correct type of aircraft.
    """

    def has_permission(self, request, view):
        """
        Verifies that the part's aircraft type matches the specified aircraft type in the request.
        """
        # Only applies to the 'create' action
        if view.action == 'create':
            part_id = request.data.get('part')  # Retrieve the part ID from the request data
            aircraft_id = request.data.get('aircraft')  # Retrieve the aircraft ID from the request data

            # Retrieve the part based on part_id
            part = Part.objects.filter(id=part_id).first()  # Get the part by ID
            aircraft = Aircraft.objects.filter(id=aircraft_id).first()  # Get the aircraft by ID

            # Deny permission if the part's aircraft type does not match the requested aircraft
            if part and part.aircraft_type != aircraft.name:
                return False  # Permission denied
        return True  # Permission granted if conditions are met
