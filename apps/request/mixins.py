# in request/mixins.py (NEW FILE)

from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class SLAMixin(models.Model):
    '''
    SLA used to track requests. This provides all the SLA tools.
    '''
    
    class SLAStatus(models.TextChoices):
        ON_TRACK = "on_track", _("On Track")
        DUE_SOON = "due_soon", _("Due Soon")
        OVERDUE = "overdue", _("Overdue")
        
    sla_target = models.DurationField(
        null=True,
        blank=True,
        help_text="Duration a project, task, or request should be completed"
    )
    
    sla_due = models.DateTimeField(
        null=True, blank=True,
        help_text=_("Computed due datetime = created_at + sla_target.")
    )
    
    sla_status = models.CharField(
        max_length=12,
        choices=SLAStatus.choices,
        default=SLAStatus.ON_TRACK,
        db_index=True,
    )
    
    sla_breached = models.BooleanField(default=False)
    
    sla_breached_at = models.DateTimeField(
        null=True, blank=True,
        help_text=_("When the SLA was first breached.")
    )

    class Meta:
        abstract = True

    def compute_sla_due(self):
        """Compute the due date/time if sla_target exists."""
        if self.sla_target:
            start = getattr(self, "timestamp", None) or getattr(self, "created_at", None) or timezone.now()
            return start + self.sla_target
        return None

    def update_sla_status(self, due_soon_threshold=timedelta(hours=24)):
        """
        Evaluate SLA state (on_track / due_soon / overdue).
        Returns True if fields were changed, False otherwise.
        """
        now = timezone.now()
        
        # Store old values to check for changes
        old_status = self.sla_status
        old_due = self.sla_due
        old_breached = self.sla_breached
        old_breached_at = self.sla_breached_at
        
        # 1. Compute Due Date if it's missing
        if self.sla_target and not self.sla_due:
            self.sla_due = self.compute_sla_due()

        # 2. If no due date, it's always On Track
        if not self.sla_due:
            self.sla_status = self.SLAStatus.ON_TRACK
            self.sla_breached = False
            self.sla_breached_at = None
        
        # 3. If due date exists, evaluate status
        else:
            time_left = self.sla_due - now
            if time_left.total_seconds() < 0:
                self.sla_status = self.SLAStatus.OVERDUE
                if not self.sla_breached: # Only set breach time once
                    self.sla_breached = True
                    self.sla_breached_at = now
            elif time_left <= due_soon_threshold:
                self.sla_status = self.SLAStatus.DUE_SOON
                self.sla_breached = False 
            else:
                self.sla_status = self.SLAStatus.ON_TRACK
                self.sla_breached = False
        
        # 4. Return True if any of the SLA fields were modified
        return (
            self.sla_status != old_status or
            self.sla_due != old_due or
            self.sla_breached != old_breached or
            self.sla_breached_at != old_breached_at
        )