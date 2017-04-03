from django.db.models import Q
from rest_framework.generics import (
    ListAPIView, RetrieveAPIView
)
from rest_framework.filters import (
    SearchFilter, OrderingFilter
)
from rest_framework.mixins import DestroyModelMixin, UpdateModelMixin, CreateModelMixin
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from posts.models import Post
from .serializers import PostListSerializer, PostDetailSerializer
from .permissions import IsOwnerOrReadOnly


class PostListAPIView(ListAPIView, CreateModelMixin):
    serializer_class = PostListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'content', 'user__first_name']
    # pagination_class = PostPageNumberPagination / enable if needed
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset_list = Post.objects.all()
        query = self.request.GET.get("q")
        if query:
            queryset_list = queryset_list.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query)).distinct()
        return queryset_list

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def post(self, request, *args, **kwargs):
        return self.create(request, args, kwargs)


class PostDetailAPIView(RetrieveAPIView, DestroyModelMixin, UpdateModelMixin):
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer
    permission_classes = [IsOwnerOrReadOnly]
    lookup_field = "slug"

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

