"""
Test feed api end-point
"""
import os
import tempfile
from PIL import Image
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Feed, Tag
from feed.serializers import PostsSerializer, PostDetailsSerializer


FEED_URL = reverse('feed:posts-list')

# Helper Functions


def post_detail_url(post_id):
    """Return a post url"""
    return reverse('feed:posts-detail', args=[post_id])


def create_feed_post(user, **params):
    """Create sample feed"""
    default = {
        'title': 'Sample title',
        'description': 'Sample description',
    }

    default.update(params)

    feed_post = Feed.objects.create(user=user, **default)
    return feed_post


def create_user(**params):
    """Createing user"""
    return get_user_model().objects.create_user(**params)


def image_upload_url(post_id):
    """Get image url"""
    return reverse('feed:posts-upload-image', args=[post_id])


class PublicFeedApiTests(TestCase):
    """Test unathenticated request to feed endpoint"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_is_required(self):
        """Test authentication is required"""
        res = self.client.get(FEED_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateFeedApiTests(TestCase):
    """Test authentication required for feed api call"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example.com',
            password='testpass',
            username='testuser'
        )
        self.client.force_authenticate(self.user)

    def test_retrive_feed_posts(self):
        """Test feed api call return feed list"""
        create_feed_post(user=self.user)
        create_feed_post(user=self.user)

        res = self.client.get(FEED_URL)
        feed_post = Feed.objects.all().order_by('-id')
        serializer = PostsSerializer(feed_post, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_feed_post_limited_to_authenticated_user(self):
        """Test the feed shows the list post related to authenticated user"""
        user = create_user(
            email='newtest@example.com',
            password='newpass',
            username='testuser3'
        )
        create_feed_post(user)
        create_feed_post(self.user)

        res = self.client.get(FEED_URL)
        feed_post = Feed.objects.filter(user=self.user)
        serializer = PostsSerializer(feed_post, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotEqual(res.data, serializer.data)

    def test_retrive_post_details(self):
        """Test retriving details of a post"""
        feed_post = create_feed_post(user=self.user)
        url = post_detail_url(post_id=feed_post.id)

        res = self.client.get(url)
        serializer = PostDetailsSerializer(feed_post)

        self.assertEqual(res.data, serializer.data)

    def test_create_post_feed(self):
        """Test creating a post to the feed"""
        payload = {
            'title': 'Create sample title',
            'description': 'Create sample description',
        }

        res = self.client.post(FEED_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        post = Feed.objects.get(id=res.data['id'])
        for key, value in payload.items():
            self.assertEqual(getattr(post, key), value)
        self.assertEqual(post.user, self.user)

    def test_create_post_feed_with_not_allowed_words_in_descripiton(self):
        """Test creating a post to the feed"""
        payload = {
            'title': 'Create sample title',
            'description': 'Create Murder description',
        }

        res = self.client.post(FEED_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        post = Feed.objects.filter(title='Create sample title').exists()
        self.assertFalse(post)

    def test_partial_post_details_update(self):
        """Test partial updates for post"""
        description = "New Test Description"
        feed_post = create_feed_post(
            user=self.user,
            title="New Sample Title",
            description=description
        )
        payload = {'title': 'update title'}
        url = post_detail_url(feed_post.id)

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        feed_post.refresh_from_db()
        self.assertEqual(feed_post.title, payload['title'])
        self.assertEqual(feed_post.description, description)
        self.assertEqual(feed_post.user, self.user)

    def test_full_update_post_datails(self):
        """Test full update for a post"""
        feed_post = create_feed_post(
            user=self.user,
            title="New Sample Title",
            description="New Test Description"
        )
        payload = {'title': 'update title',
                   'description': 'update description'}
        url = post_detail_url(feed_post.id)

        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        feed_post.refresh_from_db()
        for key, value in payload.items():
            self.assertEqual(getattr(feed_post, key), value)
        self.assertEqual(feed_post.user, self.user)

    def test_other_user_can_update_post(self):
        """Test if other user can update the user post"""
        user = create_user(
            email='newtest@example.com',
            password='newpassword',
            username='testuser1'
        )
        title = 'New sample title'
        description = 'New sample description'
        feed_post = create_feed_post(
            user=user,
            title=title,
            description=description
        )
        payload = {
            'title': 'Change title',
            'description': 'Change description'
        }
        url = post_detail_url(feed_post.id)

        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        feed_post.refresh_from_db()
        self.assertEqual(feed_post.title, title)
        self.assertEqual(feed_post.description, description)

    def test_update_user_returm_error(self):
        """Test user can't update read-only field"""
        new_user = create_user(
            email='newuser@example.com',
            password='newpasstest',
            username='testuser2'
        )
        feed_post = create_feed_post(user=self.user)
        payload = {'user': new_user.id}
        url = post_detail_url(feed_post.id)

        self.client.patch(url, payload)

        feed_post.refresh_from_db()
        self.assertEqual(feed_post.user, self.user)

    def test_delete_post(self):
        """Test post deleting post"""
        feed_post = create_feed_post(
            user=self.user,
            title='Sample title',
            description='Sample description'
        )
        url = post_detail_url(feed_post.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Feed.objects.filter(id=feed_post.id).exists())

    def test_other_user_can_delete_post(self):
        """Test if other user can delete user post"""
        user = create_user(
            email='newtest@example.com',
            password='newpassword',
            username='testuser3'
        )
        feed_post = create_feed_post(user=user)
        url = post_detail_url(feed_post.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Feed.objects.filter(id=feed_post.id).exists())

    def test_create_feed_post_with_new_tag(self):
        """Test if user can create tag"""
        payload = {
            'title': 'Sample title',
            'description': 'Sample description',
            'tags': [{'name': 'Test tag'}, {'name': 'Test2 tag'}]

        }

        res = self.client.post(FEED_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        feed_post = Feed.objects.filter(id=res.data['id'])
        self.assertEqual(feed_post.count(), 1)
        post = feed_post[0]
        self.assertEqual(post.tags.count(), 2)
        for tag in payload['tags']:
            exist = post.tags.filter(
                name=tag['name']
            ).exists()
            self.assertTrue(exist)

    def test_create_feed_post_with_exsiting_tag(self):
        """Test if user can create tag"""
        Tag.objects.create(
            user=self.user,
            name='Test tag'
        )
        payload = {
            'title': 'Sample title',
            'description': 'Sample description',
            'tags': [{'name': 'Test tag'}]
        }

        res = self.client.post(FEED_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        feed_post = Feed.objects.filter(id=res.data['id'])
        self.assertEqual(feed_post.count(), 1)
        post = feed_post[0]
        self.assertEqual(post.tags.count(), 1)
        for tag in payload['tags']:
            exist = post.tags.filter(
                name=tag['name']
            ).exists()
            self.assertTrue(exist)

    def test_create_tag_on_update_feed_post(self):
        """Test if tag could be created through updating post"""
        feed_post = create_feed_post(self.user)
        url = post_detail_url(feed_post.id)
        payload = {'tags': [{'name': 'ALL Test tag'}]}

        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='ALL Test tag')
        self.assertIn(new_tag, feed_post.tags.all())

    def test_create_post_with_forbiden_tag_words(self):
        """Test if tags would created with forbiden words"""
        payload = {
            'title': 'Sample title',
            'description': 'Sample description',
            'tags': [{'name': 'Murderr'}]
        }

        res = self.client.post(FEED_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        new_tag = Tag.objects.filter(user=self.user, name='Murder')
        self.assertNotIn(new_tag, res.data)


class ImageUploadTest(TestCase):
    """Test upload image"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example.com',
            password="testpass",
            username='testuser'
        )
        self.client.force_authenticate(self.user)
        self.feed_post = create_feed_post(self.user)

    def tearDown(self):
        self.feed_post.image.delete()

    def test_upload_image_success(self):
        """Test if user can upload image successfuly"""
        url = image_upload_url(self.feed_post.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image': image_file}

            res = self.client.post(url, payload, format='multipart')

        self.feed_post.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.feed_post.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image."""
        url = image_upload_url(self.feed_post.id)
        payload = {'image': 'notanimage'}

        res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
