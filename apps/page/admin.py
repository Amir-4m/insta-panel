from django.contrib import admin

from apps.page.forms import PageForm
from .models import Page


class PageAdmin(admin.ModelAdmin):
    form = PageForm


admin.site.register(Page, PageAdmin)
