from django.urls import path

from .views import AdminDashboardView, ReaderDashboardView, dashboard

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("dashboard/reader/", ReaderDashboardView.as_view(), name="reader_dashboard"),
    path("dashboard/admin/", AdminDashboardView.as_view(), name="admin_dashboard"),
]
