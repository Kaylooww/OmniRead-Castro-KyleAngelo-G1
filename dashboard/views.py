from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, UpdateView

from accounts.models import CustomUser

from .forms import UserManageForm

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


# ===== Admin panel: manage users =====

class UserListView(RoleRequiredMixin, ListView):
    """Table of all users, with an optional search box (?q=...)."""
    role = Role.ADMIN
    template_name = "dashboard/user_list.html"
    context_object_name = "members"

    def get_queryset(self):
        users = CustomUser.objects.order_by("-date_joined")
        q = self.request.GET.get("q", "").strip()
        if q:
            users = users.filter(
                Q(email__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q)
            )
        return users


class UserEditView(RoleRequiredMixin, SuccessMessageMixin, UpdateView):
    """Change another user's role or deactivate them."""
    role = Role.ADMIN
    form_class = UserManageForm
    template_name = "dashboard/user_form.html"
    context_object_name = "member"
    success_url = reverse_lazy("user_list")
    success_message = "User updated."

    def get_queryset(self):
        # Admins cannot edit themselves here, so they can't remove their own admin access by mistake
        return CustomUser.objects.exclude(pk=self.request.user.pk)
