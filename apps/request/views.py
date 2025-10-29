from rest_framework import viewsets, permissions
from .models import Request
from .serializers import RequestSerializer
from .pagination import StandardResultsSetPagination

# Create your views here.

class RequestViewSet(viewsets.ModelViewSet):
    """
    API endpoints for Requests.
    Gives us /api/requests/ and /api/requests/<id>/
    """
    serializer_class = RequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    queryset = Request.objects.select_related(
        'assigned_to', 
        'assigned_by'
    ).all()
