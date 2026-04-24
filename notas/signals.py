"""
APP: notas
ARCHIVO: signals.py

Signals para recalcular promedios automáticamente al guardar/eliminar notas.
"""
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from .models import Nota, PromedioAsignatura

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Nota)
def recalcular_promedio_al_guardar(sender, instance, **kwargs):
    """Se ejecuta después de guardar una Nota (create o update)."""
    try:
        with transaction.atomic():
            PromedioAsignatura.recalcular(instance.alumno, instance.asignatura)
    except Exception as e:
        logger.error(
            "Error recalculando promedio tras guardar Nota %s: %s",
            instance.pk, e, exc_info=True
        )


@receiver(post_delete, sender=Nota)
def recalcular_promedio_al_eliminar(sender, instance, **kwargs):
    """Se ejecuta después de eliminar una Nota."""
    try:
        with transaction.atomic():
            PromedioAsignatura.recalcular(instance.alumno, instance.asignatura)
    except Exception as e:
        logger.error(
            "Error recalculando promedio tras eliminar Nota %s: %s",
            instance.pk, e, exc_info=True
        )
