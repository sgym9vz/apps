from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from matching_app.views.chat import chat_room, chat_room_create, chat_room_list
from matching_app.views.index import index
from matching_app.views.login import login_view, logout_view
from matching_app.views.recruitment import (
    recruitment_create,
    recruitment_delete,
    recruitment_detail,
    recruitment_search,
    recruitment_timeline,
    recruitment_update,
)
from matching_app.views.signup import signup
from matching_app.views.user_like import user_like_list, user_like_toggle
from matching_app.views.user_profile import user_home, user_profile_detail, user_profile_list, user_profile_update
from matching_app.views.verify import send_new_verification_code, verify_email

urlpatterns = (
    [
        # Index
        path("", index, name="index"),
        # Auth
        path("signup/", signup, name="signup"),
        path("signup/verify/<int:id>/", verify_email, name="verify_email"),
        path("signup/verify/resend/<int:id>/", send_new_verification_code, name="send_new_verification_code"),
        path("login/", login_view, name="login"),
        path("logout/", logout_view, name="logout"),
        # User profile
        path("home/", user_home, name="user_home"),
        path("profiles/me/update/", user_profile_update, name="user_profile_update"),
        path("profiles/list/", user_profile_list, name="user_profile_list"),
        path("profiles/<int:pk>/", user_profile_detail, name="user_profile_detail"),
        # Recruitment
        path("recruitments/", recruitment_timeline, name="recruitment_timeline"),
        path("recruitments/<int:pk>/", recruitment_detail, name="recruitment_detail"),
        path("recruitments/create/", recruitment_create, name="recruitment_create"),
        path("recruitments/<int:pk>/update/", recruitment_update, name="recruitment_update"),
        path("recruitments/<int:pk>/delete/", recruitment_delete, name="recruitment_delete"),
        path("recruitments/search/", recruitment_search, name="recruitment_search"),
        # User like
        path("likes/<int:receiver_id>/", user_like_toggle, name="user_like_toggle"),
        path("likes/list/", user_like_list, name="user_like_list"),
        # Chat
        path("chats/<int:room_id>/", chat_room, name="chat_room"),
        path("chats/create/<int:user_id>/", chat_room_create, name="chat_room_create"),
        path("chats/list/", chat_room_list, name="chat_room_list"),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)
