"""
APP: usuarios
ARCHIVO: signals.py

Señales de seguridad: login exitoso, logout y login fallido.
Los eventos exitosos se registran en historial; los fallidos solo en el logger
(django-axes ya los persiste en su propia tabla).
"""
import logging

from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.dispatch import receiver

logger = logging.getLogger('sge.seguridad')


def _get_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '—')


@receiver(user_logged_in)
def on_login(sender, request, user, **kwargs):
    from historial.models import HistorialCambio
    from historial.utils import registrar_evento_usuario

    ip = _get_ip(request)
    logger.info('LOGIN exitoso | usuario=%s | ip=%s', user.username, ip)
    registrar_evento_usuario(
        usuario_pk=user.pk,
        accion=HistorialCambio.ACCION_LOGIN,
        datos={'ip': ip, 'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200]},
        modificado_por=user,
        descripcion=f'{user.get_full_name()} ({user.username})',
    )


@receiver(user_logged_out)
def on_logout(sender, request, user, **kwargs):
    if user is None:
        return
    from historial.models import HistorialCambio
    from historial.utils import registrar_evento_usuario

    ip = _get_ip(request)
    logger.info('LOGOUT | usuario=%s | ip=%s', user.username, ip)
    registrar_evento_usuario(
        usuario_pk=user.pk,
        accion=HistorialCambio.ACCION_LOGOUT,
        datos={'ip': ip},
        modificado_por=user,
        descripcion=f'{user.get_full_name()} ({user.username})',
    )


@receiver(user_login_failed)
def on_login_failed(sender, credentials, request, **kwargs):
    ip = _get_ip(request)
    username = credentials.get('username', '—')
    logger.warning('LOGIN FALLIDO | username="%s" | ip=%s', username, ip)
