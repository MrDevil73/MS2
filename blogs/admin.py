from django.contrib import admin
from blogs.models import Blog,Post,Like,Comment,Subscription, User
# Register your models here.
admin.site.register(Blog)
admin.site.register(Post)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(Subscription)
#admin.site.register(User)