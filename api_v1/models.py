from django.db import models


class Post(models.Model):
    user = models.ForeignKey('auth.User', related_name='posts', on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True, default='')
    body = models.TextField(blank=False)
    likes_counter = models.IntegerField(blank=True, default=0)
    created = models.DateTimeField(auto_now_add=True)

