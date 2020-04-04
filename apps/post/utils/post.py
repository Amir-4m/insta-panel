from apps.page.models import Page
from apps.post.models import Post
from apps.post.utils.instagram import Instagram


def upload_photo(post, page):
    bot = Instagram(page.username, page.password)
    photo_path = post.photo_set.all()[0].photo.path
    bot.upload_photo(photo_path, post.caption)


def upload_video(post, page):
    bot = Instagram(page.username, page.password)
    bot.upload_video(post.video_set.first, post.caption)


def upload_album(post, page):
    bot = Instagram(page.username, page.password)
    bot.upload_album(post.photo_set.all(), post.video_set.all(), post.caption)


def upload_post(pk):
    post = Post.objects.get(pk=pk)
    upload = None
    if post.photo_set.count() + post.video_set.count() > 1:
        upload = upload_album
    elif post.photo_set.count() == 1:
        upload = upload_photo
    elif post.video_set.count() == 1:
        upload = upload_video

    for page in post.pages.all():
        upload(post, page)
