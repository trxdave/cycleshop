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
            stripe.confirmCardPayment(clientSecret, {
                payment_method: {
                    card: card,
                    billing_details: {
                        name: document.getElementById('name').value.trim(),
                        email: document.getElementById('email').value.trim(),
                        phone: document.getElementById('phone').value.trim(),
                        address: {
                            line1: document.getElementById('address').value.trim(),
                            city: document.getElementById('city').value.trim(),
                            country: document.getElementById('location').value.trim(),
                        },
                    },
                },
                shipping: {
                    name: document.getElementById('name').value.trim(),
                    phone: document.getElementById('phone').value.trim(),
                    address: {
                        line1: document.getElementById('address').value.trim(),
                        city: document.getElementById('city').value.trim(),
                        country: document.getElementById('location').value.trim(),
                    },
                },
            }).then(function (result) {
                loadingOverlay.classList.remove('show');

                if (result.error) {
                    document.getElementById('card-errors').textContent = result.error.message;
                } else if (result.paymentIntent && result.paymentIntent.status === 'succeeded') {
                    window.location.href = `/checkout/checkout_success/`;
                }
            });
        })
        .catch(error => {
            loadingOverlay.classList.remove('show');
            alert("An error occurred while processing your payment. Please try again.");
            console.error("Error:", error);
        });
    });
});