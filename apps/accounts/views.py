from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.shortcuts import redirect
from .forms import AzertaLoginForm


class AzertaLoginView(LoginView):
    """
    Login view styled with Azerta branding.
    """
    template_name = 'accounts/login.html'
    authentication_form = AzertaLoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me', False)
        if not remember_me:
            # Session expires when user closes the browser
            self.request.session.set_expiry(0)
        else:
            # 2 weeks session
            self.request.session.set_expiry(1209600)
        messages.success(self.request, f"¡Bienvenido de vuelta, {form.get_user().get_username()}!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Credenciales incorrectas. Por favor verifique su usuario y contraseña.")
        return super().form_invalid(form)


class AzertaLogoutView(LogoutView):
    """
    Logout view redirecting to home.
    """
    next_page = 'login'

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, "Has cerrado sesión correctamente.")
        return super().dispatch(request, *args, **kwargs)
