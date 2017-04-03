from django.conf.urls import url
from .views import PostListAPIView, PostDetailAPIView


urlpatterns = [
    url(r'^$', PostListAPIView.as_view(), name="list"),  # also create
    url(r'^(?P<slug>[\w-]+)/$', PostDetailAPIView.as_view(), name="detail"),  # also update and delete
]
