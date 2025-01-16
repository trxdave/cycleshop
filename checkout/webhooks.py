import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .webhook_handler import StripeWH_Handler


@require_POST
@csrf_exempt
def stripe_webhook(request):
    """Listen for webhooks from Stripe"""
    # Stripe requires the payload and signature to verify the event
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    # Verify the event
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return HttpResponse(status=400)

    # Set up a webhook handler
    handler = StripeWH_Handler(request)

    # Map webhook events to relevant handler functions
    event_map = {
        'payment_intent.succeeded': handler.handle_payment_intent_succeeded,
        'payment_intent.payment_failed': (
            handler.handle_payment_intent_failed
        ),
    }

    # Get the event type
    event_type = event['type']

    # If there is a handler for the event
    event_handler = event_map.get(event_type, handler.handle_event)

    # Call the event handler with the event
    response = event_handler(event)
    return response
