/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js
*/

var stripe = Stripe('{{ stripe_public_key }}');

// Create an instance of Elements
var elements = stripe.elements();

// Custom styling for the card Element
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

// Create separate instances for card number, expiry, and CVV
var cardNumber = elements.create('cardNumber', { style: style });
var cardExpiry = elements.create('cardExpiry', { style: style });
var cardCvc = elements.create('cardCvc', { style: style });

// Mount the elements to their respective divs
cardNumber.mount('#card-number-element');
cardExpiry.mount('#card-expiry-element');
cardCvc.mount('#card-cvc-element');

// Handle real-time validation errors from the card elements
cardNumber.addEventListener('change', function(event) {
  var displayError = document.getElementById('card-errors');
  if (event.error) {
    displayError.textContent = event.error.message;
  } else {
    displayError.textContent = '';
  }
});

// Handle form submission
var form = document.getElementById('payment-form');
form.addEventListener('submit', function(event) {
  event.preventDefault();

  stripe.confirmCardPayment('{{ client_secret }}', {
    payment_method: {
      card: cardNumber, // Note: We use cardNumber for the payment method
      billing_details: {
        name: document.getElementById('name-on-card').value
      }
    }
  }).then(function(result) {
    if (result.error) {
      // Show error to your customer
      var errorElement = document.getElementById('card-errors');
      errorElement.textContent = result.error.message;
    } else {
      // Payment succeeded, submit the form
      if (result.paymentIntent.status === 'succeeded') {
        form.submit();
      }
    }
  });
});