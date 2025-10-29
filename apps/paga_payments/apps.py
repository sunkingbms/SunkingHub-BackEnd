from django.apps import AppConfig


class PagaPaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.paga_payments'
    
    def ready(self):
        from . import signals
