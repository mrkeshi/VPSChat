from __future__ import annotations

import json
from django.conf import settings
from django.utils import timezone
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .models import Room, Message, RoomPresence


@database_sync_to_async
def get_room(slug: str) -> Room | None:
    try:
        return Room.objects.get(slug=slug)
    except Room.DoesNotExist:
        return None

@database_sync_to_async
def has_access(session, room: Room) -> bool:
    if not room.is_protected:
        return True
    access = session.get("room_access", {})
    return bool(access.get(room.slug))

@database_sync_to_async
def get_display_name(session) -> str | None:
    return session.get("display_name")

@database_sync_to_async
def touch_presence(room: Room, session_key: str, display_name: str, online: bool) -> None:
    pres, _ = RoomPresence.objects.get_or_create(
        room=room,
        session_key=session_key,
        defaults={"display_name": display_name, "is_online": online, "last_seen_at": timezone.now()},
    )
    pres.display_name = display_name
    pres.last_seen_at = timezone.now()
    pres.is_online = online
    pres.save(update_fields=["display_name", "last_seen_at", "is_online"])

@database_sync_to_async
def save_message(room: Room, sender_name: str, content: str, msg_type: str, file_url: str = "", file_name: str = "") -> int | None:
    if not getattr(settings, "SAVE_MESSAGES_TO_DB", True):
        return None
    if msg_type == Message.TYPE_TEXT:
        msg = Message.objects.create(room=room, sender_name=sender_name, content=content, type=Message.TYPE_TEXT)
        return msg.id
    if msg_type == Message.TYPE_SYSTEM:
        msg = Message.objects.create(room=room, sender_name=sender_name, content=content, type=Message.TYPE_SYSTEM)
        return msg.id
    # file messages are created by upload endpoint
    return None

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_slug = self.scope["url_route"]["kwargs"]["slug"]
        self.room_group_name = f"room_{self.room_slug}"

        self.room = await get_room(self.room_slug)
        if not self.room:
            await self.close(code=4404)
            return

        session = self.scope.get("session")
        if not session:
            await self.close(code=4401)
            return

        allowed = await has_access(session, self.room)
        if not allowed:
            await self.close(code=4403)
            return

        display_name = await get_display_name(session)
        if not display_name:
            await self.close(code=4401)
            return

        self.display_name = display_name
        self.session_key = session.session_key or ""

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        if self.session_key:
            await touch_presence(self.room, self.session_key, self.display_name, True)

        # system join
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "message": {
                    "type": "system",
                    "sender": "سیستم",
                    "content": f"{self.display_name} وارد شد",
                    "timestamp": timezone.now().isoformat(),
                },
            },
        )
        await save_message(self.room, "سیستم", f"{self.display_name} وارد شد", Message.TYPE_SYSTEM)

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        except Exception:
            pass

        if getattr(self, "room", None) and getattr(self, "session_key", ""):
            await touch_presence(self.room, self.session_key, getattr(self, "display_name", "کاربر"), False)

        # system leave
        if getattr(self, "room", None) and getattr(self, "display_name", None):
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat.message",
                    "message": {
                        "type": "system",
                        "sender": "سیستم",
                        "content": f"{self.display_name} خارج شد",
                        "timestamp": timezone.now().isoformat(),
                    },
                },
            )
            await save_message(self.room, "سیستم", f"{self.display_name} خارج شد", Message.TYPE_SYSTEM)

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return
        try:
            payload = json.loads(text_data)
        except json.JSONDecodeError:
            return

        msg_type = payload.get("type", "text")
        content = (payload.get("content") or "").strip()

        if getattr(self, "session_key", "") and getattr(self, "room", None):
            await touch_presence(self.room, self.session_key, self.display_name, True)

        if msg_type == "text":
            if not content:
                return
            message = {
                "type": "text",
                "sender": self.display_name,
                "content": content,
                "timestamp": timezone.now().isoformat(),
            }
            await self.channel_layer.group_send(self.room_group_name, {"type": "chat.message", "message": message})
            await save_message(self.room, self.display_name, content, Message.TYPE_TEXT)
        elif msg_type == "file":
            # File messages are created by HTTP upload endpoint.
            file_url = payload.get("file_url", "")
            file_name = payload.get("file_name", "")
            message_id = payload.get("message_id")
            if not file_url:
                return
            message = {
                "type": "file",
                "sender": self.display_name,
                "content": "",
                "file_url": file_url,
                "file_name": file_name,
                "message_id": message_id,
                "timestamp": timezone.now().isoformat(),
            }
            await self.channel_layer.group_send(self.room_group_name, {"type": "chat.message", "message": message})
        else:
            return

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event["message"], ensure_ascii=False))
