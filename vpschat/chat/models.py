from __future__ import annotations

from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import make_password, check_password

slug_validator = RegexValidator(
    regex=r"^[a-z0-9-]+$",
    message="Slug must contain only lowercase letters, digits and hyphens.",
)

class Room(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, validators=[slug_validator])
    is_protected = models.BooleanField(default=False)
    password_hash = models.CharField(max_length=256, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def set_password(self, raw_password: str | None) -> None:
        if raw_password:
            self.password_hash = make_password(raw_password)
            self.is_protected = True
        else:
            self.password_hash = None
            self.is_protected = False

    def check_password(self, raw_password: str) -> bool:
        if not self.is_protected or not self.password_hash:
            return True
        return check_password(raw_password, self.password_hash)


class Message(models.Model):
    TYPE_TEXT = "text"
    TYPE_FILE = "file"
    TYPE_SYSTEM = "system"
    TYPE_CHOICES = [
        (TYPE_TEXT, "Text"),
        (TYPE_FILE, "File"),
        (TYPE_SYSTEM, "System"),
    ]

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="messages")
    sender_name = models.CharField(max_length=80)
    content = models.TextField(blank=True, default="")
    timestamp = models.DateTimeField(default=timezone.now)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_TEXT)
    file = models.FileField(upload_to="uploads/%Y/%m/%d/", blank=True, null=True)
    file_name = models.CharField(max_length=255, blank=True, default="")
    uploader_session_key = models.CharField(max_length=64, blank=True, default="")

    class Meta:
        ordering = ["timestamp"]

    def __str__(self) -> str:
        return f"[{self.room.slug}] {self.sender_name}: {self.type}"


class RoomPresence(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="presences")
    session_key = models.CharField(max_length=64)
    display_name = models.CharField(max_length=80)
    last_seen_at = models.DateTimeField(default=timezone.now)
    is_online = models.BooleanField(default=False)

    class Meta:
        unique_together = [("room", "session_key")]
        indexes = [
            models.Index(fields=["room", "is_online"]),
            models.Index(fields=["room", "last_seen_at"]),
        ]

    def touch(self, online: bool | None = None) -> None:
        self.last_seen_at = timezone.now()
        if online is not None:
            self.is_online = online
        self.save(update_fields=["last_seen_at", "is_online"])

    def __str__(self) -> str:
        return f"{self.display_name} @ {self.room.slug}"
