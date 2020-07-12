from __future__ import unicode_literals

import json
import os
import shutil
import time
from random import randint
from uuid import uuid4

from requests_toolbelt import MultipartEncoder

from . import config
from .api_photo import get_image_size, stories_shaper
from .api_video import resize_video


def download_story(self, filename, story_url, username):
    path = "stories/{}".format(username)
    if not os.path.exists(path):
        os.makedirs(path)
    fname = os.path.join(path, filename)
    if os.path.exists(fname):  # already exists
        self.logger.info("Stories already downloaded...")
        return os.path.abspath(fname)
    response = self.session.get(story_url, stream=True)
    if response.status_code == 200:
        with open(fname, "wb") as f:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)
        return os.path.abspath(fname)


def upload_story_video(self, video, upload_id=None, thumbnail=None, is_sidecar=None, options={}):
    options = dict(
        {"configure_timeout": 15, "rename_thumbnail": True, "rename": True},
        **(options or {})
    )
    video, thumbnail, width, height, duration = resize_video(video, thumbnail)

    if upload_id is None:
        upload_id = str(int(time.time() * 1000))

    if not video:
        return False

    waterfall_id = str(uuid4())
    # upload_name example: '1576102477530_0_7823256191'
    upload_name = "{upload_id}_0_{rand}".format(
        upload_id=upload_id, rand=randint(1000000000, 9999999999)
    )
    rupload_params = {
        'retry_context': {
            'num_step_auto_retry': 0, 'num_reupload': 0, 'num_step_manual_retry': 0
        },
        "media_type": 2,
        "xsharing_user_ids": "[]",
        "upload_id": upload_id,
        "upload_media_duration_ms": int(duration * 1000),
        "upload_media_width": width,
        "upload_media_height": height,

    }
    if is_sidecar:
        rupload_params["is_sidecar"] = '1'

    self.session.headers.update(
        {
            "Accept-Encoding": "gzip",
            "X-Instagram-Rupload-Params": json.dumps(rupload_params),
            "X_FB_VIDEO_WATERFALL_ID": waterfall_id,
            "X-Entity-Type": "video/mp4",
        }
    )
    response = self.session.get(
        "https://{domain}/rupload_igvideo/{name}".format(
            domain=config.API_DOMAIN, name=upload_name
        ),
    )
    if response.status_code != 200:
        return False

    video_data = open(video, "rb").read()
    video_len = str(len(video_data))
    self.session.headers.update(
        {
            "Offset": "0",
            "X-Entity-Name": "fb_uploader_" + upload_id,
            "X-Entity-Length": video_len,
            "Content-Type": "application/octet-stream",
            "Content-Length": video_len,
        }
    )
    try:
        response = self.session.post(
            "https://{domain}/rupload_igvideo/{name}".format(
                domain=config.API_DOMAIN, name=upload_name
            ),
            data=video_data,
        )
    except Exception as e:
        print(e)

    if response.status_code != 200:
        return False

    upload_id = json.loads(response.text).get("upload_id")
    if self.configure_story(upload_id, video):
        # self.expose()
        return True

    return False


def upload_story_photo(self, photo, upload_id=None):
    if upload_id is None:
        upload_id = str(int(time.time() * 1000))
    if not photo:
        return False
    photo = stories_shaper(photo)
    if not photo:
        return False
    waterfall_id = str(uuid4())
    # upload_name example: '1576102477530_0_7823256191'
    upload_name = "{upload_id}_0_{rand}".format(
        upload_id=upload_id, rand=randint(1000000000, 9999999999)
    )
    rupload_params = {
        "retry_context": '{"num_step_auto_retry":0,"num_reupload":0,"num_step_manual_retry":0}',
        "media_type": "1",
        "xsharing_user_ids": "[]",
        "upload_id": upload_id,
        "image_compression": json.dumps(
            {"lib_name": "moz", "lib_version": "3.1.m", "quality": "80"}
        ),
    }
    photo_data = open(photo, "rb").read()
    photo_len = str(len(photo_data))
    self.session.headers.update(
        {
            "Accept-Encoding": "gzip",
            "X-Instagram-Rupload-Params": json.dumps(rupload_params),
            "X_FB_PHOTO_WATERFALL_ID": waterfall_id,
            "X-Entity-Type": "image/jpeg",
            "Offset": "0",
            "X-Entity-Name": upload_name,
            "X-Entity-Length": photo_len,
            "Content-Type": "application/octet-stream",
            "Content-Length": photo_len,
            "Accept-Encoding": "gzip",
        }
    )
    response = self.session.post(
        "https://{domain}/rupload_igphoto/{name}".format(
            domain=config.API_DOMAIN, name=upload_name
        ),
        data=photo_data,
    )

    # response = self.session.post(config.API_URL + "upload/photo/", data=m.to_string())

    if response.status_code == 200:
        upload_id = json.loads(response.text).get("upload_id")
        if self.configure_story(upload_id, photo):
            # self.expose()
            return True
    return False


