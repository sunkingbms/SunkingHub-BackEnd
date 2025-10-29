from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from .models import Project, Task
from .serializers import ProjectSerializer, TaskSerializer


class StandardResultsSetPagination(PageNumberPagination):
    """
    Custom pagination class for consistent results across the API.
    """
    page_size = 20  # Number of items per page
    page_size_query_param = 'page_size'  # Allow clients to override page size via query param
    max_page_size = 100  # Maximum page size clients can request
    page_query_param = 'page'  # Query parameter name for page number

class ProjectViewSet(viewsets.ModelViewSet):
    """
        API endpoints for the Project model. This viewset give us /api/projects/ and /api/projects/<id>/
    """ 
    queryset = Project.objects.all().select_related('project_manager', 'request').prefetch_related('tasks')
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
     
    def perform_create(self, serializer):
        # You could, for example, set the project_manager to the current user
        # serializer.save(project_manager=self.request.user)
        serializer.save()
         
class TaskViewSet(viewsets.ModelViewSet):
    """
        API endpoints for Tasks.
        This ViewSet is nested under projects.
        Gives us /api/projects/<project_id>/tasks/
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """
            Filters tasks based on the project_id in the URL.
            Uses select_related and prefetch_related to avoid N+1 queries.
        """
        # Get the project_pk from the URL
        project_pk = self.kwargs.get('project_pk')
        if project_pk:
            # Return only tasks for that specific project with optimized queries
            return Task.objects.filter(project_id=project_pk).select_related('assigned_to', 'project')
        # if no project_pk is provided.
        return Task.objects.none()
    
    def perform_create(self, serializer):
        """
        This automatically sets the project on the task when we create it.
        """
        project_pk = self.kwargs.get('project_pk')
        try:
            project = Project.objects.get(pk=project_pk)
        except Project.DoesNotExist:
            raise PermissionDenied('Project not found')
        
        # Save the task with the project automatically linked
        serializer.save(project=project)
        
    def get_serializer_context(self):
        """Passes the 'project_pk' from the URL to the serializer."""
        context = super().get_serializer_context()
        context['project_pk'] = self.kwargs.get('project_pk')
        return context