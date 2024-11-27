from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from cycleshop.models import Profile, NewsletterSubscriber
from products.models import Product


class CycleshopViewsTest(TestCase):
    def setUp(self):
        """
        Setup test client, user, and initial data for testing.
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        self.profile = Profile.objects.create(
            user=self.user,
            location='Test Location',
            bio='Test Bio',
        )
        self.product = Product.objects.create(
            name='Test Product',
            price=100.00,
        )
        self.home_url = reverse('home')
        self.contact_url = reverse('contact')
        self.search_url = reverse('search_results')
        self.view_profile_url = reverse('view_profile')
        self.edit_profile_url = reverse('edit_profile')
        self.delete_profile_url = reverse('delete_profile')

    def test_home_page(self):
        """
        Test if the home page loads successfully.
        """
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cycleshop/home.html')

    def test_contact_form_submission(self):
        """
        Test the contact form submission.
        """
        response = self.client.post(self.contact_url, {
            'name': 'Test User',
            'email': 'test@example.com',
            'message': 'Test Message'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Your message has been successfully sent.'
        )

    def test_search_request(self):
        """
        Test the search request and results.
        """
        response = self.client.get(self.search_url, {'q': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cycleshop/search_results.html')
        self.assertContains(response, 'Test Product')

    def test_view_profile(self):
        """
        Test if the profile page loads for authenticated users.
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.view_profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/view_profile.html')
        self.assertContains(response, 'Test Bio')

    def test_edit_profile(self):
        """
        Test editing the user's profile.
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(self.edit_profile_url, {
            'location': 'Updated Location',
            'bio': 'Updated Bio',
        })
        self.profile.refresh_from_db()
        self.assertRedirects(response, self.view_profile_url)
        self.assertEqual(self.profile.location, 'Updated Location')
        self.assertEqual(self.profile.bio, 'Updated Bio')

    def test_delete_profile(self):
        """
        Test deleting the user's profile.
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(self.delete_profile_url)
        self.assertRedirects(response, self.home_url)
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def test_subscribe_newsletter(self):
        """
        Test subscribing to the newsletter.
        """
        response = self.client.post(reverse('subscribe_newsletter'), {
            'email': 'test@example.com'
        })
        self.assertRedirects(response, self.home_url)
        self.assertTrue(
            NewsletterSubscriber.objects.filter(
                email='test@example.com'
            ).exists()
        )

    def test_handler_404(self):
        """
        Test the custom 404 handler.
        """
        response = self.client.get('/nonexistent-url/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'templates/404.html')

    def test_handler_500(self):
        """
        Test the custom 500 handler (simulated).
        """
        with self.assertRaises(Exception):
            self.client.get('/simulate-500-error/')
