from django.contrib import admin, messages
from django.contrib.gis.admin import OSMGeoAdmin
from django.utils import timezone
from django.shortcuts import redirect
from django.urls import reverse, path
from django.utils.html import format_html
from apps.page.models import Page
from .forms import PostAdminForm
from .utils.post import publish_post, upload_story
from .utils.post_admin import custom_change_delete_permission, custom_view_permission
from .models import Post, PostImage, PostVideo, Story, StoryImage, StoryVideo, InstagramAccount
from ..insta_panel.api.api import API
from .tasks import publish_post_async, publish_story_async

api = API()


@admin.register(InstagramAccount)
class InstagramAccountModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'is_enable')
    search_fields = ('username',)
    list_filter = ('is_enable',)
    readonly_fields = ('failed_login_attempt',)


class ImageInline(admin.TabularInline):
    model = PostImage
    extra = 1
    max_num = 10


class VideoInline(admin.TabularInline):
    model = PostVideo
    extra = 1
    max_num = 1


class PostAdmin(OSMGeoAdmin):
    class Media:
        js = (
            'http://code.jquery.com/jquery-1.9.1.min.js',
            "http://www.openlayers.org/api/OpenLayers.js",
            'post/admin/postadmin.js',

        )

    form = PostAdminForm
    add_form_template = 'post/add.html'
    list_display = [
        'caption',
        'creator',
        'page',
        'created_time',
        'updated_time',
        'post_actions',
    ]
    readonly_fields = ('publish_time',)

    exclude = ["creator", "is_crontab"]
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
        html = None
        if obj.publish_time is None and obj.is_crontab is False:
            html = format_html(
                '<a class="button" href="{}">Publish</a>',
                reverse('admin:post-publish', args=[obj.pk])
            )
        elif obj.is_crontab and obj.publish_time is None:
            html = format_html('<span>In publish queue</span>')
        elif obj.publish_time is not None:
            html = format_html('<span>Published</span>')
        return html

    post_actions.short_description = 'Actions'
    post_actions.allow_tags = True

    def publish(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
            if post.publish_on is not None:
                publish_time = post.publish_on - timezone.now()
                post.is_crontab = True
                post.save()
                if publish_time.total_seconds() <= 0:
                    return messages.error(request, 'publish schedule time is invalid !')
                publish_post_async.apply_async((post_id,), countdown=publish_time.total_seconds())
            else:
                if post.publish_time is None:
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
        location = form.data.get('places')
        for page in pages:
            if request.user not in page.admins.all():
                messages.set_level(request, messages.ERROR)
                return messages.error(request, f"you have no access to page {page.username}")
        obj.creator = request.user
        obj.location = location
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


# class StoryVideoInline(admin.TabularInline):
#     model = StoryVideo
#     max_num = 1


class StoryAdmin(admin.ModelAdmin):
    list_display = [
        'creator',
        'page',
        'created_time',
        'updated_time',
        'post_actions',
    ]
    readonly_fields = ('publish_time',)

    exclude = ["creator", "is_crontab"]

    inlines = [
        StoryImageInline,
        # StoryVideoInline,
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
        html = None

        if obj.publish_time is None and obj.is_crontab is False:
            html = format_html(
                '<a class="button" href="{}">Publish</a>',
                reverse('admin:story-publish', args=[obj.pk])
            )
        elif obj.is_crontab and obj.publish_time is None:
            html = format_html('<span>In publish queue</span>')
        elif obj.publish_time is not None:
            html = format_html('<span>Published</span>')
        return html

    post_actions.short_description = 'Actions'
    post_actions.allow_tags = True

    def publish(self, request, story_id):
        try:
            story = Story.objects.get(id=story_id)
            if story.publish_on is not None:
                publish_time = story.publish_on - timezone.now()
                story.is_crontab = True
                story.save()
                if publish_time.total_seconds() <= 0:
                    return messages.error(request, 'publish schedule time is invalid !')
                publish_story_async.apply_async((story_id,), countdown=publish_time.total_seconds())
            elif not story.publish_time and upload_story(story_id):
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
