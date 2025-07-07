# core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    health_check,
    ProfileViewSet,
    PlantViewSet,
    CareTaskViewSet,
    PlantCareLogViewSet,
    CalendarView,
)

router = DefaultRouter()
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'plants', PlantViewSet, basename='plant')
router.register(r'care-tasks', CareTaskViewSet, basename='caretask')
router.register(r'plant-care-logs', PlantCareLogViewSet, basename='plantcarelog')
urlpatterns = [
    # API endpoints
    path('', include(router.urls)),
    # Health check endpoint
    path('health/', health_check, name='health-check'),
    path('calendar-events/', CalendarView.as_view(), name='calendar'),
]
