from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    # Health check
    path('status/', views.health_check, name='health-check'),
    
    # Chat endpoint
    path('chat/', views.chat_view, name='chat'),
    
    # Conversaciones
    path('conversations/', views.ConversationListCreateView.as_view(), name='conversation-list-create'),
    path('conversations/<int:pk>/', views.ConversationDetailView.as_view(), name='conversation-detail'),
    
    # Mensajes dentro de una conversación
    path('conversations/<int:conversation_id>/messages/', views.MessageListCreateView.as_view(), name='message-list-create'),
    
    # Logs y trazabilidad
    path('logs/queries/', views.query_logs_view, name='query-logs'),
    path('logs/queries/<int:log_id>/', views.query_log_detail_view, name='query-log-detail'),
    path('logs/audit/', views.audit_logs_view, name='audit-logs'),
    
    # Métricas y estadísticas
    path('metrics/', views.metrics_view, name='metrics'),
]
