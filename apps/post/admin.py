from django.contrib import admin
from django.shortcuts import reverse
from .models import Post, Photo, Video
from apps.post.utils.post import upload_post


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 0


class VideoInline(admin.TabularInline):
    model = Video
    extra = 0


class PostAdmin(admin.ModelAdmin):
    list_display = [
        'caption',
        'creator',
        'page',
        'created_time',
        'updated_time',
    ]
    inlines = [
        PhotoInline,
        VideoInline,
    ]

    def page(self, obj):
        return ', '.join(obj.pages.values_list('name', flat=True))

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        upload_post(obj.pk)


class PhotoAdmin(admin.ModelAdmin):
    pass


class VideoAdmin(admin.ModelAdmin):
    pass


admin.site.register(Post, PostAdmin)
admin.site.register(Photo, PhotoAdmin)
admin.site.register(Video, VideoAdmin)
