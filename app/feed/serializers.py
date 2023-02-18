"""
Feed endpoint serializer
"""
from rest_framework import serializers
from core.models import Feed, Tag
from feed import validators


class TagSerializer(serializers.ModelSerializer):
    """Tag serializer"""
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        """Only creator can update the tag"""
        user = self.context['request'].user
        print(user)
        if instance.user != user:
            raise serializers.ValidationError(
                "You are not allowed to update this tag"
            )
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class PostsSerializer(serializers.ModelSerializer):
    """Feed serializer"""
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Feed
        fields = ['id', 'user', 'title', 'created_at', 'tags']
        read_only_fields = ['user']

    def _get_user(self):
        requested_user = self.context['request'].user
        return requested_user

    def _validate_user(self, instance):
        """Check user privilage for update and delete"""
        user = self._get_user()
        if instance.user != user:
            raise serializers.ValidationError(
                "You are not allowed to update this tag"
            )

    def _get_or_create_tag(self, tags, post):
        """Create tag if dosen't exist else get from database"""
        user = self._get_user()
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=user,
                **tag
            )
            post.tags.add(tag_obj)

    def validate_tags(self, value):
        """Validate tags to not contain not_allowed words"""
        for tag in value:
            validators.check_allowed_words(tag['name'])
        return value

    def create(self, validated_data):
        """Overwite default create method to support tags"""
        tags = validated_data.pop('tags', [])
        post = Feed.objects.create(**validated_data)
        self._get_or_create_tag(tags, post)
        return post

    def update(self, instance, validated_data):
        """Only creator can update the post"""
        self._validate_user(instance)

        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tag(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class PostDetailsSerializer(PostsSerializer):
    """Post details serializer"""
    class Meta(PostsSerializer.Meta):
        fields = PostsSerializer.Meta.fields + ['description']

    def validate_description(self, value):
        """Validate description to not contain not_allowed words"""
        validators.check_allowed_words(value)
        return value
