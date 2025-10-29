from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.request.models import Request
from .models import Task, Project

User = get_user_model()

class TaskSerializer(serializers.ModelSerializer):
    """
    Task Serializer
    """
    
    assigned_to_name = serializers.StringRelatedField(source="assigned_to", read_only=True)
    
    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ["project"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make project field read-only if we're in a nested context
        if self.context.get('view') and 'project_pk' in self.context['view'].kwargs:
            self.fields['project'].read_only = True
            
class ProjectSerializer(serializers.ModelSerializer):
    # --- Read-only fields for related object names ---
    project_manager_name = serializers.StringRelatedField(source='project_manager', read_only=True)
    request_name = serializers.StringRelatedField(source='request', read_only=True)
    
    # --- Nested Serializer for Tasks ---
    # This includes all tasks related to this project in the response.
    # It's 'read_only' because tasks are managed at their own endpoint.
    tasks = TaskSerializer(many=True, read_only=True)
    
    # --- Choice Fields ---
    # Show the "human-readable" version of the choices (e.g., "Work in Progress")
    status = serializers.CharField(source='get_status_display', read_only=True)
    priority = serializers.CharField(source='get_priority_display', read_only=True)
    
    # --- Writeable Foreign Keys ---
    # We must redefine these so they are writeable (since we're also
    # showing the read-only '..._name' versions above)
    project_manager = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, allow_null=True, required=False
    )
    
    request = serializers.PrimaryKeyRelatedField(
        queryset=Request.objects.all(), write_only=True, allow_null=True, required=False
    )
    
    # We must also make the choice fields writeable again
    status_write = serializers.ChoiceField(
        choices=Project.Status.choices, write_only=True, source='status'
    )
    priority_write = serializers.ChoiceField(
        choices=Project.Priority.choices, write_only=True, source='priority'
    )
    
    class Meta:
        model = Project
        # We list all fields, including our custom ones
        fields = [
            'id', 'name', 'description', 'department', 'country', 
            'start_date', 'end_date', 'status', 'priority', 
            'created_at', 'updated_at',
            
            # --- Related Object Fields ---
            'request', 'request_name',
            'project_manager', 'project_manager_name',
            
            # --- Writeable Choice Fields ---
            'status_write', 'priority_write',

            # --- SLA Fields (from mixin) ---
            'sla_due', 'sla_status', 'sla_breached', 'sla_breached_at',
            
            # --- Nested Tasks ---
            'tasks'
        ]
        
        read_only_fields = [
            'sla_due',
            'sla_breached',
            'sla_breached_at'
        ]

    def save(self, **kwargs):
        """
        Handles the custom 'save' logic from your model.
        """
        # We don't need to do anything special!
        # When serializer.save() is called, it will call the
        # Project.save() method, which already contains your
        # double-save logic for the SLA mixin. It just works!
        return super().save(**kwargs)