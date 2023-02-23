"""
User View.
"""
from django.shortcuts import get_object_or_404
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.exceptions import ValidationError
from rest_framework import mixins, viewsets
from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
    UserFollowerSerializer,
    UserFollowingSerializer
)
from core.models import User, Follower, Following
from user.signals import follow_user


class CreateUserView(generics.CreateAPIView):
    """Create new user"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create auth token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile view"""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrive and return authenticated user"""
        username = self.kwargs['username']
        return get_object_or_404(User, username=username)


class UserFollowerViewSet(mixins.ListModelMixin,
                          mixins.CreateModelMixin,
                          viewsets.GenericViewSet):
    """User follower viewset"""
    serializer_class = UserFollowerSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Follower.objects.all()

    def get_queryset(self):
        username = self.kwargs['username']
        return self.queryset.filter(target_user__username=username)

    def perform_create(self, serializer):
        username = self.kwargs['username']
        target = get_object_or_404(User, username=username)
        current_user = get_object_or_404(
            User, username=self.request.user.username)

        current_user_id = current_user.id
        queryset = self.queryset.filter(
            target_user=target, follower_id=current_user_id)

        if current_user_id == target.id or queryset.exists():
            raise ValidationError({'detail': 'Not allowed'})

        payload = {
            'user': current_user,
            'following_id': target.id,
            'following_name': target.name
        }

        serializer.save(
            target_user=target,
            follower_id=current_user_id,
            follower_name=self.request.user
        )
        follow_user.send_robust(self.__class__, data=payload)


class UserFollowingViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """User following viewset"""
    serializer_class = UserFollowingSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Following.objects.all()

    def get_queryset(self):
        username = self.kwargs['username']
        return self.queryset.filter(user__username=username)
