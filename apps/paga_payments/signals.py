from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Payment
from .utils import generate_reference

@receiver(pre_save, sender=Payment)
def add_reference_if_missing(sender, instance, **kwargs):
    if not instance.reference_number:
        instance.reference_number = generate_reference()