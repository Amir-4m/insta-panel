import logging

from celery import shared_task
from django.utils import timezone

from apps.post.models import Post, Story
from apps.post.utils.post import publish_post, upload_story

logger = logging.getLogger(__name__)


@shared_task
def publish_post_async(post_id):
    try:
        publish_post(post_id)
        Post.objects.filter(id=post_id).update(publish_time=timezone.now())
    except Exception as e:
        logger.error(f"publishing post {post_id} got error : {e}")


@shared_task
def publish_story_async(story_id):
    try:
        if upload_story(story_id):
            Story.objects.filter(id=story_id).update(publish_time=timezone.now())
        else:
            logger.error(f"upload story {story_id} failed")

    except Exception as e:
        logger.error(f"publishing story {story_id} got error : {e}")
