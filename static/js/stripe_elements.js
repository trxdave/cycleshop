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
  form.addEventListener('submit', function(ev) {
      ev.preventDefault();

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
        var alertBox = document.createElement('div');
        alertBox.className = 'alert';

        if (result.error) {
            // Payment failed
            alertBox.classList.add('alert-danger');
            alertBox.textContent = "Payment failed: " + result.error.message;
        } else {
            // Payment succeeded
            if (result.paymentIntent.status === 'succeeded') {
                alertBox.classList.add('alert-success');
                alertBox.textContent = "Payment successful! Thank you for your order.";
                form.reset();
            }
        }

        // Insert the alert box at the top of the form
        form.parentNode.insertBefore(alertBox, form);
      });
  });
});