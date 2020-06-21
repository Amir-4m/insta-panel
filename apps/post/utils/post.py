import time

from apps.insta_panel.api.api import API
from apps.post.models import Post, Story

api = API()

CONFIGURE_TIMEOUT = 15


def login(page):
    try:
        api.login(page.username, page.password, ask_for_code=True)
    except:
        raise Exception("login error")


def publish_photo(post):
    photo = post.postimage_set.first().file.path
    upload_id = api.upload_photo(photo)
    if upload_id:
        # CONFIGURE
        for attempt in range(4):
            if CONFIGURE_TIMEOUT:
                time.sleep(CONFIGURE_TIMEOUT)
            if api.configure_photo(upload_id, photo, post.caption):
                return True
    return False


def publish_video(post):
    video = post.postvideo_set.first().file.path
    upload_id, width, height, duration = api.upload_video(video, post.caption)
    # CONFIGURE
    for attempt in range(4):
        if CONFIGURE_TIMEOUT:
            time.sleep(CONFIGURE_TIMEOUT)
        if api.configure_video(
                upload_id=upload_id,
                width=width,
                height=height,
                duration=duration,
                caption=post.caption):
            media = api.last_json.get("media")
            api.expose()
            return media
    return False


def publish_album(post):
    images = post.postimage_set.all()
    videos = post.postvideo_set.all()
    media = []
    for image in images:
        media.append(
            {
                'type': 'photo',
                'file': image.file.path,  # Path to the photo file.
            }
        )

    for video in videos:
        media.append(
            {
                'type': 'video',
                'file': video.file.path,  # Path to the video file.
            }
        )

    if api.upload_album(media, post.caption):
        return True
    return False


def upload_story(story_id):
    story = Story.objects.get(id=story_id)
    image_path = story.storyimage_set.first().file.path
    for page in story.pages.all():
        login(page)
        if api.upload_story_photo(image_path):
            return True
        return False


def publish_post(post_id):
    post = Post.objects.get(id=post_id)

    if 1 < post.postimage_set.count() + post.postvideo_set.count() <= 10:
        upload = publish_album
    elif post.postimage_set.count() == 1:
        upload = publish_photo
    elif post.postvideo_set.count() == 1:
        upload = publish_video
    else:
        return False

    for page in post.pages.all():
        login(page)
        if not upload(post):
            raise Exception(f"error while posting on page {page.username}!")
