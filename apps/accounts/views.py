from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from functools import wraps

from .forms import AzertaLoginForm, UserCreateForm, UserUpdateForm, build_initial_password
from .models import User


def staff_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        is_legacy_admin = request.user.is_staff and request.user.role != 'TI'
        if not (request.user.is_superuser or request.user.role == 'ADMIN' or is_legacy_admin):
            messages.error(request, 'No tienes permisos para administrar usuarios.')
            return redirect('dashboard')
        return view(request, *args, **kwargs)

    return wrapped


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


@staff_required
def user_list(request):
    users = User.objects.prefetch_related('tickets').order_by('last_name', 'first_name', 'username')
    return render(request, 'accounts/user_list.html', {'users': users})


@staff_required
def user_create(request):
    form = UserCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        password = build_initial_password(user.first_name, user.rut)
        messages.success(request, f'Usuario creado. Contraseña inicial: {password}')
        return redirect('user_list')
    return render(request, 'accounts/user_form.html', {'form': form, 'page_title': 'Nuevo usuario'})


@staff_required
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = UserUpdateForm(request.POST or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        updated_user = form.save()
        if form.cleaned_data.get('reset_password'):
            password = build_initial_password(updated_user.first_name, updated_user.rut)
            messages.success(request, f'Usuario actualizado. Nueva contraseña: {password}')
        else:
            messages.success(request, 'Usuario actualizado correctamente.')
        return redirect('user_list')
    return render(request, 'accounts/user_form.html', {
        'form': form,
        'page_title': f'Editar usuario: {user.get_full_name() or user.username}',
        'edit_user': user,
    })


@staff_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method != 'POST':
        return redirect('user_list')
    if user == request.user:
        messages.error(request, 'No puedes eliminar tu propio usuario.')
    elif user.tickets.exists():
        user.is_active = False
        user.save(update_fields=['is_active'])
        messages.success(request, 'Usuario desactivado para conservar su historial de solicitudes.')
    else:
        user.delete()
        messages.success(request, 'Usuario eliminado correctamente.')
    return redirect('user_list')


@login_required
def dismiss_onboarding(request):
    if request.method == 'POST':
        request.user.onboarding_dismissed = True
        request.user.save(update_fields=['onboarding_dismissed'])
        messages.success(request, 'La guía inicial no volverá a mostrarse.')
    return redirect('dashboard')
