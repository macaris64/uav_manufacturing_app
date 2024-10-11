from rest_framework import serializers
from manufacturing.models import Aircraft, Team, Part, Personnel, AircraftPart

class AircraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aircraft
        fields = '__all__'

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'

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
