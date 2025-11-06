from django.urls import path
from . import views

app_name = "agent_session_manager"

urlpatterns = [
    path("", views.index, name="index"),
    path("get_users/", views.get_users, name="get_users"),
    path("add_user/", views.add_user, name="add_user"),
    path("get_user_details_for_edit/", views.get_user_details_for_edit, name="get_user_details_for_edit"),
]
