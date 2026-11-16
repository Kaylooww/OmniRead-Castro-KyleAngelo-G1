from django.urls import path

from .views import AdminDashboardView, ReaderDashboardView, UserEditView, UserListView, dashboard

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("dashboard/reader/", ReaderDashboardView.as_view(), name="reader_dashboard"),
    path("dashboard/admin/", AdminDashboardView.as_view(), name="admin_dashboard"),
    path("dashboard/admin/users/", UserListView.as_view(), name="user_list"),
    path("dashboard/admin/users/<int:pk>/edit/", UserEditView.as_view(), name="user_edit"),
]
