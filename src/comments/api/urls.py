from django.conf.urls import url
from .views import (
    CommentListAPIView,
    CommentDetailAPIView
)

urlpatterns = [
    url(r'^$', CommentListAPIView.as_view(), name="list"),
    url(r'^(?P<id>\d+)/$', CommentDetailAPIView.as_view(), name="detail"),
    # url(r'^(?P<id>\d+)/$', CommentDetailAPIView.as_view(), name="delete"),
]
