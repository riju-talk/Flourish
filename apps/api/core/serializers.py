from rest_framework import serializers
from .models import (
    Profile,
    Plant,
    CareTask,
    PlantCareLog,
)
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']
        read_only_fields = ['id', 'email']

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Profile
        fields = ['id', 'user', 'full_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class PlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = [
            'id', 'name', 'scientific_name', 'plant_type',
            'sunlight_requirement', 'watering_frequency', 'fertilizing_frequency',
            'location', 'room', 'health_status', 'last_watered', 'last_fertilized',
            'next_watering', 'image_url', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'next_watering']

class PlantNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = ['id', 'name']
        read_only_fields = ['id', 'name']

class CareTaskSerializer(serializers.ModelSerializer):
    plants = PlantNameSerializer(source='plant', read_only=True)

    class Meta:
        model = CareTask
        fields = ['id', 'title', 'task_type', 'scheduled_date', 'status', 'plants']

class PlantCareLogSerializer(serializers.ModelSerializer):
    plant_name = serializers.CharField(source='plant.name', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    
    class Meta:
        model = PlantCareLog
        fields = [
            'id', 'plant', 'plant_name', 'task', 'task_title', 'task_type',
            'notes', 'performed_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']