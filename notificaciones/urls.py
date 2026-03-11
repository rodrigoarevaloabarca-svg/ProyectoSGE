"""APP: notificaciones - urls.py"""
from django.urls import path
from . import views

app_name = 'notificaciones'

urlpatterns = [
    path('',          views.bandeja,           name='bandeja'),
    path('enviadas/', views.enviadas,           name='enviadas'),
    path('redactar/', views.redactar,           name='redactar'),
    path('masivo/',   views.envio_masivo,       name='masivo'),
    path('<int:pk>/', views.ver_notificacion,   name='ver'),
    path('leidas/',   views.marcar_todas_leidas, name='marcar_leidas'),
]
