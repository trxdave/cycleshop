/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js
*/

document.addEventListener('DOMContentLoaded', function() {
    var stripePublicKeyElement = document.getElementById('id_stripe_public_key');
    var clientSecretElement = document.getElementById('id_client_secret');

    var stripePublicKey = stripePublicKeyElement ? stripePublicKeyElement.textContent.trim() : null;
    var clientSecret = clientSecretElement ? clientSecretElement.textContent.trim() : null;

    if (!stripePublicKey || !clientSecret) {
        console.error("Stripe public key or client secret is missing!");
        return;
    }

    var stripe = Stripe(stripePublicKey);
    var elements = stripe.elements();

    var style = {
        base: {
            color: '#000000',
            fontFamily: '"Arial", sans-serif',
            fontSize: '16px',
            '::placeholder': {
                color: '#aab7c4'
            }
        },
        invalid: {
            color: '#dc3545',
            iconColor: '#dc3545'
        }
    };

    var card = elements.create('card', { style: style });
    card.mount('#card-number-element');

    card.addEventListener('change', function(event) {
        var errorDiv = document.getElementById('card-errors');
        if (event.error) {
            errorDiv.textContent = event.error.message;
        } else {
            errorDiv.textContent = '';
        }
    });

    var form = document.getElementById('payment-form');
    var loadingOverlay = document.getElementById('loading-overlay');

    form.addEventListener('submit', function(ev) {
        ev.preventDefault();

        // Show the loading overlay with fade-in effect
        loadingOverlay.classList.add('show');

        stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: card,
                billing_details: {
                    name: document.getElementById('name-on-card').value,
                    email: document.getElementById('email').value,
                    phone: document.getElementById('phone').value,
                    address: {
                        line1: document.getElementById('address').value,
                        city: document.getElementById('city').value,
                        country: document.getElementById('location').value
                    }
                }
            }
        }).then(function(result) {
            if (result.error) {
                // Hide the loading overlay if there's an error
                loadingOverlay.classList.remove('show');

                // Redirect to failure page after short delay
                setTimeout(function() {
                    window.location.href = "/checkout/checkout_failure/";
                }, 2000);
            } else {
                if (result.paymentIntent.status === 'succeeded') {
                    // Payment succeeded - hide overlay and redirect to success page
                    setTimeout(function() {
                        window.location.href = "/checkout/checkout_success/";
                    }, 2000);
                }
            }
        });
    });
});