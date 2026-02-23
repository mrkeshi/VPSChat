from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("", views.room_list, name="room_list"),
    path("rooms/<slug:slug>/", views.room_chat, name="room_chat"),
    path("rooms/<slug:slug>/enter/", views.enter_room, name="enter_room"),
    path("rooms/<slug:slug>/presence/", views.room_presence, name="room_presence"),
    path("rooms/<slug:slug>/upload/", views.upload_file, name="upload_file"),
    path("rooms/<slug:slug>/messages/<int:message_id>/delete-file/", views.delete_file_message, name="delete_file_message"),

    # management panel
    path("manage/rooms/", views.manage_rooms, name="manage_rooms"),
    path("manage/rooms/create/", views.manage_room_create, name="manage_room_create"),
    path("manage/rooms/<int:room_id>/edit/", views.manage_room_edit, name="manage_room_edit"),
    path("manage/rooms/<int:room_id>/delete/", views.manage_room_delete, name="manage_room_delete"),
]
