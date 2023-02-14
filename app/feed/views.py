"""
Feed endpoint view, handle requests
"""
from rest_framework import viewsets, permissions, authentication
from feed import serializers
from core.models import Feed


class PostsViewSet(viewsets.ModelViewSet):
    """View for feed APIs"""
    serializer_class = serializers.PostDetailsSerializer
    queryset = Feed.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.PostsSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
