import datetime

from .models import Blog, Post, Comment, Like, Subscription
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Count

from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import permissions, status, serializers
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, RetrieveDestroyAPIView, \
    CreateAPIView, DestroyAPIView, UpdateAPIView
from rest_framework.pagination import PageNumberPagination


class MyPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 10


from .serializers import BlogSerializer, UserSerializer, PostSerializer, \
    CommentSerializer, CommentListSer, UserViewSerializer, \
    SubscriptionSerializer, PostViewSerializer, BlogViewSerializer, BlogSecondSerializer, \
    BlogsGeneralSerializer, PostSecondSerializer


class BlogCreateView(CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = BlogSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['owner'] = self.request.user
        return context

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CreatePostAPIView(CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['author'] = self.request.user
        return context

    def perform_create(self, serializer):
        is_published = self.request.data.get('is_published')
        if is_published and is_published.lower() == 'true':
            post = serializer.save()
            blog = post.blog
            blog.updated_at = timezone.now()
            blog.save()
        else:
            serializer.save(created_at=None)

    def create(self, request, *args, **kwargs):
        if "blog" not in request.data.keys():
            return Response({'error': 'No blog'}, status=status.HTTP_403_FORBIDDEN)
        blog_id = request.data.get('blog')
        try:
            blog = Blog.objects.get(id=blog_id)
        except:
            return Response({'error': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)
        user = request.user
        if user == blog.owner or user in blog.authors.all():
            return super().create(request, *args, **kwargs)
        else:
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)


class PostDeleteAPIView(DestroyAPIView):
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        user = request.user
        if post.author == user or post.blog.owner == user:
            return self.destroy(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

class CommentDelete(APIView):

    def delete(self, request, post_id,comment_id):
        try:
            comment = Comment.objects.get(id=comment_id,post_id=post_id)
        except Comment.DoesNotExist:
            return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
        if request.user != comment.author:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        comment.delete()
        return Response({'message': 'Comment deleted'}, status=status.HTTP_200_OK)


class CommentListAPIView(ListAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentListSer

    def get_queryset(self):
        post_id = self.kwargs['pk']
        return Comment.objects.filter(post_id=post_id)


class CommentCreateAPIView(CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        post_id = self.kwargs['pk']  # Получаем идентификатор поста из URL
        serializer.save(post_id=post_id, author=self.request.user)
        # serializer.save()


class CommentDetailAPIView(DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        comment_id = self.kwargs['pk_comment']
        comment = Comment.objects.filter(id=comment_id, author=self.request.user).first()
        if not comment:
            raise serializers.ValidationError("Comment not found or you are not the author")
        return comment


class AuthorsView(APIView):
    def get(self, request, blog_id):
        try:
            blog = Blog.objects.get(id=blog_id)
        except Blog.DoesNotExist:
            return Response({'error': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)
        if blog.owner != request.user:
            return Response({'error': 'Only the blog owner can see authors'}, status=status.HTTP_403_FORBIDDEN)
        authors = blog.authors.all()
        serializer = UserViewSerializer(authors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, blog_id):
        try:
            blog = Blog.objects.get(id=blog_id)
        except Blog.DoesNotExist:
            return Response({'error': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)
        if blog.owner != request.user:
            return Response({'error': 'Only the blog owner can add authors'}, status=status.HTTP_403_FORBIDDEN)
        author_names = request.data.get('author_names')
        if not author_names:
            return Response({'error': 'No parameter author_names'}, status=status.HTTP_400_BAD_REQUEST)
        authors = User.objects.exclude(username=blog.owner).filter(username__in=author_names.split(','))
        if not authors:
            return Response({'error': 'No find author names'}, status=status.HTTP_400_BAD_REQUEST)
        blog.authors.add(*authors)
        authors = blog.authors.all()
        serializer = UserViewSerializer(authors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, blog_id):
        try:
            blog = Blog.objects.get(id=blog_id)
        except Blog.DoesNotExist:
            return Response({'error': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)
        if blog.owner != request.user:
            return Response({'error': 'Only the blog owner can remove authors'}, status=status.HTTP_403_FORBIDDEN)
        author_names = request.data.get('author_names')
        if not author_names:
            return Response({'error': 'No parameter author_names'}, status=status.HTTP_400_BAD_REQUEST)
        authors = User.objects.filter(username__in=author_names.split(','))
        if not authors:
            return Response({'error': 'No find author names'}, status=status.HTTP_400_BAD_REQUEST)
        blog.authors.remove(*authors)
        authors = blog.authors.all()
        serializer = UserViewSerializer(authors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LikePostAPIView(APIView):
    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        if Like.objects.filter(user=request.user, post=post).exists():
            return Response({'error': 'User has already liked this post'}, status=status.HTTP_400_BAD_REQUEST)
        like = Like(user=request.user, post=post)
        like.save()
        return Response({'message': 'Post liked successfully'}, status=status.HTTP_201_CREATED)

    def delete(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            like = Like.objects.get(user=request.user, post=post)
        except Like.DoesNotExist:
            return Response({'error': 'User has not liked this post'}, status=status.HTTP_400_BAD_REQUEST)
        like.delete()
        return Response({'message': 'Post unliked successfully'}, status=status.HTTP_200_OK)


class BlogSubscriptionAPIView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'User not authorized'}, status=status.HTTP_401_UNAUTHORIZED)
        subscriptions = Subscription.objects.filter(user=request.user)
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, blog_id=None):
        if not blog_id:
            return Response({'error': 'Blog_id not found'}, status=status.HTTP_404_NOT_FOUND)
        if not request.user:
            return Response({'error': 'User not authorized'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            blog = Blog.objects.get(id=blog_id)
        except Blog.DoesNotExist:
            return Response({'error': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)
        if Subscription.objects.filter(user=request.user, blog=blog).exists():
            return Response({'error': 'Already subscribed to this blog'}, status=status.HTTP_400_BAD_REQUEST)
        subscription = Subscription(user=request.user, blog=blog)
        subscription.save()
        return Response({'status': 'ok'}, status=status.HTTP_201_CREATED)

    def delete(self, request, blog_id):
        try:
            blog = Blog.objects.get(id=blog_id)
        except Blog.DoesNotExist:
            return Response({'error': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)
        Subscription.objects.filter(user=request.user, blog=blog).delete()
        return Response({'status': 'Unsubscribed'}, status=status.HTTP_204_NO_CONTENT)


class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostPublishAPIView(UpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def update(self, request, *args, **kwargs):
        post_id = self.kwargs['post_id']
        post = get_object_or_404(Post, id=post_id, is_published=False)
        if post.author != request.user:  # and request.user.is_superuser == False:
            return Response({'error': 'Nice try'}, status=status.HTTP_403_FORBIDDEN)
        post.is_published = True
        post.save()
        blog = post.blog
        blog.updated_at = post.created_at
        blog.save()
        return Response({'detail': 'Post published successfully.'})


class MyBlogListAPIView(ListAPIView):
    serializer_class = BlogViewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Blog.objects.filter(owner=user)


class BlogDetailAPIView(RetrieveDestroyAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogViewSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'blog_id'

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        if instance.owner == user:
            self.perform_destroy(instance)
            return Response({'status': 'Deleted'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': "Access denied"}, status=status.HTTP_403_FORBIDDEN)


class PostListCreateAPIView(APIView):
    def get(self, request, blog_id):
        try:
            blog_ = Blog.objects.get(id=blog_id)
        except Blog.DoesNotExist:
            return Response({'error': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)
        posts = Post.objects.filter(blog=blog_)
        for post in posts:
            post.increase_views()
        serializer = PostViewSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PostDetailAPIView(RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostViewSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'post_id'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.increase_views()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        if instance.author == user or instance.blog.owner == user:
            self.perform_destroy(instance)
            return Response({'status': 'Deleted'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': "Access denied"}, status=status.HTTP_403_FORBIDDEN)

    def perform_destroy(self, instance):
        instance.delete()


class BlogSecondDetailView(APIView):
    def get(self, request, blog_id):
        blog = Blog.objects.get(pk=blog_id)
        serializer = BlogSecondSerializer(blog)
        return Response(serializer.data)


class GeneralAPIView(APIView):
    def get(self, request):
        N = request.query_params.get('N', 5)
        blogs = Blog.objects.all()
        serializer = BlogsGeneralSerializer(blogs, many=True, context={'N': int(N)})
        return Response(serializer.data)


class UserPostsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        posts = Post.objects.filter(author=user).order_by("-created_at")
        serializer = PostSecondSerializer(posts, many=True)
        return Response(serializer.data)


class BlogsNewListView(APIView):
    pagination_class = MyPagination

    def get(self, request):
        start_date = request.query_params.get('start_date', datetime.datetime(1970, 1, 1, tzinfo=timezone.utc))
        end_date = request.query_params.get('end_date', datetime.datetime.now(tz=timezone.utc))
        kw = {'created_at__range': [start_date, end_date]}
        author = request.query_params.get('author')
        title = request.query_params.get('title')
        if title:
            kw['title__icontains'] = title
        if author:
            kw['owner__username__icontains'] = author
        blogs = Blog.objects.filter(**kw)
        order_by = request.GET.get('order_by', 'title')
        if order_by.lower() in ['title', '-title', 'created_at', '-created_at']:
            blogs = blogs.order_by(order_by.lower())
        elif order_by.lower() in ['likes_count', '-likes_count']:
            blogs = blogs.annotate(likes_count=Count('posts__likes')).order_by(order_by.lower())
        elif order_by.lower() in ['relev', '-relev']:
            blogs = blogs.annotate(
                relev=Count('posts__likes') * 2 + Count('posts__views') + Count('posts__comments') * 3
            ).order_by(order_by.lower())
        paginator = self.pagination_class()
        paginated_blogs = paginator.paginate_queryset(blogs, request)
        serializer = BlogViewSerializer(paginated_blogs, many=True)

        return paginator.get_paginated_response(serializer.data)


class PostsListView(APIView):
    pagination_class = MyPagination

    def get(self, request):
        start_date = request.query_params.get('start_date', datetime.datetime(1970, 1, 1, tzinfo=timezone.utc))
        end_date = request.query_params.get('end_date', datetime.datetime.now(tz=timezone.utc))
        kw = {'is_published': True}
        author = request.query_params.get('author')
        title = request.query_params.get('title')
        if title:
            kw['title__icontains'] = title
        if author:
            kw['author__username__icontains'] = author
        posts = Post.objects.filter(**kw)
        order_by = request.GET.get('order_by', 'title')

        if order_by.lower() in ['title', '-title', 'created_at', '-created_at']:
            posts = posts.order_by(order_by.lower())
        elif order_by.lower() in ['likes_count', '-likes_count']:
            posts = posts.annotate(likes_count=Count('posts__likes')).order_by(order_by.lower())
        elif order_by.lower() in ['relev', '-relev']:
            posts = posts.annotate(
                relev=Count('likes') * 2 + Count('views') + Count('comments') * 3
            ).order_by(order_by.lower())
        paginator = self.pagination_class()
        paginated_posts = paginator.paginate_queryset(posts, request)
        for post in paginated_posts:
            post.increase_views()
        serializer = PostViewSerializer(paginated_posts, many=True)
        return paginator.get_paginated_response(serializer.data)
