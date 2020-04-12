import json
import calendar
import time
from datetime import datetime

from .api_photo import upload_photo


def upload_album(self, media, caption=None, upload_id=None, options={}):
    if not media:
        raise Exception("List of media to upload can't be empty.")

    if len(media) < 2 or len(media) > 10:
        raise Exception('Instagram requires that albums contain 2-10 items. You tried to submit {}.'.format(len(media)))

    # Figure out the media file details for ALL media in the album.
    # NOTE: We do this first, since it validates whether the media files are
    # valid and lets us avoid wasting time uploading totally invalid albums!
    for idx, item in enumerate(media):
        if not item.get('file', '') or item.get('tipe', ''):
            raise Exception('Media at index "{}" does not have the required "file" and "type" keys.'.format(idx))

        # $itemInternalMetadata = new InternalMetadata();
        # If usertags are provided, verify that the entries are valid.

        # if item.get('usertags', []):
        #     self.throwIfInvalidUsertags(item['usertags'])

        # Pre-process media details and throw if not allowed on Instagram.
        if item.get('type', '') == 'photo':
            # Determine the photo details.
            # $itemInternalMetadata->setPhotoDetails(Constants::FEED_TIMELINE_ALBUM, $item['file']);
            pass

        elif item.get('type', '') == 'video':
            # Determine the video details.
            # $itemInternalMetadata->setVideoDetails(Constants::FEED_TIMELINE_ALBUM, $item['file']);
            pass

        else:
            raise Exception('Unsupported album media type "{}".'.format(item['type']))

        itemInternalMetadata = {}
        item['internalMetadata'] = itemInternalMetadata

    # Perform all media file uploads.
    for idx, item in enumerate(media):
        itemInternalMetadata = item['internalMetadata']
        item_upload_id = str(int(time.time() * 1000))
        if item.get('type', '') == 'photo':
            upload_photo(self, photo=item['file'], caption=caption, is_sidecar=True, upload_id=item_upload_id,
                         from_video=True)
            # $itemInternalMetadata->setPhotoUploadResponse($this->ig->internal->uploadPhotoData(Constants::FEED_TIMELINE_ALBUM, $itemInternalMetadata));

        elif item.get('type', '') == 'video':
            # Attempt to upload the video data.
            self.uploadVideo(item['file'], item['thumbnail'], caption=caption, is_sidecar=True,
                             upload_id=item_upload_id)
            # $itemInternalMetadata = $this->ig->internal->uploadVideo(Constants::FEED_TIMELINE_ALBUM, $item['file'], $itemInternalMetadata);
            # Attempt to upload the thumbnail, associated with our video's ID.
            # $itemInternalMetadata->setPhotoUploadResponse($this->ig->internal->uploadPhotoData(Constants::FEED_TIMELINE_ALBUM, $itemInternalMetadata));
            pass
        item['internalMetadata']['upload_id'] = item_upload_id

    album_internal_metadata = {}

    # CONFIGURE
    configure_timeout = options.get("configure_timeout")
    for attempt in range(4):
        if configure_timeout:
            time.sleep(configure_timeout)
        if configure_time_line_album(self, media, album_internal_metadata, captionText=caption):
            media = self.last_json.get("media")
            self.expose()
            return media
    return False


def configure_time_line_album(self, media, albumInternalMetadata, captionText='', location=None):
    endpoint = 'media/configure_sidecar/'
    albumUploadId = str(calendar.timegm(datetime.utcnow().utctimetuple()))

    date = datetime.utcnow().isoformat()
    childrenMetadata = []
    for item in media:
        itemInternalMetadata = item['internalMetadata']
        uploadId = itemInternalMetadata.get('upload_id', str(calendar.timegm(datetime.utcnow().utctimetuple())))
        if item.get('type', '') == 'photo':
            # Build this item's configuration.
            photoConfig = {'date_time_original': date,
                           'scene_type': 1,
                           'disable_comments': False,
                           'upload_id': uploadId,
                           'source_type': 0,
                           'scene_capture_type': 'standard',
                           'date_time_digitized': date,
                           'geotag_enabled': False,
                           'camera_position': 'back',
                           'edits': {'filter_strength': 1,
                                     'filter_name': 'IGNormalFilter'}
                           }
            # This usertag per-file EXTERNAL metadata is only supported for PHOTOS!
            if item.get('usertags', []):
                # NOTE: These usertags were validated in Timeline::uploadAlbum.
                photoConfig['usertags'] = json.dumps({'in': item['usertags']})

            childrenMetadata.append(photoConfig)
        if item.get('type', '') == 'video':
            # Get all of the INTERNAL per-VIDEO metadata.
            videoDetails = itemInternalMetadata.get('video_details', {})
            # Build this item's configuration.
            videoConfig = {'length': videoDetails.get('duration', 1.0),
                           'date_time_original': date,
                           'scene_type': 1,
                           'poster_frame_index': 0,
                           'trim_type': 0,
                           'disable_comments': False,
                           'upload_id': uploadId,
                           'source_type': 'library',
                           'geotag_enabled': False,
                           'edits': {
                               'length': videoDetails.get('duration', 1.0),
                               'cinema': 'unsupported',
                               'original_length': videoDetails.get('duration', 1.0),
                               'source_type': 'library',
                               'start_time': 0,
                               'camera_position': 'unknown',
                               'trim_type': 0}
                           }

            childrenMetadata.append(videoConfig)
    # Build the request...
    data = self.json_data(
        {'_csrftoken': self.token,
         '_uid': self.user_id,
         '_uuid': self.uuid,
         'client_sidecar_id': albumUploadId,
         'caption': captionText,
         'children_metadata': childrenMetadata}
    )

    return self.send_request("media/configure_sidecar/?", data)
