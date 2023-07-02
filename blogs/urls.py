from django.urls import path

from .views import BlogCreateView, BlogSubscriptionAPIView, BlogDetailAPIView, \
    MyBlogListAPIView, BlogSecondDetailView, BlogsNewListView
from .views import AuthorsView, LikePostAPIView, CommentCreateAPIView, CommentListAPIView, CommentDelete
from .views import PostListCreateAPIView, PostDetailAPIView, CreatePostAPIView, PostsListView, PostPublishAPIView
from .views import GeneralAPIView
from .views import UserPostsView, UserRegistrationView

urlpatterns = [
    path('blog/', BlogCreateView.as_view(), name='blog-create'),
    path('blogs/', BlogsNewListView.as_view(), name='blogs-list'),
    path('blogs/<int:blog_id>/', BlogDetailAPIView.as_view(), name='blog-detail'),
    path('blogs/<int:blog_id>/posts/', PostListCreateAPIView.as_view(), name='post-list-create'),
    path('blogs/<int:blog_id>/authors/', AuthorsView.as_view(), name='blog-authors'),  # Get post Delete
    path('myblogs/', MyBlogListAPIView.as_view(), name='blogs-user-list'),
    path('detailblog/<int:blog_id>/', BlogSecondDetailView.as_view(), name='blog-detail'),

    path('post/', CreatePostAPIView.as_view(), name='post-create'),

    path('posts/', PostsListView.as_view(), name='posts-list'),
    path('posts/<int:post_id>/', PostDetailAPIView.as_view(), name='post-detail'),
    path('posts/<int:post_id>/public/', PostPublishAPIView.as_view(), name='post-publish'),
    path('myposts/', UserPostsView.as_view(), name='get-user-posts'),

    path('posts/<int:pk>/comments/', CommentListAPIView.as_view(), name='comments-list'),
    path('posts/<int:pk>/comments/create/', CommentCreateAPIView.as_view(), name='create-comment'),
    path('posts/<int:post_id>/comments/<int:comment_id>/', CommentDelete.as_view(), name='delete-comment'),

    path('posts/<int:post_id>/like/', LikePostAPIView.as_view(), name='like-post'),

    path('subscriptions/', BlogSubscriptionAPIView.as_view(), name='blog-subscriptions'),
    path('subscriptions/<int:blog_id>/', BlogSubscriptionAPIView.as_view(), name='blog-subscription-detail'),

    path('register/', UserRegistrationView.as_view(), name='user_registration'),
    path('general/', GeneralAPIView.as_view(), name='main-page'),

]
