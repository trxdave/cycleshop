from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from django.core.mail import send_mail
from django.conf import settings

@receiver(post_save, sender=Order)
def order_created(sender, instance, created, **kwargs):
    if created:
        print(f"New order created with ID: {instance.id} and status: {instance.status}")


@receiver(post_save, sender=Order)
def send_order_confirmation_email(sender, instance, created, **kwargs):
    """
    Send an email when an order is marked as completed.
    """
    if created and instance.status == 'completed':
        subject = f"Order Confirmation - {instance.id}"
        message = f"Thank you for your order, {instance.full_name}!\n\nYour order ID is {instance.id}."
        recipient_list = [instance.email]
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=False,
        )