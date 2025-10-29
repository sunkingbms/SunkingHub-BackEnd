from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
from .mixins import SLAMixin


# Create your models here.

class Request(SLAMixin, models.Model):
    class Status(models.TextChoices):
        SCOPING = "scoping", _("Scoping")
        WIP = "wip", _("Work in Progress")
        COMPLETED = "completed", _("Completed")
        DEFERRED = "deferred", _("Deferred")
        ON_HOLD = "on-hold", _("On-hold")
        CONVERTED = "converted_to_project", _("Converted to Project")

    class Priority(models.TextChoices):
        LOW = "low", _("Low")
        MEDIUM = "medium", _("Medium")
        HIGH = "high", _("High")

    class DurationType(models.TextChoices):
        SHORT = "short_term", _("Short Term")
        LONG = "long_term", _("Long Term")
    
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    request_type = models.CharField(max_length=50)
    system = models.CharField(max_length=100)
    department = models.CharField(max_length=50)
    market = models.CharField(max_length=100)
    priority = models.CharField(max_length=40, choices=Priority.choices, default=Priority.MEDIUM)
    
    # Request time tracking
    # estimated_duration_days = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    duration_type = models.CharField(max_length=10, choices=DurationType.choices, default=DurationType.SHORT)
    
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.SCOPING)
    
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_requests'
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name = 'requests_assigned_by'
    )
    completed_at = models.DateTimeField(blank=True, null=True)
    # handling_time = models.DurationField(null=True, blank=True)
    # sla_status = models.CharField(max_length=100, choices=SLAStatus.choices, default=SLAStatus.ON_TRACK)
    follow_up = models.BooleanField(default=False)
    requestor_email = models.EmailField(blank=True)
    improvement_type = models.CharField(max_length=60)
    
    
    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["priority"]),
            models.Index(fields=["assigned_to"]),
            models.Index(fields=["sla_status"]),
            models.Index(fields=["sla_due"]),
        ]
        
        
    def __str__(self):
        return f"Request #{self.pk} - {self.request_type} ({self.status})"
    
    
    def save(self, *args, **kwargs):
        """
        Override save to automatically set the sla_target based on
        duration_type, and then run the mixin's SLA calculator.
        """
        
        # --- This is our "Bridge Logic" ---
        # It sets the sla_target from the mixin based on the
        # old duration_type field.
        if self.duration_type == self.DurationType.SHORT:
            self.sla_target = timedelta(days=3)
        else: # 'long_term'
            self.sla_target = timedelta(days=10)
        # ------------------------------------

        # --- This is the Mixin Logic (copied from Project) ---
        # First save to get a 'timestamp' (if new)
        # We must avoid an infinite loop, so we only run SLA logic 
        # if we are NOT just updating SLA fields
        update_fields = kwargs.get("update_fields")
        is_sla_update = update_fields and "sla_due" in update_fields

        if not is_sla_update:
            super().save(*args, **kwargs) # Save normally
            
            changed = False
            try:
                changed = self.update_sla_status()
            except TypeError:
                self.update_sla_status()
                changed = True
    
            if changed:
                # Save *only* the SLA fields
                super().save(update_fields=["sla_due", "sla_status", "sla_breached", "sla_breached_at"])
        else:
            # This is already the second save (the SLA update)
            super().save(*args, **kwargs)
    
