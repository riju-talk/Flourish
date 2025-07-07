# ai/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser

from .groq_chain import get_plant_care_advice

# In‑memory chat for fallback
chat_store = {}

class ChatAPIView(APIView):
    parser_classes = [JSONParser]

    def get(self, request):
        email = request.query_params.get('email')
        if not email:
            return Response(
                {'error': 'email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        messages = chat_store.get(email, [
            {'role': 'assistant', 'content': '🌿 Welcome to HaritPal! I can help you care for your plants.'}
        ])
        return Response({'messages': messages})

    def post(self, request):
        email = request.data.get('email')
        question = request.data.get('question')
        plant_type = request.data.get('plant_type', '')   # optional
        context = request.data.get('context', {})

        if not email or not question:
            return Response(
                {'error': 'email and question are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ensure chat history exists
        if email not in chat_store:
            chat_store[email] = [{
                'role': 'assistant',
                'content': '🌿 Welcome to HaritPal! I can help you care for your plants.'
            }]

        # add user message
        chat_store[email].append({
            'role': 'user',
            'content': question
        })

        # get AI advice
        result = get_plant_care_advice(plant_type, question, context)

        if result.get('status') == 'success':
            answer = result['answer']
            suggestions = result.get('suggestions', [])

            chat_store[email].append({
                'role': 'assistant',
                'content': answer
            })

            return Response({
                'status': 'success',
                'answer': answer,
                'suggestions': suggestions,
                'messages': chat_store[email]
            })

        # AI chain error
        return Response(
            {'status': 'error', 'message': result.get('message', 'AI failed')},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
