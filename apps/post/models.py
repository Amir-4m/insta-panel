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


class Story(models.Model):
    creator = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    pages = models.ManyToManyField(Page)

    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Stories"


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    file = models.ImageField(upload_to='posts/images')

    def __str__(self):
        return self.file.name


class PostVideo(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    file = models.FileField(upload_to='posts/videos')

    def __str__(self):
        return self.file.name


class StoryImage(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    file = models.ImageField(upload_to='stories/images')

    def __str__(self):
        return self.file.name


class StoryVideo(models.Model):
    post = models.ForeignKey(Story, on_delete=models.CASCADE)
    file = models.FileField(upload_to='stories/videos')

    def __str__(self):
        return self.file.name