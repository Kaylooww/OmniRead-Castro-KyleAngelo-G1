from django.urls import path

from .views import ProfileEditView, ProfileView, SignUpView, logout_view

urlpatterns = [
    # Comes before Django's built-in auth URLs, so this logout is the one used
    path("logout/", logout_view, name="logout"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/edit/", ProfileEditView.as_view(), name="profile_edit"),
]
