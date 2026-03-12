"""APP: usuarios - views.py"""
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy, reverse

from .models import Usuario
from .forms import UsuarioCreacionForm, UsuarioEdicionForm, LoginForm


def solo_admin(user):
    return user.is_authenticated and user.es_admin
class LoginPersonalizado(LoginView):
    template_name        = 'usuarios/login.html'
    authentication_form  = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('dashboard:inicio')


class LogoutPersonalizado(LogoutView):
    next_page = reverse_lazy('usuarios:login')

@login_required
def perfil(request):
    if request.method == 'POST':
        form = UsuarioEdicionForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('usuarios:perfil')
    else:
        form = UsuarioEdicionForm(instance=request.user)
    return render(request, 'usuarios/perfil.html', {
        'usuario': request.user,
        'form':    form,
        'breadcrumbs': [
            {'label': 'Mi Perfil', 'url': ''},
        ],
    })

@login_required
@user_passes_test(solo_admin)
def lista_usuarios(request):
    usuarios = Usuario.objects.all().order_by('rol', 'last_name')
    return render(request, 'usuarios/lista.html', {
        'usuarios': usuarios,
        'breadcrumbs': [
            {'label': 'Usuarios', 'url': ''},
        ],
    })


@login_required
@user_passes_test(solo_admin)
def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioCreacionForm(request.POST, request.FILES)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, f'Usuario {usuario.get_full_name()} creado exitosamente.')
            return redirect('usuarios:lista')
    else:
        form = UsuarioCreacionForm()
    return render(request, 'usuarios/form.html', {
        'form':  form,
        'titulo': 'Crear Usuario',
        'breadcrumbs': [
            {'label': 'Usuarios', 'url': reverse('usuarios:lista')},
            {'label': 'Crear',    'url': ''},
        ],
    })


@login_required
@user_passes_test(solo_admin)
def editar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        form = UsuarioEdicionForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuario {usuario.get_full_name()} actualizado.')
            return redirect('usuarios:lista')
    else:
        form = UsuarioEdicionForm(instance=usuario)
    return render(request, 'usuarios/form.html', {
        'form':  form,
        'titulo': f'Editar {usuario.get_full_name() or usuario.username}',
        'breadcrumbs': [
            {'label': 'Usuarios',                                     'url': reverse('usuarios:lista')},
            {'label': usuario.get_full_name() or usuario.username,   'url': ''},
            {'label': 'Editar',                                       'url': ''},
        ],
    })


@login_required
@user_passes_test(solo_admin)
def desactivar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if usuario == request.user:
        messages.error(request, 'No puedes desactivar tu propia cuenta.')
        return redirect('usuarios:lista')
    usuario.is_active = False
    usuario.save()
    messages.warning(request, f'Usuario {usuario.get_full_name()} desactivado.')
    return redirect('usuarios:lista')
