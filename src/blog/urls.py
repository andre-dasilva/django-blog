"""blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework_jwt.views import obtain_jwt_token

from accounts import views as account

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/', account.login_view, name="login"),
    url(r'^logout/', account.logout_view, name="logout"),
    url(r'^register/', account.register_view, name="register"),
    url(r'^comments/', include("comments.urls", namespace="comments")),
    url(r'^api/auth/token/', obtain_jwt_token),
    url(r'^api/posts/', include("posts.api.urls", namespace="posts-api")),
    url(r'^api/comments/', include("comments.api.urls", namespace="comments-api")),
    url(r'^api/users/', include("accounts.api.urls", namespace="users-api")),
    url(r'^', include("posts.urls", namespace="posts")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

