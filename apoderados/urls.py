from django.urls import path
from . import views
"""apoderados/urls.py — VERSIÓN CORREGIDA"""
from django.urls import path
from . import views

app_name = 'apoderados'

urlpatterns = [
    path('',                    views.lista_apoderados,   name='lista'),
    path('crear/',              views.crear_apoderado,    name='crear'),
    path('<int:pk>/',           views.detalle_apoderado,  name='detalle'),
    path('<int:pk>/editar/',    views.editar_apoderado,   name='editar'),    # ← faltaba
    path('<int:pk>/eliminar/',  views.eliminar_apoderado, name='eliminar'),  # ← faltaba
]