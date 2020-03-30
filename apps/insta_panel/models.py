from django.conf.global_settings import AUTH_USER_MODEL
from django.db import models


class Page(models.Model):
    admins = models.ManyToManyField(AUTH_USER_MODEL)
    name = models.CharField(max_length=100)
    bio = models.CharField(max_length=250, null=True, blank=True)


class Post(models.Model):
    creator = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    pages = models.ManyToManyField(Page)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    image = models.ImageField()


class PostVideo(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    video = models.FileField()
