from django.db.models import Q
from rest_framework.generics import (
    CreateAPIView, ListAPIView, RetrieveAPIView, RetrieveUpdateAPIView, UpdateAPIView, DestroyAPIView,
)
from rest_framework.filters import (
    SearchFilter, OrderingFilter
)
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from comments.models import Comment
from .serializers import CommentSerializer

from posts.api.permissions import IsOwnerOrReadOnly
from posts.api.pagination import LimitOffsetPagination, PostPageNumberPagination


class CommentListAPIView(ListAPIView):
    serializer_class = CommentSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['content', 'user__first_name']
    pagination_class = PostPageNumberPagination

    def get_queryset(self):
        queryset_list = Comment.objects.all()
        query = self.request.GET.get("q")
        if query:
            queryset_list = queryset_list.filter(
                Q(content__icontains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query)).distinct()
        return queryset_list


class CommentDetailAPIView(RetrieveAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
