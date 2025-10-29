# in request/serializers.py (NEW FILE)

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Request

User = get_user_model()

class RequestSerializer(serializers.ModelSerializer):
    """
    Serializer for the Request model.
    Handles all read-only display names and writeable ID/choice fields.
    """
    
    # --- Read-Only Fields (for easy display) ---
    
    # Display human-readable names for choice fields
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    duration_type_display = serializers.CharField(source='get_duration_type_display', read_only=True)
    sla_status_display = serializers.CharField(source='get_sla_status_display', read_only=True)

    # Display the string name (e.g., email or full name) for related users
    assigned_to_name = serializers.StringRelatedField(source='assigned_to', read_only=True)
    assigned_by_name = serializers.StringRelatedField(source='assigned_by', read_only=True)
    
    
    # --- Write-Only Fields (for create/update) ---
    
    # These fields are used when you POST/PUT data
    # They are 'write_only=True' because we already have the read-only display fields above
    status = serializers.ChoiceField(choices=Request.Status.choices, write_only=True)
    priority = serializers.ChoiceField(choices=Request.Priority.choices, write_only=True)
    duration_type = serializers.ChoiceField(choices=Request.DurationType.choices, write_only=True)

    class Meta:
        model = Request
        fields = [
            'id', 'description', 'request_type', 'system', 'department', 
            'market', 'timestamp', 'completed_at', 'follow_up', 
            'requestor_email', 'improvement_type',
            
            # --- Choice Fields (Read) ---
            'status_display', 'priority_display', 'duration_type_display', 'sla_status_display',
            
            # --- Choice Fields (Write) ---
            'status', 'priority', 'duration_type',
            
            # --- Related User Fields (Read) ---
            'assigned_to_name', 'assigned_by_name',
            
            # --- Related User Fields (Write/Read-ID) ---
            'assigned_to', 'assigned_by',
            
            # --- SLA Fields (from Mixin) ---
            'sla_target', 'sla_due', 'sla_breached', 'sla_breached_at'
        ]
        
        # We make the related user fields accept a simple ID,
        # but they will still return the ID in responses.
        extra_kwargs = {
            'assigned_to': {'allow_null': True, 'required': False},
            'assigned_by': {'allow_null': True, 'required': False},
        }
        
        read_only_fields = [
            'sla_due',
            'sla_breached',
            'sla_breached_at',
            'sla_target'
        ]