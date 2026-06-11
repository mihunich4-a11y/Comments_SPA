from celery import shared_task
from PIL import Image

from .models import Comment


@shared_task
def resize_comment_image(comment_id: int):
    try:
        comment = Comment.objects.get(pk=comment_id)
    except Comment.DoesNotExist:
        return

    if not comment.image:
        return

    img = Image.open(comment.image.path)
    if img.width > 320 or img.height > 240:
        img.thumbnail((320, 240), Image.LANCZOS)
        img.save(comment.image.path)
