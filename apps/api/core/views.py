import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from django.utils import timezone
from django.middleware.csrf import get_token
from django.core.exceptions import PermissionDenied

from .models import (
    Profile,
    Plant,
    CareTask,
    PlantCareLog,
    AIChatSession,
    AIChatMessage,
)
from .serializers import (
    ProfileSerializer,
    PlantSerializer,
    CareTaskSerializer,
    PlantCareLogSerializer,
    AIChatSessionSerializer,
    AIChatMessageSerializer,
)

User = get_user_model()

def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({"status": "ok"})

class SupabaseAuthView(APIView):
    """
    View to handle Supabase JWT authentication and exchange it for our backend tokens.
    Sets httpOnly cookies for both access and refresh tokens.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Get the Supabase JWT from the Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response(
                {'error': 'No valid token provided'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        supabase_token = auth_header.split(' ')[1]
        
        try:
            # Verify the Supabase JWT
            payload = jwt.decode(
                supabase_token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=['HS256'],
                audience='authenticated',
                options={"verify_aud": True}
            )
            
            # Get or create the user
            user, created = User.objects.get_or_create(
                email=payload.get('email'),
                defaults={
                    'username': payload.get('email'),
                    'is_active': True
                }
            )
            
            # Generate our backend tokens
            refresh = RefreshToken.for_user(user)
            
            # Prepare response with httpOnly cookies
            response = Response({
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'is_active': user.is_active
                }
            }, status=status.HTTP_200_OK)
            
            # Set httpOnly cookies
            response.set_cookie(
                key='access_token',
                value=str(refresh.access_token),
                httponly=True,
                secure=not settings.DEBUG,  # Only send over HTTPS in production
                samesite='Lax',
                max_age=60 * 60  # 1 hour
            )
            
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=60 * 60 * 24 * 7  # 7 days
            )
            
            # Set CSRF token in both cookie and response header
            csrf_token = get_token(request)
            response.set_cookie(
                key='csrftoken',
                value=csrf_token,
                httponly=False,  # Allow JavaScript to read CSRF token
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=60 * 60 * 24 * 7  # 7 days
            )
            response['X-CSRFToken'] = csrf_token
            
            return response
            
        except jwt.ExpiredSignatureError:
            return Response(
                {'error': 'Token has expired'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        except jwt.InvalidTokenError:
            return Response(
                {'error': 'Invalid token'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )            

class ProfileViewSet(viewsets.ModelViewSet):
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

class AIChatSessionViewSet(viewsets.ModelViewSet):
    """API endpoint for AI chat sessions"""
    queryset = AIChatSession.objects.all()
    serializer_class = AIChatSessionSerializer
    
    def get_queryset(self):
        return AIChatSession.objects.all()
    
    def perform_create(self, serializer):
        serializer.save()

class AIChatMessageViewSet(viewsets.ModelViewSet):
    """API endpoint for AI chat messages"""
    queryset = AIChatMessage.objects.all()
    serializer_class = AIChatMessageSerializer
    
    def get_queryset(self):
        return AIChatMessage.objects.all()
    
    def perform_create(self, serializer):
        serializer.save()

class CalendarView(APIView):
    """
    View to generate a calendar of upcoming plant care tasks.
    Returns tasks for the next 14 days, skipping rainy days for watering.
    """
    permission_classes = [AllowAny]
    
    def get_weather_forecast(self, location):
        """
        Get weather forecast for the next 14 days.
        In a real app, this would call a weather API.
        """
        forecast = {}
        today = timezone.now().date()
        for i in range(14):
            date = today + timedelta(days=i)
            # Mock data - in a real app, replace with actual API call
            forecast[date.isoformat()] = {
                'condition': 'clear',
                'precipitation': 0,
            }
        return forecast
    
    def generate_care_tasks(self, plant, start_date, end_date, weather_forecast):
        """Generate care tasks for a plant within a date range"""
        tasks = []
        
        # Generate watering tasks
        current_date = start_date
        while current_date <= end_date:
            # Skip watering on rainy days
            weather = weather_forecast.get(current_date.isoformat(), {})
            if weather.get('precipitation', 0) < 5:  # Only water if less than 5mm of rain
                tasks.append({
                    'date': current_date.isoformat(),
                    'task_type': 'water',
                    'plant_id': str(plant.id),
                    'plant_name': plant.name,
                    'description': f'Water {plant.name}',
                })
            current_date += timedelta(days=plant.watering_frequency or 7)  # Default to weekly
        
        # Generate fertilizing tasks
        current_date = start_date
        while current_date <= end_date:
            tasks.append({
                'date': current_date.isoformat(),
                'task_type': 'fertilize',
                'plant_id': str(plant.id),
                'plant_name': plant.name,
                'description': f'Fertilize {plant.name}',
            })
            current_date += timedelta(days=plant.fertilizing_frequency or 30)  # Default to monthly
            
        return tasks
    
    def get(self, request):
        try:
            start_date = timezone.now().date()
            end_date = start_date + timedelta(days=14)
            
            # Get weather forecast
            weather_forecast = self.get_weather_forecast('')
            
            # Get all plants
            plants = Plant.objects.all()
            
            # Generate tasks for each plant
            all_tasks = []
            for plant in plants:
                all_tasks.extend(self.generate_care_tasks(plant, start_date, end_date, weather_forecast))
            
            # Sort tasks by date
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