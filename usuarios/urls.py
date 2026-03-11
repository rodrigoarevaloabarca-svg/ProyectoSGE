"""APP: usuarios - URLs"""
from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', views.LoginPersonalizado.as_view(), name='login'),
    path('logout/', views.LogoutPersonalizado.as_view(), name='logout'),
    path('perfil/', views.perfil, name='perfil'),
    path('lista/', views.lista_usuarios, name='lista'),
    path('crear/', views.crear_usuario, name='crear'),
    path('<int:pk>/editar/', views.editar_usuario, name='editar'),
    path('<int:pk>/desactivar/', views.desactivar_usuario, name='desactivar'),
]
