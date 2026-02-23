from __future__ import annotations

import mimetypes
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.uploadedfile import UploadedFile
from django.http import Http404, JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.timesince import timesince
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_protect
from django.db.models import Count, Q

from .forms import EnterRoomForm, RoomAdminForm
from .models import Room, Message, RoomPresence


def _ensure_session(request: HttpRequest) -> None:
    # Ensure we have a session key to identify "user"
    if not request.session.session_key:
        request.session.save()

def _get_display_name(request: HttpRequest) -> str | None:
    return request.session.get("display_name")

def _set_display_name(request: HttpRequest, name: str) -> None:
    request.session["display_name"] = name.strip()
    request.session.modified = True

def _room_access_map(request: HttpRequest) -> dict:
    return request.session.get("room_access", {})

def _has_room_access(request: HttpRequest, room: Room) -> bool:
    if not room.is_protected:
        return True
    access = _room_access_map(request)
    return bool(access.get(room.slug))

def _grant_room_access(request: HttpRequest, room: Room) -> None:
    access = _room_access_map(request)
    access[room.slug] = True
    request.session["room_access"] = access
    request.session.set_expiry(getattr(settings, "COOKIE_AGE", settings.SESSION_COOKIE_AGE))
    request.session.modified = True

def room_list(request: HttpRequest) -> HttpResponse:
    rooms = (
        Room.objects.all()
        .annotate(message_count=Count("messages", distinct=True))
        .annotate(online_count=Count("presences", filter=Q(presences__is_online=True), distinct=True))
    )
    return render(request, "chat/rooms_list.html", {"rooms": rooms})

@csrf_protect
@require_http_methods(["GET", "POST"])
def enter_room(request: HttpRequest, slug: str) -> HttpResponse:
    _ensure_session(request)
    room = get_object_or_404(Room, slug=slug)
    initial = {"display_name": _get_display_name(request) or ""}
    form = EnterRoomForm(initial=initial)

    if request.method == "POST":
        form = EnterRoomForm(request.POST)
        if form.is_valid():
            display_name = (form.cleaned_data.get("display_name") or "").strip()
            password = form.cleaned_data.get("password") or ""

            if not _get_display_name(request):
                if not display_name:
                    form.add_error("display_name", "لطفاً یک نام نمایشی وارد کنید.")
                else:
                    _set_display_name(request, display_name)
            elif display_name and display_name != _get_display_name(request):
                # allow user to change their display name
                _set_display_name(request, display_name)

            if room.is_protected and not _has_room_access(request, room):
                if not password:
                    form.add_error("password", "این اتاق رمز دارد. رمز را وارد کنید.")
                elif not room.check_password(password):
                    form.add_error("password", "رمز اشتباه است.")
                else:
                    _grant_room_access(request, room)

            if not form.errors:
                return redirect("chat:room_chat", slug=room.slug)

    return render(request, "chat/room_enter.html", {"room": room, "form": form})

def room_chat(request: HttpRequest, slug: str) -> HttpResponse:
    _ensure_session(request)
    room = get_object_or_404(Room, slug=slug)

    if room.is_protected and not _has_room_access(request, room):
        messages.info(request, "برای ورود به این اتاق باید رمز را وارد کنید.")
        return redirect("chat:enter_room", slug=slug)

    display_name = _get_display_name(request)
    if not display_name:
        return redirect("chat:enter_room", slug=slug)

    # fetch last messages
    last_messages = []
    if getattr(settings, "SAVE_MESSAGES_TO_DB", True):
        last_messages = list(room.messages.select_related("room").order_by("-timestamp")[:80])
        last_messages.reverse()
        # Clean up legacy debug messages that were accidentally stored (content was literally "text"/"system").
        junk = {"text", "system", "file"}
        last_messages = [m for m in last_messages if not (m.type in (Message.TYPE_TEXT, Message.TYPE_SYSTEM) and (m.content or "").strip() in junk)]

    # Touch presence (also shows in UI list)
    pres, _ = RoomPresence.objects.get_or_create(
        room=room,
        session_key=request.session.session_key,
        defaults={"display_name": display_name, "is_online": False, "last_seen_at": timezone.now()},
    )
    pres.display_name = display_name
    pres.last_seen_at = timezone.now()
    pres.save(update_fields=["display_name", "last_seen_at"])

    return render(
        request,
        "chat/chat_room.html",
        {
            "room": room,
            "display_name": display_name,
            "messages": last_messages,
            "ws_path": f"/ws/rooms/{room.slug}/",
            "enable_file_upload": getattr(settings, "ENABLE_FILE_UPLOAD", True),
            "max_upload_size": getattr(settings, "MAX_UPLOAD_SIZE", 0),
            "allowed_upload_types": getattr(settings, "ALLOWED_UPLOAD_TYPES", []),
        },
    )

