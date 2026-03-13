# 🏫 SGE — Sistema de Gestión Escolar

Sistema de gestión escolar desarrollado con **Django** para colegios chilenos.  
Permite administrar alumnos, profesores, cursos, notas, asistencia, anotaciones e informes PDF.

---

## 📋 Características principales

- **Multi-rol**: Admin, Profesor, Apoderado, Alumno (cada uno con su propio dashboard).
- **Gestión académica**: Cursos, asignaturas, libro de notas con promedios automáticos.
- **Asistencia**: Toma de asistencia por asignatura con historial y estadísticas.
- **Anotaciones**: Registro de conducta positiva/negativa por alumno.
- **Informes PDF** (generados con ReportLab):
  - Individual por alumno y período.
  - Ranking por curso.
  - Informe de fin de año (aprobado/promovido).
  - Impresión masiva por curso.
- **Diseño**: Dark mode con Tailwind CSS y Breadcrumb de navegación en todo el sitio.
- **Localización**: Escala de notas chilena (1.0 – 7.0) y soporte para validación de RUT.

---

## 🛠️ Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Backend | Python · Django |
| Base de datos | SQLite (desarrollo) |
| Frontend | Tailwind CSS (CDN) · Material Symbols |
| PDF | ReportLab · pypdf |
| Fuentes | Lexend (Google Fonts) |

---

## ⚙️ Instalación y configuración local

### 1. Clonar el repositorio y crear entorno virtual

```bash
git clone https://github.com/rodrigoarevaloabarca-svg/ProyectoSGE.git
cd ProyectoSGE
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
 python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

Rol	Nivel de Acceso			
admin	Acceso total — gestión completa del sistema y centro de informes.			
profesor	Sus cursos y asignaturas, notas, asistencia e informes.			
apoderado	Dashboard con información exclusiva de sus pupilos.			
alumno	Visualización de sus notas, asistencia y anotaciones.			

📄 Generación de informes PDF
Para que la generación de informes funcione correctamente:

Deben existir Períodos académicos creados en la ruta /informes/periodos/ (Ej: Trimestres o Semestres).

El logo del colegio debe estar ubicado exactamente en: media/logo_colegio.png.


🤝 Contribuir
Haz un Fork del proyecto.

Crea tu rama: git checkout -b feature/nueva-funcionalidad

Haz Commit: git commit -m 'feat: agregar nueva funcionalidad'

Haz Push: git push origin feature/nueva-funcionalidad

Abre un Pull Request

📜 Licencia y Contacto
Licencia: MIT License — ver archivo LICENSE para detalles.

Contacto: Rodrigo Arévalo — Rodrigoarevaloabarca@gmail.com

Ubicación: Rancagua, Chile 🇨🇱