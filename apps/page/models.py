from django.conf.global_settings import AUTH_USER_MODEL
from django.db import models


class Page(models.Model):
    admins = models.ManyToManyField(AUTH_USER_MODEL)
    name = models.CharField(max_length=100)
    image = models.ImageField(null=True, blank=True)
    bio = models.CharField(max_length=250, blank=True)
    owner = models.CharField(max_length=100, blank=True)
    owner_phone_number = models.CharField(max_length=11, blank=True)
