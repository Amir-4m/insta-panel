import time

from apps.insta_panel.api.api import API
from apps.post.models import Post, Story
from apps.page.services import PageServices

api = API()

CONFIGURE_TIMEOUT = 15


def login(page):
    try:
        password = PageServices.get_password(page, page.password)
        api.login(page.username, password, ask_for_code=True)
    except:
        raise Exception("login error")


def publish_photo(post):
    photo = post.postimage_set.first().file.path
    location = post.location
    location_data = None
    if location is not None:
        location_data = api.location_search(location.y, location.x).json().get('venues')[0]
        location_data.update({"address": location_data.get('name')})
    upload_id = api.upload_photo(photo, location=location_data)
    if upload_id:
        # CONFIGURE
        for attempt in range(4):
            if CONFIGURE_TIMEOUT:
                time.sleep(CONFIGURE_TIMEOUT)
            if api.configure_photo(upload_id, photo, post.caption, location=location_data):
                return True
    return False


def publish_video(post):
    location = post.location
    location_data = None
    if location is not None:
        location_data = api.location_search(location.y, location.x).json().get('venues')[0]
        location_data.update({"address": location_data.get('name')})

    video = post.postvideo_set.first().file.path
    upload_id, width, height, duration = api.upload_video(video, location=location_data)
    # CONFIGURE
    for attempt in range(4):
        if CONFIGURE_TIMEOUT:
            time.sleep(CONFIGURE_TIMEOUT)
        if api.configure_video(
                upload_id=upload_id,
                width=width,
                height=height,
                duration=duration,
                caption=post.caption,
                location=location_data
        ):
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
    if story.storyimage_set.count() == 1:
        path = story.storyimage_set.first().file.path
        upload = api.upload_story_photo
    elif story.storyvideo_set.count() == 1:
        path = story.storyvideo_set.first().file.path
        upload = api.upload_story_video
    else:
        return False

    for page in story.pages.all():
        login(page)
        if upload(path):
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
