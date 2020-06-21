from django.contrib import admin

from apps.page.forms import PageForm
from .models import Page


class PageAdmin(admin.ModelAdmin):
    form = PageForm

    def get_queryset(self, request):
        qs = super(PageAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(admins=request.user)

    def has_view_or_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        else:
            if obj:
                if request.user.id not in obj.admins.all().values_list('id', flat=True):
                    return False
                return True
            return True

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        else:
            if obj and request.user.id not in obj.admins.all().values_list('id', flat=True):
                return False
            return True


admin.site.register(Page, PageAdmin)
