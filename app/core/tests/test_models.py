"""
Test models in core app.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelsTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successfull(self):
        """Test creating user with email by using default user model."""
        email = 'test@example.com'
        password = 'testpassword'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_user_email_normalized(self):
        """Test if user email is normalized after registeration"""
        sample_emails = [
            ['test1@Example.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'testpass')
            self.assertEqual(user.email, expected)

    def test_user_empty_email_raises_error(self):
        """Test if the user not provide an eamil, raises ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'testpass')
