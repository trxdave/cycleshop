/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js
*/

document.addEventListener('DOMContentLoaded', function () {
    const stripePublicKeyElement = document.getElementById('id_stripe_public_key');
    const clientSecretElement = document.getElementById('id_client_secret');

    if (!stripePublicKeyElement || !clientSecretElement) {
        document.getElementById('card-errors').textContent = "Error: Missing Stripe keys in the DOM.";
        return;
    }

    const stripePublicKey = stripePublicKeyElement.textContent.trim();
    const clientSecret = clientSecretElement.textContent.trim();

    if (!clientSecret) {
        document.getElementById('card-errors').textContent = "Error: Client secret is empty.";
        return;
    }

    const stripe = Stripe(stripePublicKey);
    const elements = stripe.elements();

    const style = {
        base: {
            color: '#000000',
            fontSize: '16px',
            '::placeholder': {
                color: '#cccccc',
            },
        },
        invalid: {
            color: '#dc3545',
            iconColor: '#dc3545',
        },
    };

    const card = elements.create('card', { style: style });
    card.mount('#card-number-element');

    card.on('change', function (event) {
        const displayError = document.getElementById('card-errors');
        displayError.textContent = event.error ? event.error.message : '';
    });

    const form = document.getElementById('payment-form');
    const loadingOverlay = document.getElementById('loading-overlay');

    if (!form || !loadingOverlay) {
        document.getElementById('card-errors').textContent = "Error: Required form elements are missing.";
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
            full_name: document.getElementById('full_name').value.trim(),
            email: document.getElementById('email').value.trim(),
            phone_number: document.getElementById('phone_number').value.trim(),
            address: document.getElementById('address').value.trim(),
            city: document.getElementById('city').value.trim(),
            postal_code: document.getElementById('postal_code').value.trim(),
            country: document.getElementById('country').value.trim(),
        };

        const url = '/checkout/cache_checkout_data/';

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify(postData),
        })
            .then(response => {
                if (!response.ok) throw new Error(`Network response was not ok: ${response.statusText}`);
                return response.json();
            })
            .then(data => {
                const orderId = data.order_id;

                if (!orderId) {
                    throw new Error('Order ID is not defined.');
                }

                return stripe.confirmCardPayment(clientSecret, {
                    payment_method: {
                        card: card,
                        billing_details: {
                            name: postData.full_name,
                            email: postData.email,
                            phone: postData.phone_number,
                            address: {
                                line1: postData.address,
                                city: postData.city,
                                country: postData.country,
                            },
                        },
                    },
                });
            })
            .then(function (result) {
                loadingOverlay.classList.remove('show');

                if (result.error) {
                    document.getElementById('card-errors').textContent = result.error.message;
                } else if (result.paymentIntent && result.paymentIntent.status === 'succeeded') {
                    const orderId = result.paymentIntent.metadata.order_id;
                    window.location.href = `/checkout/checkout_success/${orderId}/`;
                }
            })
            .catch(error => {
                loadingOverlay.classList.remove('show');
                document.getElementById('card-errors').textContent = "Error: " + error.message;
            });
    });
});