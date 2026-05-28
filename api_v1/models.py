from django.conf import settings
from django.db import models


class Post(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='posts', on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200, blank=True, default='')
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='likes', on_delete=models.CASCADE
    )
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name='unique_user_post_like'),
        ]
