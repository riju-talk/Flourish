import os
from typing import Dict, List, Optional
from langchain_groq import ChatGroq
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from django.conf import settings

# Initialize the Groq chat model
chat = ChatGroq(
    temperature=0.7,
    model_name="meta-llama/llama-4-scout-17b-16e-instruct",
    api_key=os.getenv("GROQ_API_KEY")
)

# System prompt for plant care assistant
SYSTEM_PROMPT = """You are an expert plant care assistant with deep knowledge of horticulture, 
plant diseases, and gardening best practices. You help users care for their plants by providing 
personalized advice based on their specific plant types, locations, and conditions.

When answering questions:
1. Be concise but thorough
2. Provide actionable advice
3. Consider the user's location and climate if mentioned
4. For plant identification, ask for clear photos if needed
5. For disease diagnosis, ask about symptoms and examine photos carefully
6. Always be friendly and encouraging

If you don't know something, it's okay to say so and suggest general best practices."""

# Initialize conversation memory
memory = ConversationBufferMemory(return_messages=True)

# Set up the prompt template
prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{input}")
])

# Create the conversation chain
conversation = ConversationChain(
    llm=chat,
    memory=memory,
    prompt=prompt,
    verbose=True
)

def get_plant_care_advice(plant_type: Optional[str], question: str, context: Optional[Dict] = None) -> Dict:
    """
    Get plant care advice for a specific plant type, or general advice if plant_type is not given.
    
    Args:
        plant_type: Optional; Type of plant (e.g., 'snake plant')
        question: User's question about plant care
        context: Optional; Additional context like location, symptoms, etc.
        
    Returns:
        Dict containing the AI's response and any follow-up suggestions
    """
    context_str = ""
    if context:
        context_str = "\nContext:\n"
        for key, value in context.items():
            context_str += f"- {key}: {value}\n"

    if plant_type:
        full_prompt = f"""Plant Type: {plant_type}
{context_str}
Question: {question}

Please provide specific care advice for this plant based on the information given."""
    else:
        full_prompt = f"""{context_str}
General Plant Care Question: {question}

Please provide helpful advice or general best practices for this plant-related question."""

    try:
        response = conversation.predict(input=full_prompt)
        return {
            'status': 'success',
            'answer': response,
            'suggestions': generate_follow_up_suggestions(question, response)
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }


def identify_plant_from_image(image_url: str) -> Dict:
    """
    Identify a plant from an image URL.
    
    Args:
        image_url: URL of the plant image
        
    Returns:
        Dict containing the plant identification and care information
    """
    try:
        # In a real implementation, you would process the image here
        # For now, we'll just return a mock response
        prompt = f"""I have a plant image at {image_url}. 
        Please identify the plant and provide basic care instructions.
        
        Since you can't actually see the image, provide general guidance 
        on how to identify plants and what information would be helpful to provide."""
        
        response = conversation.predict(input=prompt)
        return {
            'status': 'success',
            'plant_info': {
                'common_name': 'Unknown Plant',
                'scientific_name': 'Unknown',
                'confidence': 0.0
            },
            'care_instructions': response,
            'suggestions': [
                'Upload a clear photo of the plant',
                'Describe the leaves, flowers, and size',
                'Mention any distinctive features'
            ]
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Failed to identify plant: {str(e)}'
        }

def generate_follow_up_suggestions(question: str, response: str) -> List[str]:
    suggestions = []
    
    if 'water' in question.lower():
        suggestions.extend([
            'How often should I water this plant?',
            'What are signs of overwatering?',
            'What type of water is best?'
        ])
    
    if 'light' in question.lower():
        suggestions.extend([
            'What kind of light does this plant need?',
            'Can it tolerate direct sunlight?',
            'How do I know if it\'s getting too much light?'
        ])
    
    if not suggestions:
        suggestions = [
            'What are common problems with this plant?',
            'How often should I fertilize it?',
            'When is the best time to repot?'
        ]
    
    return suggestions[:3]  # Return max 3 suggestions
