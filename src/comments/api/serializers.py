from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, HyperlinkedIdentityField, SerializerMethodField
from comments.models import Comment
from accounts.api.serializers import UserDetailSerializer

User = get_user_model()


def create_comment_serializer(model_type="post", slug=None, parent_id=None, user=None):
    class CommentCreateSerializer(ModelSerializer):
        class Meta:
            model = Comment
            fields = [
                'id',
                'content',
                'timestamp',
            ]

        def __init__(self, *args, **kwargs):
            self.model_type = model_type
            self.slug = slug
            self.parent_obj = None

            if parent_id:
                parent_qs = Comment.objects.filter(id=parent_id)
                if parent_qs.exists() and parent_qs.count() == 1:
                    self.parent_obj = parent_qs.first()

            super(CommentCreateSerializer, self).__init__(*args, **kwargs)

        def validate(self, data):
            m_type = self.model_type
            model_qs = ContentType.objects.filter(model=m_type)
            if not model_qs.exists() or model_qs.count() != 1:
                raise ValidationError("This is not a valid content type")
            some_model = model_qs.first().model_class()
            obj_qs = some_model.objects.filter(slug=self.slug)
            if not obj_qs.exists() or obj_qs.count() != 1:
                raise ValidationError("This is not a slug for this content type")
            return data

        def create(self, validated_data):
            content = validated_data.get("content")
            if user:
                main_user = user
            else:
                main_user = User.objects.all.first()
            m_type = self.model_type
            sl = self.slug
            parent_obj = self.parent_obj
            comment = Comment.objects.create_by_model_type(m_type, sl, content, main_user, parent_obj)
            return comment

    return CommentCreateSerializer


class CommentListSerializer(ModelSerializer):
    reply_count = SerializerMethodField()
    detail_url = HyperlinkedIdentityField(
       view_name='comments-api:detail',
       lookup_field='id'
    )
    user = SerializerMethodField()
    content_object_url = SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id',
            'user',
            'parent',
            'content_object_url',
            'detail_url',
            'content',
            'reply_count',
            'timestamp',
        ]

    def get_user(self, obj):
        return str(obj.user.username)

    def get_content_object_url(self, obj):
        request = self.context["request"]
        if obj.content_object:
            return request.build_absolute_uri(obj.content_object.get_api_url())
        return None

    def get_reply_count(self, obj):
        if obj.is_parent:
            return obj.children().count()
        return 0


class CommentChildSerializer(ModelSerializer):
    user = UserDetailSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id',
            'user',
            'content',
            'timestamp',
        ]


class CommentDetailSerializer(ModelSerializer):
    reply_count = SerializerMethodField()
    replies = SerializerMethodField()
    content_object_url = SerializerMethodField()
    user = UserDetailSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id',
            'user',
            'content',
            'reply_count',
            'replies',
            'content_object_url',
            'timestamp',
        ]
        read_only_fields = [
            "reply_count",
            "replies",
        ]

    def get_content_object_url(self, obj):
        request = self.context["request"]
        if obj.content_object:
            return request.build_absolute_uri(obj.content_object.get_api_url())
        return None

    def get_replies(self, obj):
        if obj.is_parent:
            return CommentChildSerializer(obj.children(), many=True).data
        return None

    def get_reply_count(self, obj):
        if obj.is_parent:
            return obj.children().count()
        return 0
