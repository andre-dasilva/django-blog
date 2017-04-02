from django.db.models import Q
from rest_framework.generics import (
    CreateAPIView, ListAPIView, RetrieveAPIView,
)
from rest_framework.mixins import DestroyModelMixin, UpdateModelMixin, CreateModelMixin
from rest_framework.filters import (
    SearchFilter, OrderingFilter
)
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from comments.models import Comment
from posts.api.permissions import IsOwnerOrReadOnly
from .serializers import CommentListSerializer, CommentDetailSerializer, create_comment_serializer

from posts.api.pagination import PostPageNumberPagination


class CommentCreateAPIView(CreateAPIView):
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        model_type = self.request.GET.get("type")
        slug = self.request.GET.get("slug")
        parent_id = self.request.GET.get("parent_id", None)

        return create_comment_serializer(model_type=model_type, slug=slug, parent_id=parent_id, user=self.request.user)


class CommentListAPIView(ListAPIView, CreateModelMixin):
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['content', 'user__first_name']
    pagination_class = PostPageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = CommentListSerializer

    def get_queryset(self):
        queryset_list = Comment.objects.all()
        query = self.request.GET.get("q")
        if query:
            queryset_list = queryset_list.filter(
                Q(content__icontains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query)).distinct()
        return queryset_list


class CommentDetailAPIView(DestroyModelMixin, UpdateModelMixin, RetrieveAPIView):
    queryset = Comment.objects.filter(id__gte=0)
    serializer_class = CommentDetailSerializer
    lookup_field = "id"
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

