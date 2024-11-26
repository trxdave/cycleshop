from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
import logging

# Set up logger
logger = logging.getLogger(__name__)

class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        """Handle generic/unknown/unexpected webhook events"""
        logger.info(f"Unhandled event received: {event['type']}")
        return HttpResponse(
            content=f"Unhandled event received: {event['type']}",
            status=200,
        )

    def handle_payment_intent_succeeded(self, event):
        """Handle the payment_intent.succeeded webhook event"""
        intent = event['data']['object']  # Stripe PaymentIntent object
        metadata = intent.get('metadata', {})
        order_id = metadata.get('order_id')
        email = metadata.get('email')

        logger.info(f"PaymentIntent succeeded: {intent['id']}")

        # Update order status in the database
        if order_id:
            try:
                from checkout.models import Order
                order = Order.objects.get(id=order_id)
                order.status = "Completed"
                order.save()
                logger.info(f"Order {order_id} updated to Completed")
            except Order.DoesNotExist:
                logger.error(f"Order with ID {order_id} not found")

        # Send confirmation email
        if email:
            try:
                send_mail(
                    subject="Order Confirmation",
                    message=f"Thank you for your order! Your order ID is {order_id}.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                )
                logger.info(f"Confirmation email sent to {email}")
            except Exception as e:
                logger.error(f"Error sending email: {e}")

        return HttpResponse(
            content="Payment succeeded webhook received",
            status=200,
        )

    def handle_payment_intent_failed(self, event):
        """Handle the payment_intent.failed webhook event"""
        intent = event['data']['object']
        metadata = intent.get('metadata', {})
        order_id = metadata.get('order_id')

        logger.warning(f"PaymentIntent failed: {intent['id']}")

        # Update order status in the database
        if order_id:
            try:
                from checkout.models import Order
                order = Order.objects.get(id=order_id)
                order.status = "Failed"
                order.save()
                logger.info(f"Order {order_id} updated to Failed")
            except Order.DoesNotExist:
                logger.error(f"Order with ID {order_id} not found")

        return HttpResponse(
            content="Payment failed webhook received",
            status=200,
        )
