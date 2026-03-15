/* ============================================================
   navbar.js — SGE · Menú móvil + Dark Mode persistente
   Colocar en: static/js/navbar.js
   Cargar con: <script src="{% static 'js/navbar.js' %}" defer></script>

   IMPORTANTE: El bloque anti-FOUC que va en el <head> del
   base.html NO va aquí porque debe ejecutarse de forma síncrona
   antes de que el DOM pinte (ver base.html).
   ============================================================ */

(function () {
    "use strict";

    /* ════════════════════════════════════════
       1. DARK MODE
       ════════════════════════════════════════ */
    const DARK_KEY  = "sge-theme";   // clave en localStorage
    const htmlEl    = document.documentElement;

    /**
     * Aplica o quita la clase "dark" en <html> y
     * guarda la preferencia en localStorage.
     */
    function setTheme(dark) {
        if (dark) {
            htmlEl.classList.add("dark");
        } else {
            htmlEl.classList.remove("dark");
        }
        localStorage.setItem(DARK_KEY, dark ? "dark" : "light");
        updateDarkBtn(dark);
    }

    /**
     * Actualiza el aria-label del botón según el estado actual.
     */
    function updateDarkBtn(dark) {
        const btn = document.getElementById("dark-mode-btn");
        if (!btn) return;
        btn.setAttribute(
            "aria-label",
            dark ? "Cambiar a modo claro" : "Cambiar a modo oscuro"
        );
        btn.setAttribute("title", dark ? "Modo claro" : "Modo oscuro");
    }

    /**
     * Lee la preferencia guardada; si no existe usa el sistema.
     * Retorna true si corresponde modo oscuro.
     */
    function prefersDark() {
        const saved = localStorage.getItem(DARK_KEY);
        if (saved === "dark")  return true;
        if (saved === "light") return false;
        // Sin preferencia guardada → seguir al sistema operativo
        return window.matchMedia("(prefers-color-scheme: dark)").matches;
    }

    // Inicializa el estado al cargar la página
    // (la clase ya fue aplicada por el script inline anti-FOUC,
    //  aquí solo sincronizamos el botón)
    updateDarkBtn(htmlEl.classList.contains("dark"));

    // Click en el botón
    const darkBtn = document.getElementById("dark-mode-btn");
    if (darkBtn) {
        darkBtn.addEventListener("click", () => {
            const isDark = htmlEl.classList.contains("dark");
            setTheme(!isDark);
        });
    }

    // Si el usuario cambia el tema del SO mientras tiene la página abierta
    // y NO tiene preferencia guardada → respetamos el cambio
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
        if (!localStorage.getItem(DARK_KEY)) {
            setTheme(e.matches);
        }
    });


    /* ════════════════════════════════════════
       2. MENÚ HAMBURGUESA (móvil)
       ════════════════════════════════════════ */
    const hamburgerBtn  = document.getElementById("hamburger-btn");
    const mobileMenu    = document.getElementById("mobile-menu");
    const hamburgerIcon = document.getElementById("hamburger-icon");

    if (hamburgerBtn && mobileMenu) {

        /** Abre o cierra el menú móvil */
        function toggleMenu(force) {
            const willOpen = force !== undefined
                ? force
                : !mobileMenu.classList.contains("open");

            mobileMenu.classList.toggle("open", willOpen);
            hamburgerIcon.classList.toggle("open", willOpen);
            hamburgerBtn.setAttribute("aria-expanded", String(willOpen));

            // Bloquea el scroll del body mientras el menú está abierto
            document.body.style.overflow = willOpen ? "hidden" : "";
        }

        /** Cierra el menú (atajo) */
        function closeMenu() { toggleMenu(false); }

        // Click en el botón hamburguesa
        hamburgerBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            toggleMenu();
        });

        // Tecla Escape
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && mobileMenu.classList.contains("open")) {
                closeMenu();
                hamburgerBtn.focus();
            }
        });

        // Click fuera del header → cierra
        document.addEventListener("click", (e) => {
            const header = hamburgerBtn.closest("header");
            if (header && !header.contains(e.target)) {
                closeMenu();
            }
        });

        // Al pasar a pantalla md+ → cierra y limpia
        const mq = window.matchMedia("(min-width: 768px)");
        mq.addEventListener("change", (e) => {
            if (e.matches) {
                closeMenu();
                // Cierra también todos los submenús abiertos
                document.querySelectorAll(".mobile-submenu.open").forEach((el) => {
                    el.classList.remove("open");
                });
            }
        });

        // Cambio de orientación → limpia overflow por seguridad
        window.addEventListener("orientationchange", () => {
            document.body.style.overflow = "";
        });
    }


    /* ════════════════════════════════════════
       3. SUBMENÚS MÓVIL (acordeón)
       ════════════════════════════════════════ */
    document.querySelectorAll(".mobile-submenu-btn").forEach((trigger) => {
        trigger.addEventListener("click", () => {
            const key    = trigger.dataset.submenu;
            const target = document.getElementById("submenu-" + key);
            const arrow  = trigger.querySelector(".submenu-arrow");
            if (!target) return;

            const willOpen = !target.classList.contains("open");

            // Cierra los demás submenús abiertos (comportamiento acordeón)
            document.querySelectorAll(".mobile-submenu.open").forEach((el) => {
                if (el !== target) {
                    el.classList.remove("open");
                    const id  = el.id.replace("submenu-", "");
                    const btn = document.querySelector(`[data-submenu="${id}"]`);
                    btn?.querySelector(".submenu-arrow")?.classList.remove("rotate-180");
                }
            });

            target.classList.toggle("open", willOpen);
            arrow?.classList.toggle("rotate-180", willOpen);
        });
    });


    /* ════════════════════════════════════════
       4. MENSAJES FLASH — auto-dismiss (5 s)
       ════════════════════════════════════════ */
    document.querySelectorAll(".flash-message").forEach((msg) => {
        // Auto-cierra en 5 s con fade out
        setTimeout(() => {
            msg.style.transition = "opacity 0.5s ease, max-height 0.4s ease";
            msg.style.opacity    = "0";
            msg.style.maxHeight  = "0";
            msg.style.overflow   = "hidden";
            setTimeout(() => msg.remove(), 500);
        }, 5000);

        // Botón ✕ manual
        const closeBtn = msg.querySelector(".flash-close");
        if (closeBtn) {
            closeBtn.addEventListener("click", () => {
                msg.style.transition = "opacity 0.3s ease";
                msg.style.opacity    = "0";
                setTimeout(() => msg.remove(), 300);
            });
        }
    });

})();
