/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js
*/

document.addEventListener('DOMContentLoaded', function () {
    const stripePublicKey = document.getElementById('id_stripe_public_key').textContent.trim();
    const clientSecret = document.getElementById('id_client_secret').textContent.trim();
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

        const url = '/checkout/cache_checkout_data/';

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
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
                throw new Error('Order ID is not defined');
            }

            const nameElement = document.getElementById('full_name');
            const emailElement = document.getElementById('email');
            const phoneElement = document.getElementById('phone_number');
            const addressElement = document.getElementById('address');
            const cityElement = document.getElementById('city');
            const countryElement = document.getElementById('country');

            if (!nameElement || !emailElement || !phoneElement || !addressElement || !cityElement || !countryElement) {
                document.getElementById('card-errors').textContent = "Error: Required form elements are missing.";
                return;
            }

            stripe.confirmCardPayment(clientSecret, {
                payment_method: {
                    card: card,
                    billing_details: {
                        name: nameElement.value.trim(),
                        email: emailElement.value.trim(),
                        phone: phoneElement.value.trim(),
                        address: {
                            line1: addressElement.value.trim(),
                            city: cityElement.value.trim(),
                            country: countryElement.value.trim(),
                        },
                    },
                },
                shipping: {
                    name: nameElement.value.trim(),
                    phone: phoneElement.value.trim(),
                    address: {
                        line1: addressElement.value.trim(),
                        city: cityElement.value.trim(),
                        country: countryElement.value.trim(),
                    },
                },
            }).then(function (result) {
                loadingOverlay.classList.remove('show');

                if (result.error) {
                    document.getElementById('card-errors').textContent = result.error.message;
                } else if (result.paymentIntent && result.paymentIntent.status === 'succeeded') {
                    window.location.href = `/checkout/checkout_success/${orderId}/`;
                }
            });
        })
        .catch(error => {
            loadingOverlay.classList.remove('show');
            document.getElementById('card-errors').textContent = "Error: " + error.message;
        });
    });
});