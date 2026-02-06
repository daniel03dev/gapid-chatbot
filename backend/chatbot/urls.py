from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    # Health check
    path('status/', views.health_check, name='health-check'),
    
    # Conversaciones
    path('conversations/', views.ConversationListCreateView.as_view(), name='conversation-list-create'),
    path('conversations/<int:pk>/', views.ConversationDetailView.as_view(), name='conversation-detail'),
    
    # Mensajes dentro de una conversación
    path('conversations/<int:conversation_id>/messages/', views.MessageListCreateView.as_view(), name='message-list-create'),
]
