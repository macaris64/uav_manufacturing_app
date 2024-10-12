from django.contrib.auth.models import User
from rest_framework import serializers
from manufacturing.models import Aircraft, Team, Part, Personnel, AircraftPart

class AircraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aircraft
        fields = '__all__'

class TeamSerializer(serializers.ModelSerializer):
    name = serializers.ChoiceField(choices=[('Wing Team', 'Wing Team'),
                                            ('Body Team', 'Body Team'),
                                            ('Tail Team', 'Tail Team'),
                                            ('Avionics Team', 'Avionics Team'),
                                            ('Assembly Team', 'Assembly Team')])

    class Meta:
        model = Team
        fields = ['id', 'name', 'description']

class PartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Part
        fields = ['id', 'name', 'aircraft_type', 'created_at']

    def create(self, validated_data):
        return Part.objects.create(**validated_data)

class PersonnelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Personnel
        fields = '__all__'

class AircraftPartSerializer(serializers.ModelSerializer):
    class Meta:
        model = AircraftPart
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser']
