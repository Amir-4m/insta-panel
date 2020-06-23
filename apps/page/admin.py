from django.contrib import admin

from apps.page.forms import PageForm
from .models import Page
from .services import PageServices


class PageAdmin(admin.ModelAdmin):
    form = PageForm

    def save_model(self, request, obj, form, change):
        if 'password' in form.changed_data:
            password = str(PageServices.make_password(obj, obj.password))
            obj.password = password[1:].strip('\'')
        super(PageAdmin, self).save_model(request, obj, form, change)


admin.site.register(Page, PageAdmin)
