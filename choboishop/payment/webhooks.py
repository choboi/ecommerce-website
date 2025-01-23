import stripe
import logging
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order
from .tasks import payment_completed

logger = logging.getLogger(__name__)


@csrf_exempt
def stripe_webhook(request):
    """
    Webhook handler for Stripe events.

    This function handles incoming webhook events from Stripe. It verifies the
    signature of the event, retrieves the event data, and then performs actions
    based on the event type.

    For example, if the event is a 'payment_intent.succeeded' event, this function
    marks the corresponding order as paid.
    """

    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        if session['mode'] == 'payment' and session['payment_status'] == 'paid':
            try:
                order = Order.objects.get(id=session['client_reference_id'])
                order.paid = True
                order.stripe_id = session.payment_intent
                order.save()
            except Order.DoesNotExist:
                logger.error(f"Order with id {session['client_reference_id']} does not exist.")
                return HttpResponse(status=404)
            payment_completed.delay(order.id)

    return HttpResponse(status=200)
