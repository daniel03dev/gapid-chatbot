from rest_framework import status, viewsets, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
import os

from .models import Conversation, Message
from .serializers import (
    ConversationListSerializer,
    ConversationDetailSerializer,
    MessageSerializer,
)
from .services.chat_service import ChatService

# Lazy loading del servicio de chat
_chat_service = None

def get_chat_service():
    """Obtiene la instancia del servicio de chat (lazy loading)."""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService(
            documents_dir=os.getenv('DOCUMENTS_DIR', 'data/documents'),
            vectors_dir=os.getenv('VECTORS_DIR', 'data/vectors')
        )
        # Intentar cargar índice si existe
        _chat_service.load_index()
    return _chat_service


@api_view(['GET'])
def health_check(request):
    """Endpoint de health check para verificar que el servicio está activo."""
    return Response({
        'status': 'ok',
        'message': 'Backend GAPID Chatbot está operacional'
    }, status=status.HTTP_200_OK)


class ConversationListCreateView(generics.ListCreateAPIView):
    """
    GET: Listar todas las conversaciones.
    POST: Crear una nueva conversación.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationListSerializer
    permission_classes = [AllowAny]
    
    def perform_create(self, serializer):
        """Crear una nueva conversación."""
        serializer.save()


class ConversationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Obtener detalles de una conversación (incluye todos sus mensajes).
    PUT/PATCH: Actualizar conversación.
    DELETE: Eliminar conversación.
    """
    queryset = Conversation.objects.all()
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        """Usar DetailSerializer para GET, ListSerializer para otros."""
        if self.request.method == 'GET':
            return ConversationDetailSerializer
        return ConversationListSerializer


class MessageListCreateView(generics.ListCreateAPIView):
    """
    GET: Listar todos los mensajes de una conversación.
    POST: Crear un nuevo mensaje en una conversación.
    """
    serializer_class = MessageSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Filtrar mensajes por conversación."""
        conversation_id = self.kwargs.get('conversation_id')
        return Message.objects.filter(conversation_id=conversation_id).order_by('created_at')
    
    def perform_create(self, serializer):
        """Crear un mensaje asociado a la conversación."""
        conversation_id = self.kwargs.get('conversation_id')
        conversation = get_object_or_404(Conversation, id=conversation_id)
        serializer.save(conversation=conversation)


@api_view(['POST'])
def chat_view(request):
    """
    Endpoint de chat: procesa mensajes del usuario y devuelve respuesta.
    
    Esperado en el request:
    {
        "message": "Tu pregunta aquí",
        "conversation_id": 1  # opcional
    }
    """
    try:
        message_text = request.data.get('message', '').strip()
        conversation_id = request.data.get('conversation_id')
        
        if not message_text:
            return Response({
                'error': 'El mensaje no puede estar vacío'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Si no hay conversación, crear una
        if not conversation_id:
            conversation = Conversation.objects.create()
            conversation_id = conversation.id
        else:
            conversation = get_object_or_404(Conversation, id=conversation_id)
        
        # Obtener respuesta del chat service
        chat_response = get_chat_service().answer_question(message_text, k=3)
        
        # Guardar mensaje del usuario
        user_message = Message.objects.create(
            conversation=conversation,
            role='user',
            content=message_text
        )
        
        # Guardar mensaje del asistente
        assistant_message = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=chat_response['answer']
        )
        
        return Response({
            'conversation_id': conversation_id,
            'user_message_id': user_message.id,
            'assistant_message_id': assistant_message.id,
            'answer': chat_response['answer'],
            'sources': chat_response.get('sources', []),
            'confidence_score': chat_response.get('confidence_score', 0)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        import traceback
        print(f"ERROR en chat_view: {str(e)}")
        traceback.print_exc()
        return Response({
            'error': f'Error procesando el chat: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
