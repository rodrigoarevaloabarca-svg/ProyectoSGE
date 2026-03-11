// Configuración de Tailwind CSS
tailwind.config = {
    darkMode: "class",
    theme: {
        extend: {
            colors: {
                "primary": "#135bec",
                "background-light": "#f6f6f8",
                "background-dark": "#101622",
                "navy-deep": "#0d121b",
                "soft-grey": "#e7ebf3",
                "muted-blue": "#4c669a"
            },
            fontFamily: {
                "display": ["Lexend", "sans-serif"]
            },
            borderRadius: {
                "DEFAULT": "0.25rem",
                "lg": "0.5rem",
                "xl": "0.75rem",
                "full": "9999px"
            },
        },
    },
}

// Aquí podrías añadir lógica interactiva en el futuro,
// como el cambio de modo oscuro o manejo de eventos.