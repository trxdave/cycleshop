from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from products.models import Product, Category, Wishlist


class ProductViewsTest(TestCase):
    def setUp(self):
        """
        Setup initial data for testing.
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpassword'
        )
        self.superuser = User.objects.create_superuser(
            username='admin', password='adminpassword'
        )
        self.category = Category.objects.create(
            name='Test Category', slug='test-category'
        )
        self.product = Product.objects.create(
            name='Test Product',
            price=100.00,
            category=self.category
        )
        self.product_list_url = reverse('products:product_list')
        self.product_detail_url = reverse(
            'products:product_detail', args=[self.product.id]
        )
        self.manage_products_url = reverse('products:manage_products')
        self.add_to_wishlist_url = reverse(
            'products:add_to_wishlist', args=[self.product.id]
        )
        self.view_wishlist_url = reverse('products:view_wishlist')

    def test_product_list_page_loads(self):
        """
        Test if the product list page loads successfully.
        """
        response = self.client.get(self.product_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_list.html')
        self.assertContains(response, 'Test Product')

    def test_product_detail_page_loads(self):
        """
        Test if the product detail page loads successfully.
        """
        response = self.client.get(self.product_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_detail.html')
        self.assertContains(response, 'Test Product')

    def test_manage_products_requires_superuser(self):
        """
        Test that only superusers can access the manage products page.
        """
        response = self.client.get(self.manage_products_url)
        self.assertRedirects(
            response, '/accounts/login/?next=' + self.manage_products_url
        )

        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(self.manage_products_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/manage_products.html')

    def test_add_to_wishlist(self):
        """
        Test adding a product to the wishlist.
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(self.add_to_wishlist_url)
        self.assertRedirects(response, self.product_detail_url)
        wishlist = Wishlist.objects.get(user=self.user)
        self.assertIn(self.product, wishlist.products.all())

    def test_view_wishlist(self):
        """
        Test viewing the wishlist.
        """
        self.client.login(username='testuser', password='testpassword')
        wishlist = Wishlist.objects.create(user=self.user)
        wishlist.products.add(self.product)

        response = self.client.get(self.view_wishlist_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/wishlist.html')
        self.assertContains(response, 'Test Product')

    def test_toggle_wishlist(self):
        """
        Test toggling a product in the wishlist.
        """
        self.client.login(username='testuser', password='testpassword')
        toggle_wishlist_url = reverse(
            'products:toggle_wishlist', args=[self.product.id]
        )

        # Add to wishlist
        response = self.client.post(toggle_wishlist_url)
        self.assertRedirects(response, self.product_detail_url)
        wishlist = Wishlist.objects.get(user=self.user)
        self.assertIn(self.product, wishlist.products.all())

        # Remove from wishlist
        response = self.client.post(toggle_wishlist_url)
        wishlist.refresh_from_db()
        self.assertNotIn(self.product, wishlist.products.all())

    def test_product_category_page_loads(self):
        """
        Test if products by category page loads successfully.
        """
        category_url = reverse(
            'products:product_category', args=[self.category.slug]
        )
        response = self.client.get(category_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/category_products.html')
        self.assertContains(response, 'Test Product')
