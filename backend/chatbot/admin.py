# Admin configuration for chatbot models
from django.contrib import admin
from .models import Conversation, Message, QueryLog, AuditLog


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'updated_at', 'message_count')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('id',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Cantidad de Mensajes'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'role', 'created_at', 'content_preview')
    list_filter = ('role', 'created_at', 'conversation')
    search_fields = ('content', 'conversation__id')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Contenido'


@admin.register(QueryLog)
class QueryLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'created_at', 'response_time', 'chunks_retrieved', 'feedback_score', 'query_preview')
    list_filter = ('created_at', 'feedback_score', 'chunks_retrieved')
    search_fields = ('user_query', 'assistant_response', 'conversation__id')
    readonly_fields = ('created_at', 'response_time', 'chunks_retrieved', 'context_used', 'ip_address', 'user_agent')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('conversation', 'created_at')
        }),
        ('Consulta y Respuesta', {
            'fields': ('user_query', 'assistant_response')
        }),
        ('Métricas', {
            'fields': ('response_time', 'chunks_retrieved', 'feedback_score')
        }),
        ('Contexto', {
            'fields': ('context_used',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    def query_preview(self, obj):
        return obj.user_query[:50] + '...' if len(obj.user_query) > 50 else obj.user_query
    query_preview.short_description = 'Consulta'


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'event_type', 'severity', 'created_at', 'description_preview')
    list_filter = ('event_type', 'severity', 'created_at')
    search_fields = ('description', 'event_type')
    readonly_fields = ('created_at', 'metadata', 'ip_address', 'user_agent')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('event_type', 'severity', 'created_at')
        }),
        ('Descripción', {
            'fields': ('description',)
        }),
        ('Metadata', {
            'fields': ('metadata', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    def description_preview(self, obj):
        return obj.description[:80] + '...' if len(obj.description) > 80 else obj.description
    description_preview.short_description = 'Descripción'
