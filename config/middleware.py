from django.shortcuts import redirect


class AdminRouteGuardMiddleware:
    """Keep non-administrators out of every direct Django admin URL."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/admin' or request.path.startswith('/admin/'):
            user = request.user
            is_admin = (
                user.is_authenticated
                and user.is_active
                and (user.is_superuser or user.role == 'ADMIN')
            )
            if not is_admin:
                return redirect('dashboard' if user.is_authenticated else 'login')
        return self.get_response(request)
