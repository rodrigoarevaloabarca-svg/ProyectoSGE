"""APP: notas - apps.py - Registra los signals al iniciar Django."""
from django.apps import AppConfig


class NotasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notas'
    verbose_name = 'Gestión de Notas'

    def ready(self):
        """
        Este método se ejecuta cuando Django inicia.
        Importamos los signals aquí para que se registren correctamente.
        """
        import notas.signals  # noqa: F401
