from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from products.models import Product


class BagViewsTest(TestCase):
    def setUp(self):
        """
        Setup a product and initial client session for testing.
        """
        self.client = Client()
        self.product = Product.objects.create(
            name='Test Product',
            price=100.00,
            stock=10
        )
        self.view_bag_url = reverse('bag:view_bag')
        self.add_to_bag_url = reverse(
            'bag:add_to_bag', args=[self.product.id]
        )
        self.remove_from_bag_url = reverse(
            'bag:remove_from_bag', args=[self.product.id]
        )

    def test_view_bag_page_loads(self):
        """
        Test if the bag page loads successfully.
        """
        response = self.client.get(self.view_bag_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bag/bag.html')

    def test_add_to_bag(self):
        """
        Test adding a product to the shopping bag.
        """
        response = self.client.post(self.add_to_bag_url, {'quantity': 2})
        self.assertRedirects(response, self.view_bag_url)
        bag = self.client.session.get('bag')
        self.assertIn(str(self.product.id), bag)
        self.assertEqual(bag[str(self.product.id)]['quantity'], 2)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                "Added Test Product to your bag." in str(m)
                for m in messages
            )
        )

    def test_update_quantity_in_bag(self):
        """
        Test updating the quantity of a product in the shopping bag.
        """
        self.client.post(self.add_to_bag_url, {'quantity': 2})
        update_url = reverse(
            'bag:update_quantity', args=[self.product.id]
        )
        response = self.client.post(update_url, {'quantity': 5})
        bag = self.client.session.get('bag')
        self.assertEqual(bag[str(self.product.id)]['quantity'], 5)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                "Updated Test Product quantity to 5." in str(m)
                for m in messages
            )
        )

    def test_remove_from_bag(self):
        """
        Test removing a product from the shopping bag.
        """
        self.client.post(self.add_to_bag_url, {'quantity': 2})
        response = self.client.post(self.remove_from_bag_url)
        bag = self.client.session.get('bag')
        self.assertNotIn(str(self.product.id), bag)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                "Test Product removed from your bag." in str(m)
                for m in messages
            )
        )

    def test_bag_calculations(self):
        """
        Test the bag calculations (total, delivery, grand total).
        """
        self.client.post(self.add_to_bag_url, {'quantity': 2})
        response = self.client.get(self.view_bag_url)
        self.assertContains(response, "200.00")
        self.assertContains(response, "20.00")
        self.assertContains(response, "220.00")

    def test_checkout_redirect_if_bag_empty(self):
        """
        Test redirect to bag view if the bag is empty during checkout.
        """
        checkout_url = reverse('bag:checkout')
        response = self.client.get(checkout_url)
        self.assertRedirects(response, self.view_bag_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                "Your bag is empty. Add items before proceeding to checkout."
                in str(m)
                for m in messages
            )
        )
