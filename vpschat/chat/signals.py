from __future__ import annotations

import logging

from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver

from .models import Message, Room

logger = logging.getLogger(__name__)


@receiver(post_delete, sender=Message)
def delete_message_file_on_delete(sender, instance: Message, **kwargs):
    """Delete uploaded file from storage when a file-message is deleted.

    Django does not delete FileField files automatically on model deletion.
    """
    try:
        if instance.file:
            instance.file.delete(save=False)
    except Exception:
        logger.exception("Failed to delete file for Message id=%s", getattr(instance, "id", None))


@receiver(pre_delete, sender=Room)
def delete_room_files_on_delete(sender, instance: Room, **kwargs):
    """When a room is deleted, delete *all* related uploaded files as well."""
    try:
        qs = instance.messages.exclude(file="").exclude(file__isnull=True).only("id", "file")
        for m in qs.iterator(chunk_size=200):
            try:
                if m.file:
                    m.file.delete(save=False)
            except Exception:
                logger.exception(
                    "Failed to delete file for Room=%s (Message id=%s)",
                    getattr(instance, "id", None),
                    getattr(m, "id", None),
                )
    except Exception:
        logger.exception("Failed to cleanup files for Room id=%s", getattr(instance, "id", None))
