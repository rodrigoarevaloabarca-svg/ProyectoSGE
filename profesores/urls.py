from django.urls import path
from . import views
app_name = 'profesores'
urlpatterns = [
    path('', views.lista_profesores, name='lista'),
    path('crear/', views.crear_profesor, name='crear'),
    path('<int:pk>/', views.detalle_profesor, name='detalle'),
    path('<int:pk>/editar/', views.editar_profesor, name='editar'),
]
