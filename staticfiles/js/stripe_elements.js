/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js
*/

var stripe = Stripe('{{ stripe_public_key }}');
var elements = stripe.elements();

// Custom styling for Stripe Elements
var style = {
    base: {
        color: '#32325d',
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
            color: '#aab7c4'
        }
    },
    invalid: {
        color: '#fa755a',
        iconColor: '#fa755a'
    }
};

// Create instances of the card elements
var cardNumber = elements.create('cardNumber', { style: style });
var cardExpiry = elements.create('cardExpiry', { style: style });
var cardCvc = elements.create('cardCvc', { style: style });

// Mount the elements to their respective divs
cardNumber.mount('#card-number-element');
cardExpiry.mount('#card-expiry-element');
cardCvc.mount('#card-cvc-element');

// Handle form submission
var form = document.getElementById('payment-form');
form.addEventListener('submit', function(ev) {
    ev.preventDefault();
    stripe.confirmCardPayment('{{ client_secret }}', {
        payment_method: {
            card: cardNumber,
            billing_details: {
                name: document.getElementById('name-on-card').value
            }
        }
    }).then(function(result) {
        if (result.error) {
            // Display error.message in your UI
            document.getElementById('card-errors').textContent = result.error.message;
        } else {
            // The payment has been processed!
            if (result.paymentIntent.status === 'succeeded') {
                form.submit();
            }
        }
    });
});