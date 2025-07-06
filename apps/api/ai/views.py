# ai/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, JSONParser
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from .groq_chain import get_plant_care_advice, identify_plant_from_image

@api_view(['POST'])
def ask_ai_view(request):
    question = request.data.get("question", "")
    return Response({"message": f"You asked: {question}"})

class AIChatView(APIView):
    parser_classes = (MultiPartParser, JSONParser)
    
    def post(self, request, *args, **kwargs):
        try:
            message = request.data.get('message', '').strip()
            image = request.FILES.get('image')
            plant_type = request.data.get('plant_type', '').strip()
            context = request.data.get('context', {})
            
            if not message and not image:
                return Response(
                    {'error': 'Either message or image is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Handle image upload if present
            image_url = None
            if image:
                # Save the uploaded file
                file_name = default_storage.save(
                    f"plant_images/{image.name}",
                    ContentFile(image.read())
                )
                image_url = f"{settings.MEDIA_URL}{file_name}"
                
                # If no message was provided, assume it's a plant identification request
                if not message:
                    return self.handle_plant_identification(image_url)
            
            # Process the message with the AI
            return self.handle_message(message, plant_type, context, image_url)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def handle_message(self, message: str, plant_type: str, context: dict, image_url: str = None) -> Response:
        try:
            if image_url:
                context['image_url'] = image_url
            
            response = get_plant_care_advice(
                plant_type=plant_type,
                question=message,
                context=context
            )
            
            return Response(response)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to process message: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def handle_plant_identification(self, image_url: str) -> Response:
        try:
            response = identify_plant_from_image(image_url)
            return Response(response)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to identify plant: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
