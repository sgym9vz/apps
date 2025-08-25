from django.urls import re_path

from matching_app.channels import chat_consumer

websocket_urlpatterns = [
    re_path(r"^ws/chat/(?P<room_id>\d+)/$", chat_consumer.ChatConsumer.as_asgi()),
]
