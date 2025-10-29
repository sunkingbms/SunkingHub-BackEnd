from django.db import models
from django.conf import settings

# Create your models here.

class Payment(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed")
    ]
    
    INITIATOR_CHOICES = [
        ("SYSTEM", "System"),
        ("USER", "User"),
        ("SCHEDULE", "Scheduled job"),
    ]
    # User related data (optional)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name="payments",
        blank=True,
        null=True
    )
    # Core fields
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    account_number = models.CharField(max_length=20)
    currency = models.CharField(max_length=5, default="NGN")
    bank_code = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=150)
    
    # Tracking identifiers
    paga_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    reference_number = models.CharField(max_length=50, blank=True, null=True)
    
    # Automation / Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    is_automated = models.BooleanField(default=True, db_index=True)
    initiator = models.CharField(max_length=28, choices=INITIATOR_CHOICES, default="SYSTEM", db_index=True)
    idempotency_key = models.CharField(max_length=128, blank=True, null=True, unique=True, db_index=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    
    # JSON for tracability
    raw_request = models.JSONField(blank=True, null=True)
    raw_response = models.JSONField(blank=True, null=True)
    
    # Audit logs tracability
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["initiator", "status"]),
        ]
    
    def __str__(self):
        user_ident = getattr(self.user, "email", "system")
        ref = self.reference_number or "-"
        return f"{self.reference_number} | {self.user.email} | {self.amount} {self.currency} | {self.status}"
    
    