def room_presence(request: HttpRequest, slug: str) -> JsonResponse:
    _ensure_session(request)
    room = get_object_or_404(Room, slug=slug)
    if room.is_protected and not _has_room_access(request, room):
        return JsonResponse({"detail": "forbidden"}, status=403)

    qs = RoomPresence.objects.filter(room=room).order_by("-is_online", "-last_seen_at")
    data = []
    now = timezone.now()
    for p in qs[:200]:
        data.append({
            "display_name": p.display_name,
            "is_online": p.is_online,
            "last_seen_human": "همین الان" if (now - p.last_seen_at).total_seconds() < 10 else f"{timesince(p.last_seen_at, now)} پیش",
            "last_seen_at": p.last_seen_at.isoformat(),
        })
    return JsonResponse({"users": data})

def _validate_upload(f: UploadedFile) -> tuple[bool, str]:
    max_size = int(getattr(settings, "MAX_UPLOAD_SIZE", 0) or 0)
    # max_size <= 0 means "no limit"
    if max_size > 0 and f.size > max_size:
        return False, "حجم فایل بیشتر از حد مجاز است."

    content_type = getattr(f, "content_type", "") or ""
    allowed = set(getattr(settings, "ALLOWED_UPLOAD_TYPES", []))
    if allowed and content_type not in allowed:
        return False, "نوع فایل مجاز نیست."

    # Basic filename sanity
    if ".." in f.name or f.name.startswith("/"):
        return False, "نام فایل نامعتبر است."

    return True, ""

@csrf_protect
@require_POST
def upload_file(request: HttpRequest, slug: str) -> JsonResponse:
    _ensure_session(request)
    room = get_object_or_404(Room, slug=slug)

    if not getattr(settings, "ENABLE_FILE_UPLOAD", True):
        return JsonResponse({"detail": "uploads_disabled"}, status=403)

    if room.is_protected and not _has_room_access(request, room):
        return JsonResponse({"detail": "forbidden"}, status=403)

    display_name = _get_display_name(request)
    if not display_name:
        return JsonResponse({"detail": "no_display_name"}, status=400)

    f = request.FILES.get("file")
    if not f:
        return JsonResponse({"detail": "no_file"}, status=400)

    ok, err = _validate_upload(f)
    if not ok:
        return JsonResponse({"detail": err}, status=400)

    # Save as a Message (file)
    msg = None
    if getattr(settings, "SAVE_MESSAGES_TO_DB", True):
        msg = Message.objects.create(
            room=room,
            sender_name=display_name,
            type=Message.TYPE_FILE,
            file=f,
            file_name=f.name,
            uploader_session_key=request.session.session_key or "",
            content="",
        )
        file_url = msg.file.url if msg.file else ""
        msg_id = msg.id
    else:
        # If DB saving is off, we still store file via default storage by creating a temp Message-less save
        # but that complicates deletions. For simplicity, we require SAVE_MESSAGES_TO_DB for uploads.
        return JsonResponse({"detail": "برای آپلود فایل باید SAVE_MESSAGES_TO_DB فعال باشد."}, status=400)

    return JsonResponse({
        "message_id": msg_id,
        "file_url": file_url,
        "file_name": msg.file_name,
        "content_type": getattr(f, "content_type", ""),
    })

