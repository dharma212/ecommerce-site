from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from .utils import generate_invoice

@receiver(post_save, sender=Order)
def create_invoice(sender, instance, created, **kwargs):
    if created:
        generate_invoice(instance)