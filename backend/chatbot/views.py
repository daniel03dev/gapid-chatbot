from rest_framework import status, viewsets, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Avg, Count, Q
from datetime import timedelta
import os

from .models import Conversation, Message, QueryLog, AuditLog
from .serializers import (
    ConversationListSerializer,
    ConversationDetailSerializer,
    MessageSerializer,
    QueryLogSerializer,
    QueryLogListSerializer,
    AuditLogSerializer,
    MetricsSerializer,
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
        
        # Preparar metadata del request
        request_meta = {
            'ip_address': get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', '')
        }
        
        # Obtener respuesta del chat service con logging
        chat_response = get_chat_service().answer_question(
            message_text, 
            k=3,
            log_to_db=True,
            conversation_id=conversation_id,
            request_meta=request_meta
        )
        
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
            'confidence_score': chat_response.get('confidence_score', 0),
            'response_time': chat_response.get('response_time', 0),
            'chunks_retrieved': chat_response.get('chunks_retrieved', 0)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        import traceback
        print(f"ERROR en chat_view: {str(e)}")
        traceback.print_exc()
        
        # Registrar error en auditoría
        ChatService.log_audit_event(
            event_type='error',
            description=f'Error en chat_view: {str(e)}',
            severity='error',
            metadata={'traceback': traceback.format_exc()}
        )
        
        return Response({
            'error': f'Error procesando el chat: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_client_ip(request):
    """Extrae la IP del cliente del request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@api_view(['GET'])
def query_logs_view(request):
    """
    Endpoint para listar registros de consultas.
    
    Query params:
    - limit: número de registros (default 50)
    - conversation_id: filtrar por conversación
    """
    try:
        limit = int(request.query_params.get('limit', 50))
        conversation_id = request.query_params.get('conversation_id')
        
        queryset = QueryLog.objects.all()
        
        if conversation_id:
            queryset = queryset.filter(conversation_id=conversation_id)
        
        queryset = queryset[:limit]
        
        serializer = QueryLogListSerializer(queryset, many=True)
        
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def query_log_detail_view(request, log_id):
    """Endpoint para obtener detalles completos de un registro de consulta."""
    try:
        query_log = get_object_or_404(QueryLog, id=log_id)
        serializer = QueryLogSerializer(query_log)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def audit_logs_view(request):
    """
    Endpoint para listar registros de auditoría.
    
    Query params:
    - limit: número de registros (default 50)
    - event_type: filtrar por tipo de evento
    - severity: filtrar por severidad
    """
    try:
        limit = int(request.query_params.get('limit', 50))
        event_type = request.query_params.get('event_type')
        severity = request.query_params.get('severity')
        
        queryset = AuditLog.objects.all()
        
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        if severity:
            queryset = queryset.filter(severity=severity)
        
        queryset = queryset[:limit]
        
        serializer = AuditLogSerializer(queryset, many=True)
        
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def metrics_view(request):
    """
    Endpoint para obtener métricas y estadísticas del sistema.
    """
    try:
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        last_30d = now - timedelta(days=30)
        
        # Consultas por periodo
        total_queries = QueryLog.objects.count()
        queries_24h = QueryLog.objects.filter(created_at__gte=last_24h).count()
        queries_7d = QueryLog.objects.filter(created_at__gte=last_7d).count()
        queries_30d = QueryLog.objects.filter(created_at__gte=last_30d).count()
        
        # Métricas de rendimiento
        avg_metrics = QueryLog.objects.aggregate(
            avg_response_time=Avg('response_time'),
            avg_chunks=Avg('chunks_retrieved'),
            avg_feedback=Avg('feedback_score')
        )
        
        # Conversaciones totales
        total_conversations = Conversation.objects.count()
        
        # Errores
        total_errors = AuditLog.objects.filter(
            Q(severity='error') | Q(severity='critical')
        ).count()
        
        # Horas más activas (últimos 7 días)
        queries_by_hour = QueryLog.objects.filter(
            created_at__gte=last_7d
        ).extra(
            select={'hour': 'EXTRACT(hour FROM created_at)'}
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        most_active_hours = [
            {'hour': int(item['hour']), 'count': item['count']}
            for item in queries_by_hour
        ]
        
        metrics_data = {
            'total_queries': total_queries,
            'total_conversations': total_conversations,
            'avg_response_time': avg_metrics['avg_response_time'] or 0.0,
            'avg_chunks_retrieved': avg_metrics['avg_chunks'] or 0.0,
            'queries_last_24h': queries_24h,
            'queries_last_7d': queries_7d,
            'queries_last_30d': queries_30d,
            'avg_feedback_score': avg_metrics['avg_feedback'],
            'total_errors': total_errors,
            'most_active_hours': most_active_hours
        }
        
        serializer = MetricsSerializer(data=metrics_data)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
