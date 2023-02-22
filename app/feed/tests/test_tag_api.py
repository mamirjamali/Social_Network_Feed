from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from core import models
from feed import serializers


TAG_URL = reverse('feed:tags-list')


def detail_url(tag_id):
    return reverse('feed:tags-detail', args=[tag_id])


def create_user(
    email='test@example.com',
    password='testpass',
    username='testuser'
):
    return get_user_model().objects.create_user(email, password)


class PublicTagApiTests(TestCase):
    """Test tags public api."""

    def setUp(self):
        self.client = APIClient()

    def test_public_tag_url(self):
        """Test if any user can see tag list"""
        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTests(TestCase):
    """Test tags private api"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_users_can_retrive_tags(self):
        """Test if user can retrive tag"""
        models.Tag.objects.create(user=self.user, name='New Tag')
        models.Tag.objects.create(user=self.user, name='New Tag2')

        res = self.client.get(TAG_URL)

        tags = models.Tag.objects.all().order_by('-name')
        serializer = serializers.TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_other_users_can_retrive_tags(self):
        """Test if every user can retrive each tag"""
        user = get_user_model().objects.create_user(
            email='test2@example.com',
            password='testpass2',
            username='testuser2'
        )
        models.Tag.objects.create(user=user, name='New Tag')
        models.Tag.objects.create(user=user, name='New Tag2')

        res = self.client.get(TAG_URL)

        tags = models.Tag.objects.all().order_by('-name')
        serializer = serializers.TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_user_can_edit_tags(self):
        """Test if user can edit their own tags"""
        tag = models.Tag.objects.create(user=self.user, name='Test tag')
        payload = {'name': 'new tag'}
        url = detail_url(tag_id=tag.id)

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_others_can_not_edit_user_tags(self):
        """Test if others can edit user tag"""
        user = get_user_model().objects.create_user(
            email="newtest@example.com",
            password='newpass',
            username='testuser2'
        )
        tag = models.Tag.objects.create(user=user, name='Test tag')
        url = detail_url(tag_id=tag.id)
        payload = {'name': 'new test'}

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        tag.refresh_from_db()
        self.assertNotEqual(tag.name, payload['name'])

    def test_filter_return_aasigned_tag(self):
        """Test return only tags assigned to feed posts"""
        tag1 = models.Tag.objects.create(
            user=self.user,
            name='Test tag1'
        )
        tag2 = models.Tag.objects.create(
            user=self.user,
            name='Test tag2'
        )
        payload = {
            'title': 'Sample title',
            'description': 'Sample description',
        }
        feed_post = models.Feed.objects.create(user=self.user, **payload)
        feed_post.tags.add(tag1)

        res = self.client.get(TAG_URL, {'assigned_only': '1'})
        s1 = serializers.TagSerializer(tag1)
        s2 = serializers.TagSerializer(tag2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_return_unique_values(self):
        """Test filtering tags will return a unique values"""
        tag = models.Tag.objects.create(
            user=self.user,
            name='Test tag1'
        )
        models.Tag.objects.create(user=self.user, name='Test tag2')
        payload = {
            'title': 'Sample title',
            'description': 'Sample description',
        }
        payload2 = {
            'title': 'Sample2 title',
            'description': 'Sample2 description',
        }
        feed_post = models.Feed.objects.create(user=self.user, **payload)
        feed_post = models.Feed.objects.create(user=self.user, **payload2)
        feed_post.tags.add(tag)
        feed_post.tags.add(tag)

        res = self.client.get(TAG_URL, {'assigned_only': '1'})

        self.assertEqual(len(res.data), 1)