def configure_story(self, upload_id, photo):
    (w, h) = get_image_size(photo)
    data = self.json_data(
        {
            "source_type": 4,
            "upload_id": upload_id,
            "story_media_creation_date": str(int(time.time()) - randint(11, 20)),
            "client_shared_at": str(int(time.time()) - randint(3, 10)),
            "client_timestamp": str(int(time.time())),
            "configure_mode": 1,  # 1 - REEL_SHARE, 2 - DIRECT_STORY_SHARE
            "device": self.device_settings,
            "edits": {
                "crop_original_size": [w * 1.0, h * 1.0],
                "crop_center": [0.0, 0.0],
                "crop_zoom": 1.3333334,
            },
            "extra": {"source_width": w, "source_height": h},
        }
    )
    return self.send_request("media/configure_to_story/?", data)


def configure_story_video(self, upload_id, width, height, duration):
    """Post Configure Video (send caption, thumbnail and more to Instagram)

    @param upload_id  Unique upload_id (String). Received from "upload_video"
    @param width      Width in px (Integer)
    @param height     Height in px (Integer)
    @param duration   Duration in seconds (Integer)
    @param caption    Media description (String)
    @param options    Object with difference options, e.g. configure_timeout,
                      rename_thumbnail, rename (Dict)
                      Designed to reduce the number of function arguments!
                      This is the simplest request object.
    """
    params = self.json_data(
        {
            'source_type': '4',
            'upload_id': upload_id,
            'story_media_creation_date': str(int(time.time()) - randint(11, 20)),
            'client_shared_at': str(int(time.time()) - randint(3, 10)),
            'client_timestamp': str(int(time.time())),
            'configure_mode': 1,  # 1 - REEL_SHARE, 2 - DIRECT_STORY_SHARE
            'device': {
                'manufacturer': self.phone_manufacturer,
                'model': self.phone_device,
                'android_version': self.android_version,
                'android_release': self.android_release
            },
            'edits': {
                'crop_original_size': [width * 1.0, height * 1.0],
                'crop_center': [0.0, 0.0],
                'crop_zoom': 1.3333334
            },
            'extra': {
                'source_width': width,
                'source_height': height,
            }
        }
    )
    self.send_request("media/configure_to_story/", params)

    data = self.json_data(
        {
            "source_type": '4',
            "upload_id": upload_id,
            "story_media_creation_date": str(int(time.time()) - randint(11, 20)),
            "client_shared_at": str(int(time.time()) - randint(3, 10)),
            "client_timestamp": str(int(time.time())),
            "configure_mode": 1,  # 1 - REEL_SHARE, 2 - DIRECT_STORY_SHARE
            'poster_frame_index': 0,
            "device": self.device_settings,
            'length': duration * 1.0,
            "audio_muted": False,
            'video_result': 'deprecated',
            "filter_type": 0,
            "width": width,
            "height": height,
            'clips': {
                'length': duration * 1.0,
                'source_type': '4',
                'camera_position': 'back'
            },
            "extra": {"source_width": width, "source_height": height},
        }
    )

    return self.send_request("media/configure_to_story/?video=1", data)
