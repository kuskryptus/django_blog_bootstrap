from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import truncatechars
from ckeditor.fields import RichTextField


class Post(models.Model):
    title = models.CharField(max_length=250)
    published_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    body = RichTextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, blank=True, related_name='likes')
    image = models.ImageField(upload_to='post_images/')

    class Meta:
        ordering = ['-published_date']
        get_latest_by = 'published_date'

    def __str__(self):
        return self.title

    def count_likes(self):
        return self.likes.count()
    
    @property
    def truncated_body(self):
        return truncatechars(self.body, 400)


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE, related_name='children')
    created_date = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, blank=True, related_name='comment_likes')

    def __str__(self):
        return f'Comment by {self.user.username}: {self.content[:50]}...'

    def count_likes(self):
        return self.likes.count()
