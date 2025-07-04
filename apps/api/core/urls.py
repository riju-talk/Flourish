# core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    health_check,
    LoginView,
    LogoutView,
    UserProfileView,
    ProfileViewSet,
    PlantViewSet,
    CalendarView,
)

router = DefaultRouter()
router.register(r'profiles', ProfileViewSet)
router.register(r'plants', PlantViewSet)

urlpatterns = [
    # API endpoints
    path('', include(router.urls)),
    
    # Authentication endpoints
    path('health/', health_check, name='health-check'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/me/', UserProfileView.as_view(), name='user-profile'),
    
    # Calendar endpoint
    path('calendar/', CalendarView.as_view(), name='calendar'),
]
