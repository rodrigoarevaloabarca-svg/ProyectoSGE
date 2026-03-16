/**
 * config.js — SGE
 * Configuración global de Tailwind CSS.
 * ÚNICA fuente de verdad para colores y tema.
 * Cargar ANTES del CDN de Tailwind en base.html y loginbase.html:
 *   <script src="{% static 'js/config.js' %}"></script>
 *   <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
 */
tailwind.config = {
    darkMode: "class",
    theme: {
        extend: {
            colors: {
                "primary":          "#197fe6",
                "background-light": "#f6f7f8",
                "background-dark":  "#111921",
                "navy-deep":        "#0d1b2a",
                "muted-blue":       "#6b7fa3",
                "soft-grey":        "#e2e8f0",
            },
            fontFamily: {
                "display": ["Lexend", "sans-serif"]
            },
            borderRadius: {
                "DEFAULT": "0.25rem",
                "lg":      "0.5rem",
                "xl":      "0.75rem",
                "full":    "9999px",
            },
        },
    },
};
