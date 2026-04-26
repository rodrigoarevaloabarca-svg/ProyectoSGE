from django.urls import path

from . import views

app_name = 'dashboard'
urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('contacto/', views.contacto, name='contacto'),
    path('chatbot/', views.chatbot_ia, name='chatbot_ia'),
]
