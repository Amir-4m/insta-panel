import uuid as uuid
from django.conf import settings
from django.db import models


class Page(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='pages')
    name = models.CharField(max_length=100)
    owner = models.CharField(max_length=100, blank=True)
    image = models.ImageField(null=True, blank=True)
    bio = models.CharField(max_length=250, blank=True)
    phone_number = models.CharField(max_length=11, blank=True)
    email = models.EmailField(null=True, blank=True)
    username = models.CharField(max_length=100, blank=False, null=False)
    password = models.CharField(max_length=100, blank=False, null=False)
    access_token = models.CharField(max_length=500, blank=True)
    refresh_token = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.name
