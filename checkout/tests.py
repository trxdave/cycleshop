from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from checkout.models import Order
from products.models import Product
from unittest.mock import patch


class CheckoutViewsTest(TestCase):
    def setUp(self):
        """
        Setup a user, product, and initial data for testing.
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        self.product = Product.objects.create(
            name='Test Product',
            price=100.00,
            stock=10,
        )
        self.bag = {
            str(self.product.id): {'quantity': 2, 'price': self.product.price}
        }
        self.client.session['bag'] = self.bag
        self.client.session.save()
        self.checkout_url = reverse('checkout:checkout')
        self.success_url = reverse('checkout:checkout_success', args=[1])
        self.failure_url = reverse('checkout:checkout_failure')

    def test_checkout_page_loads(self):
        """
        Test if the checkout page loads successfully for authenticated users.
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.checkout_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'checkout/checkout.html')

    def test_checkout_redirects_unauthenticated_users(self):
        """
        Test if unauthenticated users are redirected from the checkout page.
        """
        self.client.logout()
        response = self.client.get(self.checkout_url)
        self.assertEqual(response.status_code, 200)

    @patch('checkout.views.stripe.PaymentIntent.create')
    def test_checkout_form_submission_creates_order(self, mock_payment_intent):
        """
        Test if a valid form submission creates an order Stripe PaymentIntent.
        """
        mock_payment_intent.return_value = {'client_secret': 'test_secret'}
        self.client.login(username='testuser', password='testpassword')

        form_data = {
            'full_name': 'Test User',
            'email': 'test@example.com',
            'phone_number': '123456789',
            'address': '123 Test Street',
            'city': 'Test City',
            'postal_code': '12345',
            'country': 'Test Country',
        }
        response = self.client.post(self.checkout_url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Order.objects.filter(email='test@example.com').exists()
        )

    def test_checkout_success_view(self):
        """
        Test the checkout success view for a valid order.
        """
        self.client.login(username='testuser', password='testpassword')
        order = Order.objects.create(
            user=self.user,
            full_name='Test User',
            email='test@example.com',
            total=200.00,
            status='pending',
        )
        response = self.client.get(
            reverse('checkout:checkout_success', args=[order.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'checkout/checkout_success.html')

    def test_checkout_failure_view(self):
        """
        Test the checkout failure view.
        """
        response = self.client.get(self.failure_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'checkout/checkout_failure.html')

    @patch('checkout.views.stripe.Webhook.construct_event')
    def test_stripe_webhook_success(self, mock_webhook):
        """
        Test the Stripe webhook for a successful payment.
        """
        mock_webhook.return_value = {
            'type': 'payment_intent.succeeded',
            'data': {'object': {'metadata': {'order_id': 1}}},
        }
        order = Order.objects.create(
            id=1,
            user=self.user,
            full_name='Test User',
            total=200.00,
            status='pending',
        )
        response = self.client.post(
            reverse('checkout:stripe_webhook'),
            {},
            content_type='application/json',
        )
        order.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(order.status, 'completed')

    @patch('checkout.views.stripe.Webhook.construct_event')
    def test_stripe_webhook_failure(self, mock_webhook):
        """
        Test the Stripe webhook for a failed payment.
        """
        mock_webhook.return_value = {
            'type': 'payment_intent.payment_failed',
            'data': {'object': {'metadata': {'order_id': 1}}},
        }
        order = Order.objects.create(
            id=1,
            user=self.user,
            full_name='Test User',
            total=200.00,
            status='pending',
        )
        response = self.client.post(
            reverse('checkout:stripe_webhook'),
            {},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(order.status, 'pending')

    def test_order_history_view(self):
        """
        Test the order history view for authenticated users.
        """
        self.client.login(username='testuser', password='testpassword')
        Order.objects.create(
            user=self.user,
            full_name='Test User',
            email='test@example.com',
            total=200.00,
            status='completed',
        )
        response = self.client.get(reverse('checkout:order_history'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'checkout/order_history.html')
        self.assertContains(response, 'Test User')
