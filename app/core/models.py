"""
Database Models
"""
import os
import uuid
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
)
from django.conf import settings


def feed_post_image_url(instance, filename):
    """Generate path with uuid for image"""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'posts', filename)


class ProfileManager(BaseUserManager):
    """Manager for user proifiles"""

    def create_user(self, email, password=None, **extra_fields):

        if not email:
            raise ValueError("User must have an email")

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, **extra_fields):

        user = self.create_user(email, password, **extra_fields)

        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Define user model for the system"""

    email = models.EmailField(max_length=254, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = ProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def get_full_name(self):
        self.name

    def get_short_name(self):
        self.name

    def __str__(self):
        return self.name


class Feed(models.Model):
    """Feed model"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feed'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField('Tag')
    image = models.ImageField(null=True, upload_to=feed_post_image_url)

    def __str__(self):
        return self.title


class Tag(models.Model):
    """Tag model"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name
