from django.urls import path
from . import views
app_name = 'anotaciones'
urlpatterns = [
    path('alumno/<int:alumno_id>/', views.anotaciones_alumno, name='alumno'),
    path('crear/<int:alumno_id>/', views.crear_anotacion, name='crear'),
    path('<int:pk>/editar/', views.editar_anotacion, name='editar'),
]
