from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    # Próximos endpoints:
    # path('conversations/', views.ConversationListCreateView.as_view(), name='conversation-list-create'),
    # path('conversations/<int:pk>/', views.ConversationDetailView.as_view(), name='conversation-detail'),
    # path('conversations/<int:pk>/messages/', views.MessageListCreateView.as_view(), name='message-list-create'),
]
