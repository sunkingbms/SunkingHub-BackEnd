from django.db import models
from django.conf import settings
from apps.request.models import Request
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
from .mixins import SLAMixin
from django.core.validators import MinValueValidator, MaxValueValidator


class Project(SLAMixin):
    class Status(models.TextChoices):
        PLANNED = "planned", _("Planned")
        WIP = "wip", _("Work in Progress")
        COMPLETED = "completed", _("Completed")
        DEFERRED = "deferred", _("Deferred")
        ON_HOLD = "on-hold", _("On-hold")

    class Priority(models.TextChoices):
        LOW = "low", _("Low")
        MEDIUM = "medium", _("Medium")
        HIGH = "high", _("High")
        CRITICAL = "critical", _("Critical")

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    request = models.ForeignKey(
        Request, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="converted_project"
    )
    department = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNED)
    project_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="managed_projects"
    )
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["priority"]),
            models.Index(fields=["project_manager"]),
            models.Index(fields=["start_date"]),
            models.Index(fields=["end_date"]),
            # index SLA fields so you can quickly find due/overdue items
            models.Index(fields=["sla_status"]),
            models.Index(fields=["sla_due"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Save once to ensure created_at exists, then evaluate SLA.
        Only persist SLA fields if they actually changed (update_sla_status returns True).
        """
        # First save to get created_at (if new)
        super().save(*args, **kwargs)

        # update_sla_status should return True when it changed fields; if your mixin does not return a boolean,
        # you can remove the condition and always save the SLA fields (less optimal).
        changed = False
        try:
            changed = self.update_sla_status()
        except TypeError:
            # fallback if update_sla_status doesn't accept no args or doesn't return bool
            self.update_sla_status()
            changed = True

        if changed:
            # only update fields that the SLA logic may have changed
            super().save(update_fields=["sla_due", "sla_status", "sla_breached", "sla_breached_at"])


class Task(SLAMixin):
    class Status(models.TextChoices):
        SCOPING = "scoping", _("Scoping")
        WIP = "wip", _("Work in Progress")
        COMPLETED = "completed", _("Completed")
        DEFERRED = "deferred", _("Deferred")
        ON_HOLD = "on-hold", _("On-hold")

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="tasks_assigned"
    )

    start_date = models.DateField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)

    # use positive integers for hours
    estimated_hours = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    actual_hours = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(0)])

    # use decimal for percentage/completion (0.00 - 100.00)
    completion_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Completion percent (0.00 - 100.00)"
    )

    priority = models.CharField(
        max_length=10,
        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
        default="medium"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.WIP)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["project"]),
            models.Index(fields=["status"]),
            models.Index(fields=["assigned_to"]),
            models.Index(fields=["due_date"]),
            models.Index(fields=["sla_status"]),
            models.Index(fields=["sla_due"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.status})"

    def save(self, *args, **kwargs):
        # Persist (to populate created_at if new)
        super().save(*args, **kwargs)

        changed = False
        try:
            changed = self.update_sla_status()
        except TypeError:
            self.update_sla_status()
            changed = True

        if changed:
            super().save(update_fields=["sla_due", "sla_status", "sla_breached", "sla_breached_at"])
