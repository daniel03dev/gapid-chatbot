from django.db import models
from django.utils import timezone


class Conversation(models.Model):
    """Representa una conversación del usuario con el chatbot."""
    
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Conversación"
        verbose_name_plural = "Conversaciones"
    
    def __str__(self):
        return f"Conversación {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class Message(models.Model):
    """Representa un mensaje dentro de una conversación."""
    
    ROLE_CHOICES = [
        ('user', 'Usuario'),
        ('assistant', 'Asistente'),
    ]
    
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = "Mensaje"
        verbose_name_plural = "Mensajes"
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_role_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class QueryLog(models.Model):
    """Registra cada consulta realizada al sistema para trazabilidad."""
    
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='query_logs',
        null=True,
        blank=True
    )
    user_query = models.TextField(help_text="Consulta original del usuario")
    assistant_response = models.TextField(help_text="Respuesta generada por el sistema")
    
    # Métricas de rendimiento
    response_time = models.FloatField(
        help_text="Tiempo de respuesta en segundos",
        null=True,
        blank=True
    )
    chunks_retrieved = models.IntegerField(
        default=0,
        help_text="Número de chunks recuperados del índice"
    )
    
    # Contexto utilizado
    context_used = models.TextField(
        blank=True,
        help_text="Contexto recuperado del índice vectorial"
    )
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.CharField(max_length=45, null=True, blank=True, help_text="Dirección IP del cliente")
    user_agent = models.TextField(blank=True)
    
    # Calidad de respuesta (opcional para feedback futuro)
    feedback_score = models.IntegerField(
        null=True,
        blank=True,
        help_text="Puntuación de 1-5 si el usuario proporciona feedback"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Registro de Consulta"
        verbose_name_plural = "Registros de Consultas"
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['conversation']),
        ]
    
    def __str__(self):
        return f"Query {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class AuditLog(models.Model):
    """Registra eventos importantes del sistema para auditoría."""
    
    EVENT_TYPES = [
        ('query', 'Consulta Realizada'),
        ('index_build', 'Construcción de Índice'),
        ('error', 'Error del Sistema'),
        ('config_change', 'Cambio de Configuración'),
        ('startup', 'Inicio del Sistema'),
    ]
    
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    description = models.TextField()
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Datos adicionales en formato JSON"
    )
    
    # Información de contexto
    ip_address = models.CharField(max_length=45, null=True, blank=True, help_text="Dirección IP del cliente")
    user_agent = models.TextField(blank=True)
    
    # Severidad
    SEVERITY_CHOICES = [
        ('info', 'Información'),
        ('warning', 'Advertencia'),
        ('error', 'Error'),
        ('critical', 'Crítico'),
    ]
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
        default='info'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Registro de Auditoría"
        verbose_name_plural = "Registros de Auditoría"
        indexes = [
            models.Index(fields=['event_type', 'created_at']),
            models.Index(fields=['severity', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.get_severity_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
