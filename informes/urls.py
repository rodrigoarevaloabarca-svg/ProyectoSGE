"""APP: informes - urls.py"""
from django.urls import path
from . import views

app_name = 'informes'

urlpatterns = [
    # Dashboard central
    path('dashboard/',            views.dashboard_informes,  name='dashboard'),

    # Períodos
    path('periodos/',                 views.lista_periodos,        name='lista_periodos'),
    path('periodos/crear/',           views.crear_periodo,         name='crear_periodo'),
    path('periodos/<int:pk>/editar/', views.editar_periodo,        name='editar_periodo'),

    # Informe individual por alumno
    path('',                                               views.seleccionar_informe, name='seleccionar'),
    path('<int:alumno_id>/periodo/<int:periodo_id>/',      views.ver_informe,         name='ver_informe'),
    path('<int:alumno_id>/periodo/<int:periodo_id>/pdf/',  views.descargar_pdf,       name='descargar_pdf'),

    # Informes especiales
    path('ranking-curso/',  views.informe_ranking_curso, name='ranking_curso'),
    path('fin-de-anio/',    views.informe_fin_anio,      name='fin_anio'),

    # Impresión masiva
    path('masivo/',         views.impresion_masiva,      name='impresion_masiva'),
]
