from django.http import HttpResponse

class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        """Handle generic/unknown/unexpected webhook events"""
        return HttpResponse(
            content=f"Unhandled event received: {event['type']}",
            status=200
        )

    def handle_payment_intent_succeeded(self, event):
        """Handle the payment_intent.succeeded webhook event"""
        intent = event.data.object  # Stripe PaymentIntent object
        # Add any custom logic here, e.g., updating order status in your database
        return HttpResponse(
            content="Payment succeeded webhook received",
            status=200
        )

    def handle_payment_intent_failed(self, event):
        """Handle the payment_intent.failed webhook event"""
        intent = event.data.object  # Stripe PaymentIntent object
        # Add any custom logic here, e.g., notifying the user of failed payment
        return HttpResponse(
            content="Payment failed webhook received",
            status=200
        )