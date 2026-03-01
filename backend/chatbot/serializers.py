from rest_framework import serializers
from .models import Conversation, Message, QueryLog, AuditLog


class MessageSerializer(serializers.ModelSerializer):
    """Serializador para mensajes individuales."""
    
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'role', 'role_display', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']


class ConversationListSerializer(serializers.ModelSerializer):
    """Serializador para listar conversaciones (sin mensajes anidados)."""
    
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'created_at', 'updated_at', 'message_count']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_message_count(self, obj):
        return obj.messages.count()


class ConversationDetailSerializer(serializers.ModelSerializer):
    """Serializador para detalles de conversación (con mensajes anidados)."""
    
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'created_at', 'updated_at', 'messages', 'message_count']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_message_count(self, obj):
        return obj.messages.count()


class QueryLogSerializer(serializers.ModelSerializer):
    """Serializador para registros de consultas."""
    
    conversation_id = serializers.SerializerMethodField()
    
    class Meta:
        model = QueryLog
        fields = [
            'id',
            'conversation_id',
            'user_query',
            'assistant_response',
            'response_time',
            'chunks_retrieved',
            'context_used',
            'created_at',
            'ip_address',
            'user_agent',
            'feedback_score'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_conversation_id(self, obj):
        return obj.conversation.id if obj.conversation else None


class QueryLogListSerializer(serializers.ModelSerializer):
    """Serializador simplificado para listar consultas (sin contexto completo)."""
    
    conversation_id = serializers.SerializerMethodField()
    query_preview = serializers.SerializerMethodField()
    response_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = QueryLog
        fields = [
            'id',
            'conversation_id',
            'query_preview',
            'response_preview',
            'response_time',
            'chunks_retrieved',
            'created_at',
            'feedback_score'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_conversation_id(self, obj):
        return obj.conversation.id if obj.conversation else None
    
    def get_query_preview(self, obj):
        """Retorna preview de 100 caracteres."""
        return obj.user_query[:100] + '...' if len(obj.user_query) > 100 else obj.user_query
    
    def get_response_preview(self, obj):
        """Retorna preview de 100 caracteres."""
        return obj.assistant_response[:100] + '...' if len(obj.assistant_response) > 100 else obj.assistant_response


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializador para registros de auditoría."""
    
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id',
            'event_type',
            'event_type_display',
            'description',
            'metadata',
            'ip_address',
            'user_agent',
            'severity',
            'severity_display',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class MetricsSerializer(serializers.Serializer):
    """Serializador para estadísticas y métricas del sistema."""
    
    total_queries = serializers.IntegerField()
    total_conversations = serializers.IntegerField()
    avg_response_time = serializers.FloatField()
    avg_chunks_retrieved = serializers.FloatField()
    queries_last_24h = serializers.IntegerField()
    queries_last_7d = serializers.IntegerField()
    queries_last_30d = serializers.IntegerField()
    avg_feedback_score = serializers.FloatField(allow_null=True)
    total_errors = serializers.IntegerField()
    most_active_hours = serializers.ListField(child=serializers.DictField())
