"""
APP: notas
ARCHIVO: signals.py

Signals de Django para recalcular promedios automáticamente.

Los signals son "hooks" que se ejecutan automáticamente cuando
ocurre algo en la base de datos (guardar, eliminar un registro).

Aquí: cada vez que se crea/edita/elimina una Nota,
recalculamos el PromedioAsignatura correspondiente.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Nota, PromedioAsignatura


@receiver(post_save, sender=Nota)
def recalcular_promedio_al_guardar(sender, instance, **kwargs):
    """
    Se ejecuta DESPUÉS de guardar una Nota (create o update).
    Recalcula el PromedioAsignatura para ese alumno + asignatura.
    """
    PromedioAsignatura.recalcular(instance.alumno, instance.asignatura)


@receiver(post_delete, sender=Nota)
def recalcular_promedio_al_eliminar(sender, instance, **kwargs):
    """
    Se ejecuta DESPUÉS de eliminar una Nota.
    Recalcula el promedio sin la nota eliminada.
    """
    PromedioAsignatura.recalcular(instance.alumno, instance.asignatura)
