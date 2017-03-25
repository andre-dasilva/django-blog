from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, Http404
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Comment
from .forms import CommentForm


@login_required
def comment_thread(request, id):
    try:
        obj = Comment.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404

    initial_data = {
        "content_type": obj.content_type,
        "object_id": obj.object_id
    }

    form = CommentForm(request.POST or None, initial=initial_data)
    if form.is_valid():
        c_type = form.cleaned_data.get("content_type")
        content_type = ContentType.objects.get(model=c_type)
        object_id = form.cleaned_data.get("object_id")
        content_data = form.cleaned_data.get("content")
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
        messages.success(request, "Reply was successfully saved")
        return HttpResponseRedirect(new_comment.get_parent_url())

    context = {
        "comment": obj,
        "form": form,
    }
    return render(request, "comment_thread.html", context)


@login_required
def comment_delete(request, id):
    try:
        obj = Comment.objects.get(id=id)
    except ObjectDoesNotExist:
        raise Http404

    if obj.user != request.user:
        # response = HttpResponse("You don't have the permissions to delete this comment")
        # response.status_code = 403
        # return response
        messages.error(request, "You don't have the permissions to delete this comment")
        return HttpResponseRedirect(obj.get_absolute_url())

    if request.method == "POST":
        url = obj.content_object.get_absolute_url()
        obj.delete()
        messages.success(request, "The comment \"{}\" has been successfully deleted".format(obj.content))

        if not obj.is_parent:
            return HttpResponseRedirect(obj.get_parent_url())
        return HttpResponseRedirect(url)

    return render(request, "confirm_delete.html", {"obj": obj})

