from django.urls import path
from . import views
app_name = 'notas'
urlpatterns = [
    path('libro/<int:curso_id>/', views.libro_notas_curso, name='libro'),
    path('alumno/<int:alumno_id>/asignatura/<int:asignatura_id>/', views.notas_alumno_asignatura, name='detalle'),
    path('alumno/<int:alumno_id>/asignatura/<int:asignatura_id>/agregar/', views.agregar_nota, name='agregar'),
    path('<int:nota_id>/editar/', views.editar_nota, name='editar'),
    path('<int:nota_id>/eliminar/', views.eliminar_nota, name='eliminar'),
]
