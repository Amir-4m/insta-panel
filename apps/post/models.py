from django.conf.global_settings import AUTH_USER_MODEL
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from django.contrib.gis.db.models import PointField
from django.contrib.postgres.fields import JSONField
from django.utils.translation import ugettext_lazy as _

from django.db import models

from apps.insta_panel.api.api import API
from apps.page.models import Page

api = API()


class ChoiceField(models.CharField):
    def validate(self, value, model_instance):
        pass

    def run_validators(self, value):
        pass


class InstagramAccount(models.Model):
    username = models.CharField(_('username'), max_length=120, null=False, blank=False)
    password = models.CharField(_('password'), max_length=256, null=False, blank=False)
    is_enable = models.BooleanField(_("is enable"), default=True)
    created_time = models.DateTimeField(_("created time"), auto_now_add=True)
    updated_time = models.DateTimeField(_("updated time"), auto_now=True)
    failed_login_attempt = models.IntegerField(_("failed login attempt"), default=0)


class Post(models.Model):
    creator = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    pages = models.ManyToManyField(Page)
    caption = models.TextField(blank=True, max_length=2048)
    point = PointField(null=True, blank=True)
    location = JSONField(editable=False, null=True)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    publish_time = models.DateTimeField(null=True, blank=True, db_index=True)
    publish_on = models.DateTimeField(null=True, blank=True)
    is_crontab = models.BooleanField(default=False)

    def __str__(self):
        return self.caption[:50]


class Story(models.Model):
    creator = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    pages = models.ManyToManyField(Page)
    publish_time = models.DateTimeField(null=True, blank=True, db_index=True)
    publish_on = models.DateTimeField(null=True, blank=True)
    is_crontab = models.BooleanField(default=False)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Stories"


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    file = models.ImageField(upload_to='posts/images')

    def __str__(self):
        return self.file.name

    def clean(self):
        w, h = get_image_dimensions(self.file)
        if w > 1080 or w < 480:
            raise ValidationError(_("width should be between 1080 and 480"))


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
