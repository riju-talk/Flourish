# core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    health_check,
    ProfileViewSet,
    PlantViewSet,
    CareTaskViewSet,
    PlantCareLogViewSet,
    AIChatSessionViewSet,
    AIChatMessageViewSet,
    CalendarView,
)

router = DefaultRouter()
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'plants', PlantViewSet, basename='plant')
router.register(r'care-tasks', CareTaskViewSet, basename='caretask')
router.register(r'plant-care-logs', PlantCareLogViewSet, basename='plantcarelog')
router.register(r'ai-chat/sessions', AIChatSessionViewSet, basename='aichatsession')
router.register(r'ai-chat/messages', AIChatMessageViewSet, basename='aichatmessage')

urlpatterns = [
    # API endpoints
    path('', include(router.urls)),
    
    # Health check endpoint
    path('health/', health_check, name='health-check'),
    
    # Calendar endpoint
    path('calendar/', CalendarView.as_view(), name='calendar'),
]
