from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Full serializer for viewing payment records."""

    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "user",
            "user_email",
            "amount",
            "account_number",
            "currency",
            "bank_code",
            "bank_name",
            "reference_number",
            "paga_transaction_id",
            "status",
            "is_automated",
            "initiator",
            "idempotency_key",
            "raw_request",
            "raw_response",
            "created_at",
        ]
        read_only_fields = (
            "user",
            "reference_number",
            "paga_transaction_id",
            "status",
            "created_at",
        )


class InitiatePaymentSerializer(serializers.Serializer):
    """
    Used when creating a payment (manual, Zapier, or system job).
    """

    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    account_number = serializers.CharField(max_length=20)
    bank_code = serializers.CharField(max_length=20)
    bank_name = serializers.CharField(max_length=150, required=False)
    currency = serializers.CharField(max_length=5, required=False, default="NGN")
    idempotency_key = serializers.CharField(max_length=128, required=False, allow_blank=True)
    initiator = serializers.ChoiceField(
        choices=Payment.INITIATOR_CHOICES, default="USER", required=False
    )
    description = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        """
            Prevent double submission by verifying the idempotency key, bank_code, and account number.
        """
        idempotency_key = data.get("idempotency_key")
        amount = data.get("amount")
        account_number = data.get("account_number")
        bank_name = data.get("bank_name")
        bank_code = data.get("bank_code")
        
        # double payment protection
        fifteen_min_ago = timezone.now() - timedelta(min=15)
        recent_payment = Payment.objects.filter(
            account_number = account_number,
            amount = amount,
            bank_name = bank_name,
            bank_code = bank_code,
            created_at = fifteen_min_ago,
            status_in = ["PENDING", "SUCCESS"]
        ).order_by("-created_at").first()
        
        if recent_duplicate:
            raise serializers.ValidationError({
                "duplicate": f"A similar payment ({ref: {recent_payment.reference_number}}, already exist!)"
            })
            
        # Sanity on payment amount
        if amount <= 0:
            raise serializers.ValidationError({
                "amount": "Payment amount must be greater than zero"
            })
        
        # idempotency protection
        if idempotency_key and Payment.objects.filter(idempotency_key=idempotency_key).exists():
            raise serializers.ValidationError(
                {"idempotency_key": "This payment request has already been processed."}
            )
            
        return data
