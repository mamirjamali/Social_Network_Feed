"""
Feed endpoint view, handle requests
"""
from rest_framework import (
    viewsets,
    permissions,
    authentication,
    mixins,
    response,
    status
)
from feed import serializers
from core.models import Feed, Tag


class PostsViewSet(viewsets.ModelViewSet):
    """View for feed api"""
    serializer_class = serializers.PostDetailsSerializer
    queryset = Feed.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def get_queryset(self):
        return self.queryset.order_by('-id')

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.PostsSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        instance.delete()

    def destroy(self, request, pk=None):
        instance = self.get_object()
        if instance.user != request.user:
            return response.Response(
                {'You are not allowed to delete this object'},
                status.HTTP_400_BAD_REQUEST
            )

        try:
            post = self.perform_destroy(instance)
            return response.Response(
                {'Item deleted'},
                status.HTTP_204_NO_CONTENT
            )
        except post.DoesNotExist:
            pass


class TagViewSet(mixins.ListModelMixin,
                 mixins.UpdateModelMixin,
                 viewsets.GenericViewSet):
    """View for tag api"""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def get_queryset(self):
        return self.queryset.order_by('-name')
