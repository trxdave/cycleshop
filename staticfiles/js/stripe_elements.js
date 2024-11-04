/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js
*/

var stripe_public_key = $('#id_stripe_public_key').text().slice(1, -1);
var client_secret = $('#id_client_secret').text().slice(1, -1);
var stripe = Stripe(stripe_public_key);
var elements = stripe.elements();
var card = elements.create('card');
card.mount('#card-element');

// Handle real-time validation errors on the card element
card.addEventListener('change', function(event) {
  var errorDiv = document.getElementById('card-errors');

  if (event.error) {
    var html = `
      <span class="icon" role="alert">
          <i class="fas fa-times"></i>
      </span>
      <span>${event.error.message}</span>
    `;

    // Use innerHTML to set the HTML content
    errorDiv.innerHTML = html;
  } else {
    errorDiv.textContent = '';
  }
});

// Handle form submit
var form = document.getElementById('payment-form');

form.addEventListener('submit', function(ev) {
  ev.preventDefault();
  card.update({ 'disabled': true }); // Corrected syntax
  $('#submit-button').attr('disabled', true);

  stripe.confirmCardPayment(client_secret, {
    payment_method: {
      card: card,
    }
  }).then(function(result) {
    if (result.error) {
      var errorDiv = document.getElementById('card-errors');
      var html = `
        <span class="icon" role="alert">
            <i class="fas fa-times"></i>
        </span>
        <span>${result.error.message}</span>
      `;

      // Use innerHTML to set the error message
      errorDiv.innerHTML = html;
      card.update({ 'disabled': false });
      $('#submit-button').attr('disabled', false);
    } else {
      if (result.paymentIntent && result.paymentIntent.status === 'succeeded') {
        form.submit();
      }
    }
  });
});