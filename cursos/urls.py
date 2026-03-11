from django.urls import path
from . import views
app_name = 'cursos'
urlpatterns = [
    path('', views.lista_cursos, name='lista'),
    path('<int:pk>/', views.detalle_curso, name='detalle'),
    path('crear/', views.crear_curso, name='crear'),
    path('<int:pk>/editar/', views.editar_curso, name='editar'),
]
