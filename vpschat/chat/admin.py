from django.contrib import admin
from .models import Room, Message, RoomPresence

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_protected", "created_at")
    list_filter = ("is_protected",)
    search_fields = ("name", "slug")
    readonly_fields = ("created_at",)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("room", "sender_name", "type", "timestamp")
    list_filter = ("type", "room")
    search_fields = ("sender_name", "content", "file_name")
    readonly_fields = ("timestamp",)

@admin.register(RoomPresence)
class RoomPresenceAdmin(admin.ModelAdmin):
    list_display = ("room", "display_name", "is_online", "last_seen_at")
    list_filter = ("room", "is_online")
    search_fields = ("display_name", "session_key")
