from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class ProfileAccountViewTests(TestCase):
    """Tests for profile account update view"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@app.local",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

    def test_profile_account_get_requires_login(self):
        """Test that profile-account view requires authentication"""
        response = self.client.get(reverse("profile-account"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_profile_account_get_authenticated(self):
        """Test that authenticated user can access profile-account view"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("profile-account"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Account Information")
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.user.email)

    def test_profile_account_post_updates_user(self):
        """Test that POST request updates user profile"""
        self.client.login(username="testuser", password="testpass123")
        data = {
            "username": "newusername",
            "email": "newemail@app.local",
            "first_name": "NewTest",
            "last_name": "NewUser",
        }
        response = self.client.post(reverse("profile-account"), data)
        self.assertEqual(response.status_code, 200)

        # Verify user was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "newusername")
        self.assertEqual(self.user.email, "newemail@app.local")
        self.assertEqual(self.user.first_name, "NewTest")
        self.assertEqual(self.user.last_name, "NewUser")

    def test_profile_account_post_duplicate_username(self):
        """Test that duplicate username is rejected"""
        # Create another user
        User.objects.create_user(
            username="anotheruser",
            email="another@app.local",
            password="testpass123",
        )

        self.client.login(username="testuser", password="testpass123")
        data = {
            "username": "anotheruser",  # Try to use existing username
            "email": "test@app.local",
            "first_name": "Test",
            "last_name": "User",
        }
        response = self.client.post(reverse("profile-account"), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already taken")

    def test_profile_account_post_duplicate_email(self):
        """Test that duplicate email is rejected"""
        # Create another user
        User.objects.create_user(
            username="anotheruser",
            email="another@app.local",
            password="testpass123",
        )

        self.client.login(username="testuser", password="testpass123")
        data = {
            "username": "testuser",
            "email": "another@app.local",  # Try to use existing email
            "first_name": "Test",
            "last_name": "User",
        }
        response = self.client.post(reverse("profile-account"), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already in use")

    def test_profile_account_post_htmx_response(self):
        """Test that HTMX POST request returns correct partial"""
        self.client.login(username="testuser", password="testpass123")
        data = {
            "username": "testuser",
            "email": "test@app.local",
            "first_name": "Test",
            "last_name": "User",
        }
        response = self.client.post(
            reverse("profile-account"),
            data,
            HTTP_HX_REQUEST="true",  # Simulate HTMX request
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Account Information")
        # Verify it returns the partial template
        self.assertContains(response, "app-card")

    def test_profile_security_get_authenticated(self):
        """Test that authenticated user can access profile-security view"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("profile-security"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Security")
        self.assertContains(response, "Role and Permissions")

    def test_profile_security_get_requires_login(self):
        """Test that profile-security view requires authentication"""
        response = self.client.get(reverse("profile-security"))
        self.assertEqual(response.status_code, 302)  # Redirect to login
