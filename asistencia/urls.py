from django.urls import path
from . import views
app_name = 'asistencia'
urlpatterns = [
    path('tomar/<int:asignatura_id>/', views.tomar_asistencia, name='tomar'),
    path('asignatura/<int:asignatura_id>/', views.resumen_asignatura, name='resumen_asignatura'),
    path('alumno/<int:alumno_id>/', views.asistencia_alumno, name='historial_alumno'),
]
