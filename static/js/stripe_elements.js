/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js
*/

document.addEventListener('DOMContentLoaded', function() {
    // Get Stripe keys and other necessary elements
    var stripePublicKey = document.getElementById('id_stripe_public_key').textContent.trim();
    var clientSecret = document.getElementById('id_client_secret').textContent.trim();
    var stripe = Stripe(stripePublicKey);
    var elements = stripe.elements();
    var card = elements.create('card');
    card.mount('#card-number-element');

    var form = document.getElementById('payment-form');
    var loadingOverlay = document.getElementById('loading-overlay');

    // Submit event handler
    form.addEventListener('submit', function(ev) {
        ev.preventDefault();
        
        // Show loading overlay
        loadingOverlay.classList.add('show');

        // Cache data before confirming payment
        var saveInfo = Boolean(document.getElementById('id-save-info').checked);
        var csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
        var postData = {
            'csrfmiddlewaretoken': csrfToken,
            'client_secret': clientSecret,
            'save_info': saveInfo,
        };

        // Post data to cache endpoint
        var url = '/checkout/cache_checkout_data/';
        $.post(url, postData).done(function () {
            // Confirm payment with Stripe
            stripe.confirmCardPayment(clientSecret, {
                payment_method: {
                    card: card,
                    billing_details: {
                        name: document.getElementById('full_name').value.trim(),
                        phone: document.getElementById('phone_number').value.trim(),
                        email: document.getElementById('email').value.trim(),
                        address: {
                            line1: document.getElementById('street_address1').value.trim(),
                            line2: document.getElementById('street_address2').value.trim(),
                            city: document.getElementById('town_or_city').value.trim(),
                            country: document.getElementById('country').value.trim(),
                            state: document.getElementById('county').value.trim(),
                        }
                    }
                },
                shipping: {
                    name: document.getElementById('full_name').value.trim(),
                    phone: document.getElementById('phone_number').value.trim(),
                    address: {
                        line1: document.getElementById('street_address1').value.trim(),
                        line2: document.getElementById('street_address2').value.trim(),
                        city: document.getElementById('town_or_city').value.trim(),
                        country: document.getElementById('country').value.trim(),
                        postal_code: document.getElementById('postcode').value.trim(),
                        state: document.getElementById('county').value.trim(),
                    }
                }
            }).then(function(result) {
                loadingOverlay.classList.remove('show');  // Hide loading overlay

                if (result.error) {
                    // Handle error (display message or redirect to failure page)
                    setTimeout(function() {
                        window.location.href = "/checkout/checkout_failure/";
                    }, 2000);
                } else {
                    if (result.paymentIntent.status === 'succeeded') {
                        // Redirect to success page after successful payment
                        setTimeout(function() {
                            window.location.href = "/checkout/checkout_success/";
                        }, 2000);
                    }
                }
            });
        }).fail(function() {
            // Handle failure in caching checkout data
            loadingOverlay.classList.remove('show');
            alert("An error occurred while processing your payment. Please try again.");
        });
    });
});