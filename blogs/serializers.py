from rest_framework import serializers
from .models import Blog, Post, Comment, Subscription
from django.contrib.auth.models import User


class BlogSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)  # Добавление поля "id" только для чтения
    owner = serializers.IntegerField(required=False)

    class Meta:
        model = Blog
        fields = ('id', 'created_at', 'title', 'description', 'owner')

    def create(self, validated_data):
        validated_data['owner'] = self.context['owner']  # Установка текущего пользователя в качестве автора
        blog = super().create(validated_data)

        return blog

    def validate(self, attrs):
        # Добавьте свою проверку данных здесь
        title = attrs.get('title')

        if not title:
            raise serializers.ValidationError("Поле title обязательно для заполнения.")
        return attrs

    def to_representation(self, instance):
        representation = {
            'id': instance.id
        }
        return representation


class BlogViewSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    authors = serializers.SerializerMethodField()

    def get_owner(self, obj):
        return obj.owner.username

    def get_authors(self, obj):
        return [author.username for author in obj.authors.all()]

    class Meta:
        model = Blog
        fields = ('id', 'owner', 'title', 'description', 'created_at', 'updated_at', 'authors')


class SubscriptionSerializer(serializers.ModelSerializer):
    blog_id = serializers.IntegerField(source='blog.id', read_only=True)
    blog_title = serializers.CharField(source='blog.title', read_only=True)
    author_username = serializers.CharField(source='blog.owner.username', read_only=True)

    class Meta:
        model = Subscription
        fields = ('blog_id', 'blog_title', 'author_username')


class CommentSerializer(serializers.ModelSerializer):
    post = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'body', 'created_at', 'post')


class CommentListSer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    def get_author(self, obj):
        return obj.author.username

    class Meta:
        model = Comment
        fields = ('id', 'body', 'created_at', 'author', 'post_id')


class PostViewSerializer(serializers.ModelSerializer):
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    author = serializers.SerializerMethodField()

    def get_author(self, obj):
        return obj.author.username

    class Meta:
        model = Post
        fields = ('id', 'title', 'body', 'blog', 'author', 'is_published', 'views', 'likes_count')


class PostSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True, required=False)
    views = serializers.DateTimeField(read_only=True, required=False)
    likes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'title', 'body', 'blog', 'author', 'is_published', 'likes', 'views', 'created_at', 'comments')

    def create(self, validated_data):
        validated_data['author'] = self.context['author']  # Установка текущего пользователя в качестве автора

        post = super().create(validated_data)
        # post = Post.objects.create(**validated_data)
        return post


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user


class UserViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']


class CommentSecondSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    def get_author(self, obj):
        return obj.author.username

    class Meta:
        model = Comment
        fields = ['id', 'author', 'body', 'created_at']


class PostSecondSerializer(serializers.ModelSerializer):
    comments = CommentSecondSerializer(many=True)
    author = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)

    def get_author(self, obj):
        return obj.author.username

    class Meta:
        model = Post
        fields = ['id', 'title', 'body', 'is_published', 'likes_count', 'author', 'created_at', 'comments']


class BlogSecondSerializer(serializers.ModelSerializer):
    posts = PostSecondSerializer(many=True)
    owner = serializers.SerializerMethodField()
    authors = serializers.SerializerMethodField()

    def get_owner(self, obj):
        return obj.owner.username

    def get_authors(self, obj):
        return [author.username for author in obj.authors.all()]

    class Meta:
        model = Blog
        fields = ['id', 'owner', 'title', 'description', 'owner', 'created_at', 'updated_at', 'authors', 'posts']


class BlogsGeneralSerializer(serializers.ModelSerializer):
    posts = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

    def get_owner(self, obj):
        return obj.owner.username

    class Meta:
        model = Blog
        fields = ['id', 'title', 'owner', 'description', 'updated_at', 'created_at', 'posts']

    def get_posts(self, blog):
        N = self.context.get("N")
        # print()
        posts = Post.objects.filter(is_published=True, blog=blog)[:N]  # Ограничиваем количество постов для примера
        post_serializer = PostSecondSerializer(posts, many=True)
        return post_serializer.data
