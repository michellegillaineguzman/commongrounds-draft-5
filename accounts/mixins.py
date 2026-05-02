from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

class RoleRequiredMixin(LoginRequiredMixin):
    role = None

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if not request.user.is_authenticated:
            return response
        try:
            profile = request.user.profile
        except Exception:
            raise PermissionDenied
        if self.role and profile.role != self.role:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)