@csrf_protect
@require_POST
def delete_file_message(request: HttpRequest, slug: str, message_id: int) -> JsonResponse:
    _ensure_session(request)
    room = get_object_or_404(Room, slug=slug)
    msg = get_object_or_404(Message, id=message_id, room=room, type=Message.TYPE_FILE)

    # Permission: admin/staff OR uploader session
    can = False
    if request.user.is_authenticated and request.user.is_staff:
        can = True
    if (request.session.session_key and msg.uploader_session_key and request.session.session_key == msg.uploader_session_key):
        can = True

    if not can:
        return JsonResponse({"detail": "forbidden"}, status=403)

    # delete file + message
    if msg.file:
        msg.file.delete(save=False)
    msg.delete()
    return JsonResponse({"ok": True})


# ----------------------
# Room management panel (staff only)
# ----------------------

@staff_member_required
def manage_rooms(request: HttpRequest) -> HttpResponse:
    rooms = Room.objects.all()
    return render(request, "chat/manage/rooms_list.html", {"rooms": rooms})

@staff_member_required
@csrf_protect
@require_http_methods(["GET", "POST"])
def manage_room_create(request: HttpRequest) -> HttpResponse:
    form = RoomAdminForm()
    if request.method == "POST":
        form = RoomAdminForm(request.POST)
        if form.is_valid():
            room = Room(
                name=form.cleaned_data["name"],
                slug=form.cleaned_data["slug"],
                is_protected=form.cleaned_data.get("is_protected", False),
            )
            password = form.cleaned_data.get("password") or ""
            if room.is_protected:
                room.set_password(password)
            else:
                room.set_password(None)
            room.save()
            messages.success(request, "اتاق ایجاد شد.")
            return redirect("chat:manage_rooms")
    return render(request, "chat/manage/room_form.html", {"form": form, "mode": "create"})

@staff_member_required
@csrf_protect
@require_http_methods(["GET", "POST"])
def manage_room_edit(request: HttpRequest, room_id: int) -> HttpResponse:
    room = get_object_or_404(Room, id=room_id)
    form = RoomAdminForm(initial={"name": room.name, "slug": room.slug, "is_protected": room.is_protected, "password": ""})

    if request.method == "POST":
        form = RoomAdminForm(request.POST)
        if form.is_valid():
            room.name = form.cleaned_data["name"]
            room.slug = form.cleaned_data["slug"]
            is_protected = form.cleaned_data.get("is_protected", False)
            password = form.cleaned_data.get("password") or ""

            if is_protected:
                # Change password if provided; otherwise keep existing hash
                room.is_protected = True
                if password:
                    room.set_password(password)
                else:
                    if not room.password_hash:
                        form.add_error("password", "برای اتاق رمزدار، باید رمز تنظیم شود.")
                        return render(request, "chat/manage/room_form.html", {"form": form, "mode": "edit", "room": room})
            else:
                room.set_password(None)

            room.save()
            messages.success(request, "اتاق به‌روزرسانی شد.")
            return redirect("chat:manage_rooms")

    return render(request, "chat/manage/room_form.html", {"form": form, "mode": "edit", "room": room})

@staff_member_required
@csrf_protect
@require_http_methods(["GET", "POST"])
def manage_room_delete(request: HttpRequest, room_id: int) -> HttpResponse:
    room = get_object_or_404(Room, id=room_id)
    if request.method == "POST":
        room.delete()
        messages.success(request, "اتاق حذف شد.")
        return redirect("chat:manage_rooms")
    return render(request, "chat/manage/confirm_delete.html", {"room": room})
