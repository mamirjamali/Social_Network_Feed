"""
Feed endpoint view, handle requests
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import (
    viewsets,
    permissions,
    authentication,
    mixins,
    response,
    status,
)
from rest_framework.decorators import action
from feed import serializers
from core.models import Feed, Tag


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Comma seperated list of tags ids to filter'
            )
        ]
    )
)
class PostsViewSet(viewsets.ModelViewSet):
    """View for feed api"""
    serializer_class = serializers.PostDetailsSerializer
    queryset = Feed.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def _query_to_int(self, items):
        """Convert string query params to intiger"""
        return [int(item) for item in items.split(',')]

    def get_queryset(self):
        tags = self.request.query_params.get('tags')
        queryset = self.queryset
        if tags:
            tag_ids = self._query_to_int(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)

        return queryset.order_by('-id').distinct()

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.PostsSerializer
        if self.action == 'upload_image':
            return serializers.ImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        instance.delete()

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Custom action to control upload image"""
        feed_post = self.get_object()
        serializer = self.get_serializer(feed_post, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status.HTTP_200_OK)

        return response.Response(
            serializer.errors,
            status.HTTP_400_BAD_REQUEST
        )

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


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT, enum=[0, 1],
                description='Filter by tags assigned to feed posts'
            )
        ]
    )
)
class TagViewSet(mixins.ListModelMixin,
                 mixins.UpdateModelMixin,
                 viewsets.GenericViewSet):
    """View for tag api"""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def get_queryset(self):
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(feed__isnull=False)

        return queryset.order_by('-id').distinct()
