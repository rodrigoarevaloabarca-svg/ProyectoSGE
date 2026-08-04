"""
Comando de Django para la carga masiva de cuentas de Usuario únicamente (Fase 1).

Uso:
    python manage.py cargar_solo_usuarios ruta/al/archivo.csv
    python manage.py cargar_solo_usuarios ruta/al/archivo.csv --dry-run
"""

import csv
import os
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from usuarios.models import Usuario


class Command(BaseCommand):
    help = 'Carga masiva de cuentas de Usuario desde un archivo CSV (Fase 1)'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Ruta al archivo CSV con la información de los usuarios.'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula la carga sin modificar la base de datos.'
        )
        parser.add_argument(
            '--default-password',
            type=str,
            default='colegioal_2026',
            help='Contraseña predeterminada si no viene especificada en el CSV (Por defecto: colegioal_2026).'
        )

    def _obtener_valor(self, row, *nombres_posibles):
        """Busca el primer nombre de columna que coincida en la fila (insensible a mayúsculas/minúsculas)."""
        row_normalizado = {k.strip().lower(): v for k, v in row.items() if k}
        for nombre in nombres_posibles:
            nombre_lower = nombre.lower()
            if nombre_lower in row_normalizado:
                val = row_normalizado[nombre_lower]
                return val.strip() if val else None
        return None

    def handle(self, *args, **options):
        csv_filepath = options['csv_file']
        dry_run = options['dry_run']
        default_password = options['default_password']

        if not os.path.exists(csv_filepath):
            raise CommandError(f"El archivo '{csv_filepath}' no existe.")

        if dry_run:
            self.stdout.write(self.style.WARNING("=== MODO SIMULACIÓN (--dry-run ACTIVADO) ==="))
            self.stdout.write(self.style.WARNING("No se realizarán cambios reales en la base de datos.\n"))

        creados = 0
        omitidos = 0
        errores = 0

        try:
            with open(csv_filepath, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)

                # Validar headers básicos
                if not reader.fieldnames:
                    raise CommandError("El archivo CSV está vacío o no tiene encabezados válidos.")

                for line_num, row in enumerate(reader, start=2):
                    nickname = self._obtener_valor(row, 'Nickname', 'username', 'usuario')
                    nombres = self._obtener_valor(row, 'Nombres', 'first_name', 'nombre') or ''
                    apellidos = self._obtener_valor(row, 'Apellidos', 'last_name', 'apellido') or ''
                    rut = self._obtener_valor(row, 'RUT', 'rut')
                    password = self._obtener_valor(row, 'Password', 'password', 'clave') or default_password
                    rol = self._obtener_valor(row, 'Rol', 'rol') or Usuario.ROL_ALUMNO
                    email = self._obtener_valor(row, 'Email', 'email', 'correo')
                    telefono = self._obtener_valor(row, 'Telefono', 'telefono', 'celular')

                    # Limpiar rol
                    rol = rol.lower().strip()
                    roles_validos = [r[0] for r in Usuario.ROLES]
                    if rol not in roles_validos:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Línea {line_num}: Rol '{rol}' no es válido. Se asignará 'alumno'."
                            )
                        )
                        rol = Usuario.ROL_ALUMNO

                    # Determinar username
                    username = nickname
                    if not username and rut:
                        username = rut.replace('-', '').replace('.', '').strip()

                    if not username:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Línea {line_num}: Omitido por falta de Nickname/RUT ({nombres} {apellidos})."
                            )
                        )
                        omitidos += 1
                        continue

                    # Verificar existencia previa
                    if Usuario.objects.filter(username=username).exists():
                        self.stdout.write(
                            self.style.WARNING(f"Línea {line_num}: Usuario '{username}' ya existe. Omitiendo...")
                        )
                        omitidos += 1
                        continue

                    if rut and Usuario.objects.filter(rut=rut).exists():
                        self.stdout.write(
                            self.style.WARNING(f"Línea {line_num}: RUT '{rut}' ya registrado en otro usuario. Omitiendo...")
                        )
                        omitidos += 1
                        continue

                    if email and Usuario.objects.filter(email=email).exists():
                        self.stdout.write(
                            self.style.WARNING(f"Línea {line_num}: Email '{email}' ya registrado. Se ignorará el email.")
                        )
                        email = None

                    # Crear usuario
                    try:
                        with transaction.atomic():
                            user = Usuario(
                                username=username,
                                first_name=nombres,
                                last_name=apellidos,
                                rut=rut,
                                email=email,
                                telefono=telefono,
                                rol=rol
                            )
                            user.set_password(password)

                            if not dry_run:
                                user.save()

                            creados += 1
                            msg = f"[OK] Linea {line_num}: Usuario '{username}' ({nombres} {apellidos}) registrado con rol '{rol}'."
                            self.stdout.write(self.style.SUCCESS(msg))

                    except Exception as e:
                        errores += 1
                        self.stdout.write(
                            self.style.ERROR(f"[ERROR] Linea {line_num}: Error al crear usuario '{username}': {e}")
                        )

        except Exception as e:
            raise CommandError(f"Error procesando el archivo CSV: {e}")

        # Resumen
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS(f"RESUMEN DE LA CARGA (FASE 1):"))
        self.stdout.write(f"  • Creados exitosamente: {creados}")
        self.stdout.write(f"  • Omitidos (duplicados/incompletos): {omitidos}")
        self.stdout.write(f"  • Errores: {errores}")
        if dry_run:
            self.stdout.write(self.style.WARNING(" Recordatorio: Fue una SIMULACIÓN (--dry-run). Ningún dato fue guardado."))
        self.stdout.write("=" * 50 + "\n")
