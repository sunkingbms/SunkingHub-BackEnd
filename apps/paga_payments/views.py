from django.shortcuts import render
from rest_framework import permissions, status, generics
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone

from .models import Payment
from .serializers import PaymentSerializer, InitiatePaymentSerializer
from .utils import generate_reference, paga_post

# Create your views here.

class GetBanksView(APIView):
    "Fetch list of banks from paga"
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        ref = generate_reference()
        payload = {"referenceNumber": ref}
        try:
            res = paga_post("getBanks", payload, ref)
        except Exception as e:
            return Response({"detail": f"Paga request failed {e}"}, status=502)
        
        if res.status_code != 200:
            return Response({ "detail": res.text}, status=res.status_code)
        
        data = res.json()
        banks = data.get("banks")
        
        return Response({"referenceNumber": ref, "banks": banks}, status=200)
    


class InitiatePaymentView(APIView):
    """
        Initiating the payment to Paga
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        ser = InitiatePaymentSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        
        # Check for idempotency duplicates
        idempotency_key = data.get("idempotency_key")
        if idempotency_key and Payment.objects.filter(idempotency_key=idempotency_key).exists():
            existing = Payment.objects.get(idempotency_key=idempotency_key)
            return Response(PaymentSerializer(existing).data, status=status.HTTP_200_OK)

        # generate reference
        ref = generate_reference()

        # build local record
        payment = Payment.objects.create(
            user=request.user if request.user.is_authenticated else None,
            amount=data["amount"],
            account_number=data["account_number"],
            currency=data.get("currency", "NGN"),
            bank_code=data["bank_code"],
            bank_name=data.get("bank_name", ""),
            initiator=data.get("initiator", "USER"),
            idempotency_key=idempotency_key,
            description=data.get("description", ""),
            status="PENDING",
            is_automated=(data.get("initiator") in ["SYSTEM", "API", "SCHEDULE"]),
            raw_request=data,
        )

        # compute hash & send to Paga
        concat = f"{ref}{data['amount']}{data['bank_code']}{data['account_number']}"
        payload = {
            "referenceNumber": ref,
            "amount": str(data["amount"]),
            "destinationBank": data.get("bank_name"),
            "destinationBankCode": data["bank_code"],
            "destinationBankAccountNumber": data["account_number"],
            "currency": data.get("currency", "NGN"),
        }

        try:
            res = paga_post("payment", payload, concat)
        except Exception as e:
            payment.status = "FAILED"
            payment.raw_response = {"error": str(e)}
            payment.save(update_fields=["status", "raw_response"])
            return Response({"detail": f"Paga request failed: {e}"}, status=502)

        # handle Paga response
        body = {}
        try:
            body = res.json()
        except Exception:
            body = {"raw": res.text}

        payment.raw_response = body

        if res.status_code == 200:
            payment.status = "SUCCESS"
            payment.paga_transaction_id = body.get("transactionId") or body.get("transactionReference")
            payment.completed_at = timezone.now()
        else:
            payment.status = "FAILED"

        payment.save(update_fields=["status", "paga_transaction_id", "completed_at", "raw_response"])
        return Response(PaymentSerializer(payment).data, status=res.status_code)
    
    
class PaymentHistoryView(generics.ListAPIView):
    """List all payments for authenticated user or system."""
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Payment.objects.all()
        if self.request.user.is_authenticated:
            qs = qs.filter(user=self.request.user)
        return qs.order_by("-created_at")