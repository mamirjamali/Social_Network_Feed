"""
Feed endpoint serializer
"""
from rest_framework import serializers
from core.models import Feed


class PostsSerializer(serializers.ModelSerializer):
    """Feed serializer"""
    class Meta:
        model = Feed
        fields = ['id', 'user', 'title', 'created_at']
        read_only_fields = ['user']


class PostDetailsSerializer(PostsSerializer):
    """Post details serializer"""
    class Meta(PostsSerializer.Meta):
        fields = PostsSerializer.Meta.fields + ['description']
