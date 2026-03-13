"""APP: historial - urls.py"""
from django.urls import path
from . import views

app_name = 'historial'

urlpatterns = [
    path('', views.lista_historial, name='lista'),
]
