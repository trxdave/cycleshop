/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js
*/

document.addEventListener('DOMContentLoaded', function () {
    const stripePublicKeyElement = document.getElementById('id_stripe_public_key');
    const clientSecretElement = document.getElementById('id_client_secret');
    const orderData = document.getElementById('order-data');

    if (!stripePublicKeyElement || !clientSecretElement) {
        document.getElementById('card-errors').textContent = "Error: Missing Stripe keys in the DOM.";
        return;
    }

    const stripePublicKey = stripePublicKeyElement.textContent.trim();
    const clientSecret = clientSecretElement.textContent.trim();
    const stripe = Stripe(stripePublicKey);
    const elements = stripe.elements();
    const card = elements.create('card', { style: { base: { color: '#000', fontSize: '16px' } } });
    card.mount('#card-number-element');

    const form = document.getElementById('payment-form');
    const loadingOverlay = document.getElementById('loading-overlay');

    form.addEventListener('submit', function (ev) {
        ev.preventDefault();
        loadingOverlay.classList.add('show');

        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
        const postData = {
            csrfmiddlewaretoken: csrfToken,
            client_secret: clientSecret,
            save_info: document.getElementById('id-save-info')?.checked || false,
        };

        fetch('/checkout/cache_checkout_data/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
            body: JSON.stringify(postData),
        })
            .then(response => response.json())
            .then(data => {
                console.log('Server Response:', data);  // Debug log
                const orderId = data.order_id;

                if (!orderId) {
                    throw new Error('Order ID is missing in the server response.');
                }

                return stripe.confirmCardPayment(clientSecret, {
                    payment_method: {
                        card: card,
                        billing_details: {
                            name: document.getElementById('full_name').value.trim(),
                            email: document.getElementById('email').value.trim(),
                        },
                    },
                });
            })
            .then(result => {
                console.log('PaymentIntent:', result.paymentIntent);  // Debug log
                loadingOverlay.classList.remove('show');

                if (result.error) {
                    document.getElementById('card-errors').textContent = result.error.message;
                } else if (result.paymentIntent?.status === 'succeeded') {
                    const orderId = result.paymentIntent.metadata?.order_id || orderData?.dataset.orderId;
                    if (!orderId) throw new Error('Order ID is completely missing.');
                    window.location.href = `/checkout/checkout_success/${orderId}/`;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                loadingOverlay.classList.remove('show');
                document.getElementById('card-errors').textContent = `Error: ${error.message}`;
            });
    });
});