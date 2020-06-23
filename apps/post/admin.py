from django.contrib import admin, messages
from django.utils import timezone
from django.shortcuts import redirect
from django.urls import reverse, path
from django.utils.html import format_html
from apps.page.models import Page
from .utils.post import publish_post, upload_story
from .utils.post_admin import custom_change_delete_permission, custom_view_permission
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
        if obj.publish_time is None:
            return format_html(
                '<a class="button" href="{}">Publish</a>',
                reverse('admin:post-publish', args=[obj.pk])
            )

    post_actions.short_description = 'Actions'
    post_actions.allow_tags = True

    def publish(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
            if not post.publish_time:
                publish_post(post_id)
                messages.success(request, 'The post has been published on instagram page(s).')
                Post.objects.filter(id=post_id).update(publish_time=timezone.now())
            else:
                messages.error(request, 'this post has been published already !')
        except Exception as e:
            messages.error(request, e)

        return redirect(f"admin:post_post_changelist")

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "pages":
            kwargs["queryset"] = Page.objects.filter(admins=request.user)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        pages = form.cleaned_data.get('pages')
        for page in pages:
            if request.user not in page.admins.all():
                messages.set_level(request, messages.ERROR)
                return messages.error(request, f"you have no access to page {page.username}")
        obj.creator = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super(PostAdmin, self).get_queryset(request)
        user = request.user
        if user.is_superuser:
            return qs
        return qs.filter(pages__admins=request.user)

    def has_view_permission(self, request, obj=None):
        return custom_view_permission(request.user, obj)

    def has_change_permission(self, request, obj=None):
        user = request.user
        return custom_change_delete_permission(user, obj)

    def has_delete_permission(self, request, obj=None):
        user = request.user
        return custom_change_delete_permission(user, obj)


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
        if obj.publish_time is None:
            return format_html(
                '<a class="button" href="{}">Publish</a>',
                reverse('admin:story-publish', args=[obj.pk])
            )

    post_actions.short_description = 'Actions'
    post_actions.allow_tags = True

    def publish(self, request, story_id):
        try:
            story = Story.objects.get(id=story_id)
            if not story.publish_time and upload_story(story_id):
                messages.success(request, 'The story has been published on instagram page(s).')
                Story.objects.filter(id=story_id).update(publish_time=timezone.now())
            else:
                messages.error(request, 'error occurred !')
        except Exception as e:
            messages.error(request, e)
        return redirect(f"admin:post_story_changelist")

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "pages":
            kwargs["queryset"] = Page.objects.filter(admins=request.user)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        pages = form.cleaned_data.get('pages')
        for page in pages:
            if request.user not in page.admins.all():
                messages.set_level(request, messages.ERROR)
                return messages.error(request, f"you have no access to page {page.username}")
        obj.creator = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super(StoryAdmin, self).get_queryset(request)
        user = request.user
        if user.is_superuser:
            return qs
        return qs.filter(pages__admins=request.user)

    def has_view_permission(self, request, obj=None):
        return custom_view_permission(request.user, obj)

    def has_change_permission(self, request, obj=None):
        user = request.user
        return custom_change_delete_permission(user, obj)

    def has_delete_permission(self, request, obj=None):
        user = request.user
        return custom_change_delete_permission(user, obj)


admin.site.register(Post, PostAdmin)
admin.site.register(Story, StoryAdmin)
