from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import reverse, path
from django.utils.html import format_html

from apps.page.models import Page
from apps.post.utils.post import publish_post, upload_story
from .models import Post, PostImage, PostVideo, Story, StoryImage, StoryVideo


class ImageInline(admin.TabularInline):
    model = PostImage
    extra = 1
    max_num = 10


class VideoInline(admin.TabularInline):
    model = PostVideo
    extra = 1
    max_num = 10


class PostAdmin(admin.ModelAdmin):
    list_display = [
        'caption',
        'creator',
        'page',
        'created_time',
        'updated_time',
        'post_actions',
    ]
    exclude = ["creator"]

    inlines = [
        ImageInline,
        VideoInline,
    ]

    def page(self, obj):
        return ', '.join(obj.pages.values_list('name', flat=True))

    page.short_description = 'pages'

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
        try:
            publish_post(post_id)
            messages.success(request, 'The post has been published on instagram page(s).')
        except Exception as e:
            messages.error(request, e)

        return redirect(f"admin:post_post_changelist")

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "pages":
            kwargs["queryset"] = Page.objects.filter(admins=request.user)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.creator = request.user
        super().save_model(request, obj, form, change)


class StoryImageInline(admin.TabularInline):
    model = StoryImage
    max_num = 1


class StoryVideoInline(admin.TabularInline):
    model = StoryVideo
    max_num = 1


class StoryAdmin(admin.ModelAdmin):
    list_display = [
        'creator',
        'page',
        'created_time',
        'updated_time',
        'post_actions',
    ]

    exclude = ["creator"]

    inlines = [
        StoryImageInline,
        StoryVideoInline,
    ]

    def page(self, obj):
        return ', '.join(obj.pages.values_list('name', flat=True))

    page.short_description = 'pages'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:story_id>/publish/', self.admin_site.admin_view(self.publish), name="story-publish"),
        ]
        return custom_urls + urls

    def post_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">Publish</a>',
            reverse('admin:story-publish', args=[obj.pk])
        )

    post_actions.short_description = 'Actions'
    post_actions.allow_tags = True

    def publish(self, request, story_id):
        upload_story(story_id)
        print("PUBLISH")
        return redirect(f"admin:post_story_changelist")

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "pages":
            kwargs["queryset"] = Page.objects.filter(admins=request.user)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.creator = request.user
        super().save_model(request, obj, form, change)


admin.site.register(Post, PostAdmin)
admin.site.register(Story, StoryAdmin)
