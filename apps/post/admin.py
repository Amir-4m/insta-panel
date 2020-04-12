from django.contrib import admin
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse, path
from django.utils.html import format_html

from apps.page.models import Page
from apps.post.utils.post import upload_post
from .models import Post, Image, Video


class ImageInline(admin.StackedInline):
    model = Image
    extra = 1


class VideoInline(admin.TabularInline):
    model = Video
    extra = 1


class PostAdmin(admin.ModelAdmin):
    list_display = [
        'caption',
        'creator',
        'page',
        'created_time',
        'updated_time',
        'post_actions',
    ]
    exclude = ("creator",)

    inlines = [
        ImageInline,
        VideoInline,
    ]

    def page(self, obj):
        return ', '.join(obj.pages.values_list('name', flat=True))

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:post_id>/publish/', self.admin_site.admin_view(self.publish), name="post-publish"),
        ]
        return custom_urls + urls

    def post_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">Publish</a>',
            reverse('admin:post-publish', args=[obj.pk])
        )

    post_actions.short_description = 'Actions'
    post_actions.allow_tags = True

    def publish(self, request, post_id):
        upload_post(post_id)
        print("PUBLISH")
        return redirect(f"admin:post_post_changelist")

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "pages":
            kwargs["queryset"] = Page.objects.filter(admins=request.user)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.creator = request.user
        super().save_model(request, obj, form, change)


class ImageAdmin(admin.ModelAdmin):
    pass


class VideoAdmin(admin.ModelAdmin):
    pass


admin.site.register(Post, PostAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Video, VideoAdmin)
