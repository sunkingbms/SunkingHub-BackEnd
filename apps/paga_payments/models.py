from django.db import models
from django.conf import settings

# Create your models here.

class Payments(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed")
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    account_number = models.CharField(max_length=20)
    currency = models.CharField(max_length=5, default="NGN")
    bank_code = models.CharField(max_length=20)
    reference_number = models.CharField(max_length=50, blank=True, null=True)
    paga_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    bank_name = models.CharField(max_length=150)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    
    raw_request = models.JSONField(blank=True, null=True)
    raw_response = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add = True)
    
    def __str__(self):
        return f"{self.reference_number} | {self.user.email} | {self.amount} {self.currency} | {self.status}"
    
    
