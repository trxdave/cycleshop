/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js
*/

// Extract the Stripe public key and client secret from the HTML elements
const stripePublicKey = document.getElementById('id_stripe_public_key').textContent.trim();
const clientSecret = document.getElementById('id_client_secret').textContent.trim();
const stripe = Stripe(stripePublicKey);  // Initialize Stripe with the public key
const elements = stripe.elements();  // Create an instance of Stripe Elements

// Custom styling for the card element
const style = {
    base: {
        color: '#000',
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: 'antialiased',
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

// Create and mount the card element
const card = elements.create('card', { style: style });
card.mount('#card-element');

// Handle real-time validation errors from the card Element
card.on('change', function(event) {
    const displayError = document.getElementById('card-errors');
    displayError.textContent = event.error ? event.error.message : '';
});

// Handle form submission and confirm the payment
document.getElementById('payment-form').addEventListener('submit', function(event) {
    event.preventDefault();

    stripe.confirmCardPayment(clientSecret, {
        payment_method: {
            card: card,
            billing_details: {
                name: document.getElementById('name_on_card').value,  // Ensure this element exists
            }
        }
    }).then(function(result) {
        if (result.error) {
            // Display error message to the customer
            document.getElementById('card-errors').textContent = result.error.message;
        } else if (result.paymentIntent && result.paymentIntent.status === 'succeeded') {
            // Payment succeeded, redirect to confirmation page
            window.location.href = "/checkout/success";
        } else {
            console.log("Unexpected payment result:", result);
        }
    });
});