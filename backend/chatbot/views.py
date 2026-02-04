from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['GET'])
def health_check(request):
    """Endpoint de health check para verificar que el servicio está activo."""
    return Response({
        'status': 'ok',
        'message': 'Backend GAPID Chatbot está operacional'
    }, status=status.HTTP_200_OK)
