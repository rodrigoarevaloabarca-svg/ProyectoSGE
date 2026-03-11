from django.urls import path
from . import views
app_name = 'alumnos'
urlpatterns = [
    path('', views.lista_alumnos, name='lista'),
    path('<int:pk>/', views.detalle_alumno, name='detalle'),
    path('crear/', views.crear_alumno, name='crear'),
    path('<int:pk>/editar/', views.editar_alumno, name='editar'),
]
