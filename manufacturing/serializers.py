from django.contrib.auth.models import User
from rest_framework import serializers
from manufacturing.models import Aircraft, Team, Part, Personnel, AircraftPart


class AircraftSerializer(serializers.ModelSerializer):
    """
    Serializer for the Aircraft model.
    Serializes all fields of the Aircraft model.
    """
    class Meta:
        model = Aircraft
        fields = '__all__'  # Include all fields in the serialization


class TeamSerializer(serializers.ModelSerializer):
    """
    Serializer for the Team model.
    Serializes team data, including a choice field for team names.
    """
    name = serializers.ChoiceField(choices=[
        ('Wing Team', 'Wing Team'),
        ('Body Team', 'Body Team'),
        ('Tail Team', 'Tail Team'),
        ('Avionics Team', 'Avionics Team'),
        ('Assembly Team', 'Assembly Team')
    ])

    class Meta:
        model = Team
        fields = ['id', 'name', 'description']  # Include id, name, and description fields


class PartSerializer(serializers.ModelSerializer):
    """
    Serializer for the Part model.
    Serializes essential fields of the Part model and includes a create method.
    """
    class Meta:
        model = Part
        fields = ['id', 'name', 'aircraft_type', 'created_at', 'is_used']  # Include specified fields

    def create(self, validated_data):
        """
        Creates and returns a new Part instance.
        """
        return Part.objects.create(**validated_data)  # Create Part with validated data


class PersonnelSerializer(serializers.ModelSerializer):
    """
    Serializer for the Personnel model.
    Serializes user and team information associated with personnel.
    """
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  # Link to User model
    team = TeamSerializer(read_only=True)  # Nested serializer for team information

    class Meta:
        model = Personnel
        fields = ['id', 'user', 'team', 'role']  # Include id, user, team, and role


class AircraftPartSerializer(serializers.ModelSerializer):
    """
    Serializer for the AircraftPart model.
    Serializes all fields of the AircraftPart model.
    """
    class Meta:
        model = AircraftPart
        fields = '__all__'  # Include all fields in the serialization


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    Includes personnel information associated with the user.
    """
    personnel = PersonnelSerializer(read_only=True)  # Nested serializer for personnel information

    class Meta:
        model = User
        fields = ['pk', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'personnel']  # Include specified user fields
