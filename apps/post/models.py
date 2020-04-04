from django.conf.global_settings import AUTH_USER_MODEL
from django.db import models

from apps.page.models import Page


class Post(models.Model):
    creator = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    pages = models.ManyToManyField(Page)
    caption = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.caption[:50]


class Photo(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='photos')


class Video(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    video = models.FileField()
