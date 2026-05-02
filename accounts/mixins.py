from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

class RoleRequiredMixin(LoginRequiredMixin):
    role = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        try:
            profile = request.user.profile
            if self.role and profile.role != self.role:
                raise PermissionDenied
        except Exception:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)