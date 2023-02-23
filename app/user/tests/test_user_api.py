"""
Test user api
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
import json


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def profile_url(username):
    return reverse('user:me', args=[username])


def following_url(username):
    """Get the url to get the following list of <username>"""
    return reverse('user:me', args=[username]) + 'following/'


def follower_url(username):
    """Get the url to send post request to follow <username>"""
    return reverse('user:me', args=[username]) + 'follower/'


def create_user(**params):
    """Create and return user"""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the public features of the user api"""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test create a user successful"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpassword',
            'name': 'test name',
            'username': 'testuser'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_existing_email(self):
        """Test return error if users' email exist"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpassword',
            'name': 'test name'
        }

        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test if password is too short"""
        payload = {
            'email': 'teat@example.com',
            'password': 'qw',
            'name': 'test name'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exist = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exist)

    def test_token_create(self):
        """Test creating a token for user"""
        user_details = {
            'email': 'test@example.com',
            'password': 'testpass',
            'name': 'test name'
        }
        create_user(**user_details)

        payload = {
            'email': 'test@example.com',
            'password': 'testpass',
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_with_invalid_credentials(self):
        """Test response with invalid credentials """
        user_details = {
            'email': 'test@example.com',
            'password': 'goodpass',
            'name': 'test name'
        }
        create_user(**user_details)

        payload = {
            'email': 'test@example.com',
            'password': 'badpass',
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_with_blank_password(self):
        """Test response with blank password """
        payload = {
            'email': 'test@example.com',
            'password': '',
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_profile_endpoint_without_authentication(self):
        """Test /me endpoint without credentials return forbiden"""
        user = create_user(
            name="test12",
            email="test@example.com",
            password="test1234",
            username='testusername'
        )
        url = profile_url(user.username)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test private api with authentication"""

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            username='testuser',
            name='testname',
            password='testpassword',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_get_profile_endpoint_success(self):
        """Test logged in user can access the profile endpoint"""
        url = profile_url(self.user.username)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': self.user.email,
            'name': self.user.name,
            'username': self.user.username
        })

    def test_post_method_profile_not_allowed(self):
        """Test POST method is not allowed in profile endpoint"""
        url = profile_url(self.user.name)
        res = self.client.post(url, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_user_can_update_profile(self):
        """Test user can update its' profile"""
        url = profile_url(self.user.username)
        payload = {
            'name': 'new test',
            'password': 'newtestpass'
        }

        res = self.client.patch(url, payload)
        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_user_can_follow_others(self):
        """Test if user can follow other users"""
        user = create_user(
            name='followertest',
            email='follower@example.com',
            password='test123',
            username='testusername'
        )
        url = follower_url(user.username)

        self.client.post(url, {
            'user': self.user,
            'username': self.user.username
        })
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(self.user.name, json.dumps(res.data))

    def test_user_will_be_add_to_following_list(self):
        """Test after following a user, it will be add to following list"""
        user = create_user(
            name='followertest',
            email='follower@example.com',
            password='test123',
            username='testusername'
        )
        url = follower_url(user.username)

        self.client.post(url, {})
        url2 = following_url(self.user.username)
        res = self.client.get(url2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(user.name, json.dumps(res.data))

    def test_user_can_follow_other_once(self):
        """Test user can follow other users if they haven't before"""
        user = create_user(
            name='followertest',
            email='follower@example.com',
            password='test123',
            username='testusername'
        )
        url = follower_url(user.username)

        self.client.post(url, {})
        res1 = self.client.post(url, {})
        res2 = self.client.get(url, {})

        self.assertEqual(res1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(res2.data), 1)
