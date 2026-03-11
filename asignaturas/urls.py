from django.urls import path
from . import views
app_name = 'asignaturas'
urlpatterns = [
    path('', views.lista_asignaturas, name='lista'),
    path('curso/<int:curso_id>/', views.asignaturas_por_curso, name='por_curso'),
    path('crear/', views.crear_asignatura, name='crear'),
    path('<int:pk>/editar/', views.editar_asignatura, name='editar'),
]
