from django.urls import path
from .views import GetBanksView, InitiatePaymentView, PaymentHistoryView


urlpatterns = [
    path("get-banks/", GetBanksView.as_view(), name="get-banks"),
    path("initiate-payment/", InitiatePaymentView.as_view(), name="initiate-payment"),
    path("transactions/", PaymentHistoryView.as_view(), name="transactions"),
]