from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

class DemoAppTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_home_page_status_code(self):
        """Test that the home page loads successfully."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Test that the home page uses the correct template."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'demo/home.html')

    def test_authentication_required_pages(self):
        """Test that protected pages require authentication."""
        protected_urls = [
            reverse('profile'),
            reverse('dashboard'),
            # Add more protected URLs here
        ]
        
        for url in protected_urls:
            response = self.client.get(url)
            self.assertNotEqual(response.status_code, 200)  # Should redirect to login
            self.client.force_login(self.user)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.client.logout()

    def test_health_check_endpoint(self):
        """Test the health check endpoint used by Kubernetes."""
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})

    def test_static_files_served(self):
        """Test that static files are being served correctly."""
        response = self.client.get('/static/admin/css/base.css')
        self.assertEqual(response.status_code, 200)
