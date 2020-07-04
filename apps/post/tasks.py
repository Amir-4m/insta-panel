import logging

from celery import shared_task
from django.utils import timezone

from apps.post.models import Post
from apps.post.utils.post import publish_post

logger = logging.getLogger(__name__)


@shared_task
def publish_post_async(post_id):
    try:
        publish_post(post_id)
        Post.objects.filter(id=post_id).update(publish_time=timezone.now())
    except Exception as e:
        logger.error(f"publishing post got error : {e}")
