"""
Test models in core app.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
from core import models


def create_user(email="test@example.com", password="testpass"):
    """Handler function to create user"""
    return get_user_model().objects.create_user(email, password)


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
        i = 0
        for email, expected in sample_emails:
            i += 1
            user = get_user_model().objects.create_user(
                email,
                password='testpass',
                username=f'testuser{i}'
            )
            self.assertEqual(user.email, expected)

    def test_user_empty_email_raises_error(self):
        """Test if the user not provide an eamil, raises ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'testpass')

    def test_create_super_user(self):
        """Test create superuser."""
        user = get_user_model().objects.create_superuser(
            email="superuser@example.com",
            password="testsuperuser"
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_a_feed_post(self):
        """Test if user can create a new post on feed."""
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass',
            name='test name'
        )

        post_feed = models.Feed.objects.create(
            user=user,
            title='Sample post feed',
            description='Sample post feed description'
        )

        self.assertEqual(str(post_feed), post_feed.title)

    def test_create_tag(self):
        """Test create tag and assign to the user"""
        user = create_user()
        name = "test tag"

        res = models.Tag.objects.create(user=user, name=name)

        self.assertEqual(str(res), res.name)

    @patch('core.models.uuid.uuid4')
    def test_upload_image(self, mock_uuid):
        """Test uploading image through Feed model"""
        uuid = 'test_uuid'
        mock_uuid.return_value = uuid

        file_path = models.feed_post_image_url(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/posts/{uuid}.jpg')
