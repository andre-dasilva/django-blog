import os
from urllib.parse import quote_plus
from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect, Http404
from django.http import HttpResponseRedirect
from django.utils import timezone
from .models import Post
from .forms import PostForm
from comments.forms import CommentForm
from comments.models import Comment

# TODO: Add logging, favicon.ico and push to GitHub and of course finish advancing the blog and rest framework
# https://docs.djangoproject.com/en/1.10/topics/logging/


def post_create(request):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404

    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.save()
        messages.success(request, "Successfully created")
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "title": "Form",
        "form": form,
    }
    return render(request, "post_form.html", context)


def post_detail(request, slug=None):
    instance = get_object_or_404(Post, slug=slug)
    if instance.draft or instance.publish > timezone.now().date():
        if not request.user.is_staff or not request.user.is_superuser:
            raise Http404
    share_string = quote_plus(instance.content)

    initial_data = {
        "content_type": instance.get_content_type,
        "object_id": instance.id
    }

    comment_form = CommentForm(request.POST or None, initial=initial_data)
    if comment_form.is_valid():
        c_type = comment_form.cleaned_data.get("content_type")
        content_type = ContentType.objects.get(model=c_type)
        object_id = comment_form.cleaned_data.get("object_id")
        content_data = comment_form.cleaned_data.get("content")
        parent_obj = None
        try:
            parent_id = int(request.POST.get("parent_id"))
        except (ValueError, TypeError):
            parent_id = None

        if parent_id:
            parent_qs = Comment.objects.filter(id=parent_id)
            if parent_qs.exists() and parent_qs.count() == 1:
                parent_obj = parent_qs.first()

        new_comment, created = Comment.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=object_id,
            content=content_data,
            parent=parent_obj
        )
        messages.success(request, "Comment was successfully saved")
        return HttpResponseRedirect(new_comment.content_object.get_absolute_url())

    comments = Comment.objects.filter_by_instance(instance)

    context = {
        "title": "Detail view",
        "instance": instance,
        "share_string": share_string,
        "comments": comments,
        "comment_form": comment_form,
    }
    return render(request, "post_detail.html", context)


def post_list(request):
    today = timezone.now().date()
    queryset_list = Post.objects.active()
    if request.user.is_staff or request.user.is_superuser:
        queryset_list = Post.objects.all()

    query = request.GET.get("q")
    if query:
        queryset_list = queryset_list.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query)).distinct()

    paginator = Paginator(queryset_list, 3)
    page = request.GET.get('page')
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        queryset = paginator.page(1)
    except EmptyPage:
        queryset = paginator.page(paginator.num_pages)

    context = {
        "object_list": queryset,
        "title": "Blog",
        "today": today,
    }
    return render(request, "post_list.html", context)


def post_update(request, slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404

    instance = get_object_or_404(Post, slug=slug)
    form = PostForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, "Successfully updated")
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "title": "Edit view",
        "instance": instance,
        "form": form,
    }
    return render(request, "post_form.html", context)


def post_delete(request, slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        messages.error(request, "You don't have the permissions to delete this post")
        raise Http404

    instance = get_object_or_404(Post, slug=slug)

    os.remove(instance.image.path)
    __folder_cleanup(os.path.dirname(instance.image.path))

    instance.delete()

    messages.success(request, "Successfully deleted")
    return redirect("posts:list")


def __folder_cleanup(path):
    """
    Removes all empty folders from path to settings.MEDIA_ROOT recursively

    This method starts in the path folder and checks if the folder is empty,
    if so it deletes it. After that it makes a recursive call with the parent directory of path
    and does the same. If at any point the function can't remove the directory it stops
    :param path: The path to start the recursion
    :return: None
    """
    if path == settings.MEDIA_ROOT:
        return
    try:
        ds_store = os.path.join(path, ".DS_Store")  # For MAC OS
        if os.path.exists(ds_store):
            os.remove(ds_store)
        os.rmdir(path)
    except OSError:
        return
    return __folder_cleanup(os.path.dirname(path))
