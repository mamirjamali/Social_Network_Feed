"""
User Serializers.
"""
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _
from rest_framework import serializers
from core.models import Follower, Following


class UserSerializer(serializers.ModelSerializer):
    """User serializer"""
    class Meta:
        model = get_user_model()
        fields = ['email', 'username', 'name', 'password']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 6}}

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Auth token serializer"""
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
        min_length=6
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            email=email,
            password=password
        )

        if not user:
            msg = _('Invalid Credentials')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class UserFollowerSerializer(serializers.ModelSerializer):
    """User followers serailizer"""
    class Meta:
        model = Follower
        fields = ['target_user', 'follower_id', 'follower_name']
        read_only_fields = ['target_user',
                            'follower_id', 'follower_name']

    def create(self, validated_data):
        return Follower.objects.create(**validated_data)


class UserFollowingSerializer(UserFollowerSerializer):
    """User follower serializer"""
    class Meta:
        model = Following
        fields = ['user', 'following_id', 'following_name']
