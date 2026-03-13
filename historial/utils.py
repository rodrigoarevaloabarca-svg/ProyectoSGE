"""
APP: historial
ARCHIVO: utils.py

Funciones auxiliares para registrar cambios en el historial.
Se llaman desde las vistas de notas y anotaciones.
"""
from .models import HistorialCambio


def snapshot_nota(nota):
    """Genera un diccionario con el estado actual de una Nota."""
    return {
        'valor':           str(nota.valor),
        'descripcion':     nota.descripcion,
        'fecha':           str(nota.fecha),
        'tipo_evaluacion': str(nota.tipo_evaluacion),
        'asignatura':      str(nota.asignatura),
        'alumno':          str(nota.alumno.nombre_completo),
        'ingresado_por':   str(nota.ingresado_por) if nota.ingresado_por else None,
    }


def snapshot_anotacion(anotacion):
    """Genera un diccionario con el estado actual de una Anotación."""
    return {
        'tipo':        anotacion.tipo,
        'categoria':   anotacion.categoria,
        'descripcion': anotacion.descripcion,
        'fecha':       str(anotacion.fecha),
        'asignatura':  str(anotacion.asignatura) if anotacion.asignatura else None,
        'alumno':      str(anotacion.alumno.nombre_completo),
        'creado_por':  str(anotacion.creado_por) if anotacion.creado_por else None,
    }


def registrar_cambio_nota(nota_antes, nota_despues, usuario, accion='edicion'):
    """Registra un cambio en el historial para una Nota."""
    HistorialCambio.objects.create(
        modelo             = HistorialCambio.MODELO_NOTA,
        objeto_id          = nota_antes['_id'],
        accion             = accion,
        modificado_por     = usuario,
        descripcion_objeto = nota_antes.get('_descripcion', ''),
        datos_antes        = {k: v for k, v in nota_antes.items() if not k.startswith('_')},
        datos_despues      = nota_despues,
    )


def registrar_cambio_anotacion(anotacion_antes, anotacion_despues, usuario, accion='edicion'):
    """Registra un cambio en el historial para una Anotación."""
    HistorialCambio.objects.create(
        modelo             = HistorialCambio.MODELO_ANOTACION,
        objeto_id          = anotacion_antes['_id'],
        accion             = accion,
        modificado_por     = usuario,
        descripcion_objeto = anotacion_antes.get('_descripcion', ''),
        datos_antes        = {k: v for k, v in anotacion_antes.items() if not k.startswith('_')},
        datos_despues      = anotacion_despues,
    )
