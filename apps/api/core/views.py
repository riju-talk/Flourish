from django.contrib.auth import get_user_model
from django.http import JsonResponse
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from datetime import timedelta
from django.utils import timezone

from .models import (
    Profile,
    Plant,
    CareTask,
    PlantCareLog,
)
from .serializers import (
    ProfileSerializer,
    PlantSerializer,
    CareTaskSerializer,
    PlantCareLogSerializer,
)

User = get_user_model()

def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({"status": "ok"})
 

class ProfileViewSet(viewsets.ModelViewSet):
    print("HEloo")
    """API endpoint for user profiles"""
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    
    def get_queryset(self):
        return Profile.objects.all()
    
    def get_object(self):
        return super().get_queryset().first()
    
    def perform_update(self, serializer):
        serializer.save()

class PlantViewSet(viewsets.ModelViewSet):
    """API endpoint for plants"""
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer
    
    def get_queryset(self):
        return Plant.objects.all()
    
    def perform_create(self, serializer):
        serializer.save()

class CareTaskViewSet(viewsets.ModelViewSet):
    """API endpoint for care tasks"""
    queryset = CareTask.objects.all()
    serializer_class = CareTaskSerializer
    
    def get_queryset(self):
        return CareTask.objects.all()
    
    def perform_create(self, serializer):
        serializer.save()

class PlantCareLogViewSet(viewsets.ModelViewSet):
    """API endpoint for plant care logs"""
    queryset = PlantCareLog.objects.all()
    serializer_class = PlantCareLogSerializer
    
    def get_queryset(self):
        return PlantCareLog.objects.all()
    
    def perform_create(self, serializer):
        serializer.save()


class CalendarView(APIView):
    permission_classes = [AllowAny]

    def get_weather_forecast(self, location):
        forecast = {}
        today = timezone.now().date()
        for i in range(14):
            date = today + timedelta(days=i)
            forecast[date.isoformat()] = {
                'condition': 'clear',
                'precipitation': 0,
            }
        return forecast

    def generate_care_tasks(self, plant, start_date, end_date, weather_forecast):
        tasks = []

        # Watering tasks
        current_date = start_date
        while current_date <= end_date:
            weather = weather_forecast.get(current_date.isoformat(), {})
            if weather.get('precipitation', 0) < 5:
                tasks.append({
                    'date': current_date.isoformat(),
                    'task_type': 'watering',
                    'plant_id': str(plant.id),
                    'plant_name': plant.name,
                    'description': f'Water {plant.name}',
                })
            current_date += timedelta(days=plant.watering_frequency_days or 7)

        # Fertilizing tasks
        current_date = start_date
        while current_date <= end_date:
            tasks.append({
                'date': current_date.isoformat(),
                'task_type': 'fertilizing',
                'plant_id': str(plant.id),
                'plant_name': plant.name,
                'description': f'Fertilize {plant.name}',
            })
            current_date += timedelta(days=plant.fertilizing_frequency_days or 30)

        return tasks

    def get(self, request):
        try:
            start_date = timezone.now().date()
            end_date = start_date + timedelta(days=14)

            weather_forecast = self.get_weather_forecast('')  # Location optional for now
            plants = Plant.objects.all()

            all_tasks = []
            for plant in plants:
                all_tasks.extend(
                    self.generate_care_tasks(plant, start_date, end_date, weather_forecast)
                )

            all_tasks.sort(key=lambda x: x['date'])

            return Response({
                'status': 'success',
                'data': all_tasks,
                'meta': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'total_tasks': len(all_tasks)
                }
            })

        except Exception as e:
            return Response(
                {'status': 'error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )