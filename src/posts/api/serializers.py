from rest_framework.fields import ImageField
from rest_framework.serializers import ModelSerializer, HyperlinkedIdentityField, SerializerMethodField
from posts.models import Post
from comments.api.serializers import CommentListSerializer
from accounts.api.serializers import UserDetailSerializer
from comments.models import Comment


class PostListSerializer(ModelSerializer):
    detail_url = HyperlinkedIdentityField(
        view_name='posts-api:detail',
        lookup_field='slug'
    )
    user = UserDetailSerializer(read_only=True)
    image = ImageField(max_length=None, use_url=True)

    class Meta:
        model = Post
        fields = [
            'id',
            'detail_url',
            'user',
            'title',
            'content',
            'image',
            'publish',
        ]


class PostDetailSerializer(ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    image = ImageField(max_length=None, use_url=True)
    html = SerializerMethodField()
    comments = SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id',
            'user',
            'title',
            'slug',
            'content',
            'html',
            'image',
            'comments',
            'publish',
        ]
        read_only_fields = [
            "slug",  # SerializerMethodFields() are automatically read_only
        ]

    def get_html(self, obj):
        return obj.get_markdown()

    def get_comments(self, obj):
        comments_queryset = Comment.objects.filter_by_instance(obj)
        serializer_context = {'request': self.context['request']}
        comments = CommentListSerializer(comments_queryset, many=True, context=serializer_context).data
        return comments
