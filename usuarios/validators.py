"""
Validadores reutilizables para el proyecto SGE.
Pueden usarse tanto en formularios como en campos de modelo.
"""
from django.core.exceptions import ValidationError


def _calcular_dv_rut(cuerpo: int) -> str:
    suma, multiplo = 0, 2
    while cuerpo:
        suma    += (cuerpo % 10) * multiplo
        cuerpo  //= 10
        multiplo = 2 if multiplo == 7 else multiplo + 1
    resultado = 11 - (suma % 11)
    if resultado == 10:
        return 'k'
    if resultado == 11:
        return '0'
    return str(resultado)


def validar_rut(value):
    """
    Valida que el RUT chileno tenga formato correcto y dígito verificador válido.
    Acepta formatos: '12345678-9', '12.345.678-9', '12345678-k'.
    Lanza ValidationError si el RUT es inválido.
    """
    rut_limpio = value.replace('.', '').replace(' ', '').strip().lower()
    if '-' not in rut_limpio:
        raise ValidationError('El RUT debe tener el formato 12345678-9.')
    try:
        cuerpo_str, dv = rut_limpio.split('-')
        cuerpo = int(cuerpo_str)
    except (ValueError, AttributeError):
        raise ValidationError('El RUT no tiene un formato válido.')
    if _calcular_dv_rut(cuerpo) != dv:
        raise ValidationError('El dígito verificador del RUT es incorrecto.')


def validar_nota(value):
    """
    Valida que una nota esté en la escala chilena 1.0–7.0 con máximo 1 decimal.
    """
    try:
        valor = float(value)
    except (TypeError, ValueError):
        raise ValidationError('La nota debe ser un número.')
    if valor < 1.0 or valor > 7.0:
        raise ValidationError('La nota debe estar entre 1.0 y 7.0.')
    if round(valor, 1) != valor:
        raise ValidationError('La nota puede tener máximo 1 decimal.')
