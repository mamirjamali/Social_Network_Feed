"""
Test feed api end-point
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Feed
from feed.serializers import PostsSerializer, PostDetailsSerializer


FEED_URL = reverse('feed:posts-list')


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

# Helper Function


def create_user(**params):
    """Createing user"""
    return get_user_model().objects.create_user(**params)


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
        self.user = create_user(email='test@example.com', password='testpass')
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
        user = create_user(email='newtest@example.com', password='newpass')
        create_feed_post(user)
        create_feed_post(self.user)

        res = self.client.get(FEED_URL)
        feed_post = Feed.objects.filter(user=self.user)
        serializer = PostsSerializer(feed_post, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

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
            password='newpassword'
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

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        feed_post.refresh_from_db()
        self.assertEqual(feed_post.title, title)
        self.assertEqual(feed_post.description, description)

    def test_update_user_returm_error(self):
        """Test user can't update read-only field"""
        new_user = create_user(
            email='newuser@example.com', password='newpasstest')
        feed_post = create_feed_post(user=self.user)
        payload = {'user': new_user.id}
        url = post_detail_url(feed_post.id)

        res = self.client.patch(url, payload)

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
            password='newpassword'
        )
        feed_post = create_feed_post(user=user)
        url = post_detail_url(feed_post.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Feed.objects.filter(id=feed_post.id).exists())
