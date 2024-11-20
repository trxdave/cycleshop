/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js
*/

document.addEventListener('DOMContentLoaded', function () {
    const stripePublicKeyElement = document.getElementById('id_stripe_public_key');
    const clientSecretElement = document.getElementById('id_client_secret');
    const cardErrorsElement = document.getElementById('card-errors');

    if (!stripePublicKeyElement || !clientSecretElement) {
        if (cardErrorsElement) {
            cardErrorsElement.textContent = "Error: Missing Stripe keys in the DOM.";
        } else {
            console.error("Element with ID 'card-errors' is missing in the DOM.");
        }
        return;
    }

    const stripePublicKey = stripePublicKeyElement.textContent.trim();
    const clientSecret = clientSecretElement.textContent.trim();

    const stripe = Stripe(stripePublicKey);
    const elements = stripe.elements();

    const style = {
        base: {
            color: '#000',
            fontSize: '16px',
            '::placeholder': { color: '#888' },
        },
        invalid: { color: '#dc3545', iconColor: '#dc3545' },
    };

    const card = elements.create('card', { style: style });
    card.mount('#card-number-element');

    card.on('change', function (event) {
        if (cardErrorsElement) {
            cardErrorsElement.textContent = event.error ? event.error.message : '';
        }
    });

    const form = document.getElementById('payment-form');
    const loadingOverlay = document.getElementById('loading-overlay');

    if (!form || !loadingOverlay) {
        if (cardErrorsElement) {
            cardErrorsElement.textContent = "Error: Required form elements are missing.";
        } else {
            console.error("Form or loading overlay is missing in the DOM.");
        }
        return;
    }

    form.addEventListener('submit', function (ev) {
        ev.preventDefault();
        loadingOverlay.classList.add('show');

        const saveInfo = document.getElementById('id-save-info') ? document.getElementById('id-save-info').checked : false;
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

        const postData = {
            csrfmiddlewaretoken: csrfToken,
            client_secret: clientSecret,
            save_info: saveInfo,
        };

        fetch('/checkout/cache_checkout_data/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
            body: JSON.stringify(postData),
        })
            .then(response => response.json())
            .then(data => {
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
                loadingOverlay.classList.remove('show');
                if (result.error) {
                    if (cardErrorsElement) {
                        cardErrorsElement.textContent = result.error.message;
                    }
                } else if (result.paymentIntent && result.paymentIntent.status === 'succeeded') {
                    window.location.href = `/checkout/checkout_success/${data.order_id}/`;
                }
            })
            .catch(error => {
                loadingOverlay.classList.remove('show');
                if (cardErrorsElement) {
                    cardErrorsElement.textContent = `Error: ${error.message}`;
                } else {
                    console.error(error);
                }
            });
    });
});