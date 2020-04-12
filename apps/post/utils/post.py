from apps.insta_panel.api.api import API
from apps.post.models import Post

api = API()


def login(page):
    api.login(page.username, page.password)
    if api.is_logged_in:
        return True
    return False


def upload_photo(post):
    image_path = post.image_set.first().file.path
    api.upload_photo(image_path, post.caption)


def upload_video(post):
    api = API()
    api.upload_video(post.video_set.first, post.caption)


def upload_album(post):
    images = post.image_set.all()
    videos = post.video_set.all()
    media = []
    for image in images:
        media.append(
            {
                'type': 'photo',
                'file': image.file.path,  # Path to the photo file.
            }
        )

    api.upload_album(media, post.caption)


def upload_post(post_id):
    post = Post.objects.get(id=post_id)
    upload = None
    if post.image_set.count() + post.video_set.count() > 1:
        upload = upload_album
    elif post.image_set.count() == 1:
        upload = upload_photo
    elif post.video_set.count() == 1:
        upload = upload_video

    for page in post.pages.all():
        if login(page):
            upload(post)
