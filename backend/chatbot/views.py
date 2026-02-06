from rest_framework import status, viewsets, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

from .models import Conversation, Message
from .serializers import (
    ConversationListSerializer,
    ConversationDetailSerializer,
    MessageSerializer,
)


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
