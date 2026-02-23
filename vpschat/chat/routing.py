from django.urls import re_path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r"^ws/rooms/(?P<slug>[a-z0-9-]+)/$", ChatConsumer.as_asgi()),
]
