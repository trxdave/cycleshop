/*
    Core logic/payment flow for this comes from:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from:
    https://stripe.com/docs/stripe-js
*/

document.addEventListener('DOMContentLoaded', function () {
    const stripePublicKeyElement = document.getElementById('id_stripe_public_key');
    const clientSecretElement = document.getElementById('id_client_secret');
    const cardErrorsElement = document.getElementById('card-errors');
    const form = document.getElementById('payment-form');
    const loadingOverlay = document.getElementById('loading-overlay');

    if (!stripePublicKeyElement || !clientSecretElement || !form || !cardErrorsElement) {
        if (cardErrorsElement) {
            cardErrorsElement.textContent = "Payment system unavailable. Please try again later.";
        }
        return;
    }

    const stripePublicKey = stripePublicKeyElement.textContent.trim();
    const clientSecret = clientSecretElement.textContent.trim();

    if (!stripePublicKey || !clientSecret) {
        cardErrorsElement.textContent = "Payment system unavailable. Please try again later.";
        return;
    }

    const stripe = Stripe(stripePublicKey);
    const elements = stripe.elements();

    const card = elements.create('card', {
        style: {
            base: {
                color: '#000',
                fontSize: '16px',
                '::placeholder': { color: '#888' },
            },
            invalid: { color: '#dc3545', iconColor: '#dc3545' },
        },
    });

    card.mount('#card-number-element');

    card.on('change', function (event) {
        cardErrorsElement.textContent = event.error ? event.error.message : '';
    });

    form.addEventListener('submit', function (ev) {
        ev.preventDefault();
        loadingOverlay.style.display = 'block';

        const postData = {
            full_name: document.getElementById('full_name').value.trim(),
            email: document.getElementById('email').value.trim(),
            phone_number: document.getElementById('phone_number').value.trim(),
            address: document.getElementById('address').value.trim(),
            city: document.getElementById('city').value.trim(),
            postal_code: document.getElementById('postal_code').value.trim(),
            country: document.getElementById('country').value.trim(),
        };

        fetch('/checkout/cache_checkout_data/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(postData),
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    stripe.confirmCardPayment(clientSecret, {
                        payment_method: {
                            card: card,
                            billing_details: {
                                name: postData.full_name,
                                email: postData.email,
                            },
                        },
                    }).then(function (result) {
                        loadingOverlay.style.display = 'none';

                        if (result.error) {
                            cardErrorsElement.textContent = result.error.message;
                        } else if (result.paymentIntent && result.paymentIntent.status === 'succeeded') {
                            window.location.href = `/checkout/checkout_success/${data.order_id}/`;
                        }
                    }).catch(function (error) {
                        loadingOverlay.style.display = 'none';
                        cardErrorsElement.textContent = `Error: ${error.message}`;
                    });
                } else {
                    loadingOverlay.style.display = 'none';
                    cardErrorsElement.textContent = `Error: ${data.message}`;
                }
            })
            .catch(error => {
                loadingOverlay.style.display = 'none';
                cardErrorsElement.textContent = "An error occurred. Please try again.";
            });
    });
});