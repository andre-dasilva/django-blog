from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class CommentManager(models.Manager):
    def all(self):
        return super(CommentManager, self).filter(parent=None)

    def filter_by_instance(self, instance):
        content_type = ContentType.objects.get_for_model(instance.__class__)
        obj_id = instance.id
        return super(CommentManager, self).filter(content_type=content_type, object_id=obj_id).filter(parent=None)


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)
    # Normal foreign key for one post
    # post = models.ForeignKey(Post)

    # Generic foreign key -> advantage: see all available tables as foreign key
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    parent = models.ForeignKey("self", null=True, blank=True)

    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = CommentManager()

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return str(self.user.username)

    def get_absolute_url(self):
        return reverse("comments:comment_thread", kwargs={"id": self.id})

    def get_parent_url(self):
        return reverse("comments:comment_thread", kwargs={"id": self.parent.id})

    def children(self):  # replies to comments
        return Comment.objects.filter(parent=self)

    @property
    def is_parent(self):
        if self.parent is not None:
            return False
        return True
