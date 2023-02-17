from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from core import models
from feed import serializers


TAG_URL = reverse('feed:tag-list')


def detail_url(tag_id):
    return reverse('feed:tag-detail', args=[tag_id])


def create_user(email='test@example.com', password='testpass'):
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
            email='test2@example.com', password='testpass2')
        models.Tag.objects.create(user=user, name='New Tag')
        models.Tag.objects.create(user=user, name='New Tag2')

        res = self.client.get(TAG_URL)

        tags = models.Tag.objects.all().order_by('-name')
        serializer = serializers.TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    # def test_user_can_edit_tags_200(self):
    #     """Test if user can edit their own tags"""
    #     tag = models.Tag.objects.create(self.user, name='Test tag')
    #     name = 'new tag'
    #     url = detail_url(tag_id=tag.id)

    #     res = self.client.patch(url, name)

    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     tag.refresh_from_db()
    #     self.assertEqual(tag.name, name)

    # def test_others_can_not_edit_user_tags_403(self):
    #     """Test if others can edit user tag"""
    #     user = get_user_model().objects.create_user(
    #         email="newtest@example.com",
    #         password='newpass'
    #     )
    #     tag = models.Tag.objects.create(user, name='Test tag')
    #     url = detail_url(tag_id=tag.id)
    #     name = 'new test'

    #     res = self.client.patch(url, name)

    #     self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
    #     tag.refresh_from_db()
    #     self.assertNotEqual(tag.name, name)

    # def test_user_can_delete_tag_204(self):
    #     """Test if user can delete their won tags"""
    #     tag = models.Tag.objects.create(self.user, name='Test tag')
    #     url = detail_url(tag_id=tag.id)

    #     res = self.client.delete(url)

    #     self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
    #     self.assertFalse(models.Tag.objects.filter(id=tag.id).exists())
