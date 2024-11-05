/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js
*/

// Initialize Stripe
var stripe = Stripe('{{ stripe_public_key }}');
var elements = stripe.elements();

// Custom styling for the card element
var style = {
  base: {
    color: '#32325d',
    fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
    fontSmoothing: 'antialiased',
    fontSize: '16px',
    '::placeholder': { color: '#aab7c4' }
  },
  invalid: { color: '#fa755a', iconColor: '#fa755a' }
};

// Create card elements
var card = elements.create('card', { style: style });
card.mount('#card-number-element');

// Handle real-time validation errors
card.on('change', function(event) {
  var errorDiv = document.getElementById('card-errors');
  if (event.error) {
    errorDiv.textContent = event.error.message;
  } else {
    errorDiv.textContent = '';
  }
});

// Handle form submission
var form = document.getElementById('payment-form');
form.addEventListener('submit', function(event) {
  event.preventDefault();

  stripe.confirmCardPayment('{{ client_secret }}', {
    payment_method: {
      card: card,
      billing_details: {
        name: document.getElementById('name-on-card').value
      }
    }
  }).then(function(result) {
    if (result.error) {
      // Display error message
      var errorDiv = document.getElementById('card-errors');
      errorDiv.textContent = result.error.message;
    } else {
      if (result.paymentIntent.status === 'succeeded') {
        // Redirect to the success page
        window.location.href = "{% url 'checkout_success %}";
      }
    }
  });
});