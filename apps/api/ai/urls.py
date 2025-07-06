from django.urls import path
from .views import ask_ai_view, AIChatView

urlpatterns = [
    path('ask/', ask_ai_view, name='ask_ai'),
    path('chat/', AIChatView.as_view(), name='ai_chat'),
]