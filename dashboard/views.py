from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView

from accounts.models import CustomUser

# Create your views here.
Role = CustomUser.Role


@login_required
def dashboard(request):
    """Send each user to their own role's dashboard after login."""
    if request.user.role == Role.ADMIN:
        return redirect("admin_dashboard")
    return redirect("reader_dashboard")


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    role = None

    def test_func(self):
        return self.request.user.role == self.role  # wrong role -> 403 Forbidden


class ReaderDashboardView(RoleRequiredMixin, TemplateView):
    role = Role.READER
    template_name = "dashboard/reader.html"


class AdminDashboardView(RoleRequiredMixin, TemplateView):
    role = Role.ADMIN
    template_name = "dashboard/admin.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["reader_count"] = CustomUser.objects.filter(role=Role.READER).count()
        context["admin_count"] = CustomUser.objects.filter(role=Role.ADMIN).count()
        return context
