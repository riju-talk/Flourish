from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Profile, Plant, CareTask, PlantCareLog, AIChatSession, AIChatMessage

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'user', 'full_name', 'created_at', 'updated_at']

class PlantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    plant_type_display = serializers.CharField(source='get_plant_type_display', read_only=True)
    sunlight_requirement_display = serializers.CharField(source='get_sunlight_requirement_display', read_only=True)
    health_status_display = serializers.CharField(source='get_health_status_display', read_only=True)
    
    class Meta:
        model = Plant
        fields = [
            'id', 'name', 'scientific_name', 'plant_type', 'plant_type_display',
            'sunlight_requirement', 'sunlight_requirement_display',
            'watering_frequency', 'fertilizing_frequency',
            'location', 'room',
            'health_status', 'health_status_display',
            'last_watered', 'last_fertilized', 'next_watering',
            'image_url', 'notes', 'user',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'next_watering']
    
    def validate_watering_frequency(self, value):
        if value < 0:
            raise serializers.ValidationError("Watering frequency must be a positive number")
        return value
    
    def validate_fertilizing_frequency(self, value):
        if value < 0:
            raise serializers.ValidationError("Fertilizing frequency must be a positive number")
        return value

class CareTaskSerializer(serializers.ModelSerializer):
    plant = PlantSerializer(read_only=True)

    class Meta:
        model = CareTask
        fields = ['id', 'plant', 'task_type', 'due_date', 'completed', 'created_at', 'updated_at']

class PlantCareLogSerializer(serializers.ModelSerializer):
    plant = PlantSerializer(read_only=True)
    task = CareTaskSerializer(read_only=True)

    class Meta:
        model = PlantCareLog
        fields = ['id', 'plant', 'task', 'notes', 'created_at']

class AIChatSessionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = AIChatSession
        fields = ['id', 'user', 'created_at', 'updated_at']

class AIChatMessageSerializer(serializers.ModelSerializer):
    session = AIChatSessionSerializer(read_only=True)

    class Meta:
        model = AIChatMessage
        fields = ['id', 'session', 'content', 'is_user', 'created_at']
