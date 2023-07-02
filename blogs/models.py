from django.db import models
from django.contrib.auth.models import User

from django.utils.timezone import now


class Blog(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(default=None, blank=True, null=True)
    authors = models.ManyToManyField(User, related_name='blogs_as_author')

    def __str__(self):
        return self.title


class Post(models.Model):
    title = models.TextField()
    body = models.TextField()
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    is_published = models.BooleanField(default=False)
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=None, blank=True, null=True)
    likes = models.ManyToManyField(User, through='Like', related_name='liked_posts')

    def save(self, *args, **kwargs):
        if self.is_published and self.created_at == None:
            self.created_at = now()
        elif self.is_published == False:
            self.created_at = None
        super().save(*args, **kwargs)

    def increase_views(self):
        self.views += 1
        self.save()

    def __str__(self):
        return f"Post {self.id} on Blog№{self.blog_id} by {self.author.username} " + ("(draft)" if not self.is_published else "")


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'post']  # Уникальность лайка пользователя на пост

    def __str__(self):
        return f"Like by {self.user.username} on {self.post.title}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} subscribed to {self.blog.title}"
