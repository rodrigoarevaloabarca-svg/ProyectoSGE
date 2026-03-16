(function () {
    "use strict";

    /* ════════════════════════════════════════
       1. TOGGLE MOSTRAR / OCULTAR CONTRASEÑA
          Compatible con múltiples campos de
          contraseña en la misma página
          (ej: contraseña + confirmar contraseña)
       ════════════════════════════════════════ */

    /**
     * Registra el toggle en un par (input + botón).
     * @param {string} inputId   - id del <input type="password">
     * @param {string} iconId    - id del <span> del ícono (material symbol)
     */
    function initPasswordToggle(inputId, iconId) {
        var input = document.getElementById(inputId);
        var icon  = document.getElementById(iconId);
        if (!input || !icon) return;

        // El botón padre del ícono recibe el click
        var btn = icon.closest("button");
        if (!btn) return;

        btn.addEventListener("click", function () {
            var isHidden = input.type === "password";
            input.type       = isHidden ? "text" : "password";
            icon.textContent = isHidden ? "visibility_off" : "visibility";
            btn.setAttribute("aria-label", isHidden ? "Ocultar contraseña" : "Mostrar contraseña");
        });
    }

    // Campos estándar de Django auth
    initPasswordToggle("id_password",         "toggle-icon");
    initPasswordToggle("id_password1",        "toggle-icon-1");
    initPasswordToggle("id_password2",        "toggle-icon-2");
    initPasswordToggle("id_new_password1",    "toggle-icon-new1");
    initPasswordToggle("id_new_password2",    "toggle-icon-new2");
    initPasswordToggle("id_old_password",     "toggle-icon-old");


    /* ════════════════════════════════════════
       2. FORMATO AUTOMÁTICO DE RUT CHILENO
          Formatea mientras el usuario escribe:
          "123456789"  →  "12.345.678-9"
       ════════════════════════════════════════ */
    function formatRut(value) {
        // Elimina todo lo que no sea dígito o 'k/K'
        var clean = value.replace(/[^0-9kK]/g, "").toUpperCase();
        if (clean.length < 2) return clean;

        var body = clean.slice(0, -1);
        var dv   = clean.slice(-1);

        // Agrega puntos cada 3 dígitos desde la derecha
        body = body.replace(/\B(?=(\d{3})+(?!\d))/g, ".");

        return body + "-" + dv;
    }

    var rutInputs = document.querySelectorAll(
        "input[name='rut'], input[id*='rut'], input[placeholder*='RUT'], input[placeholder*='rut']"
    );

    rutInputs.forEach(function (input) {
        input.addEventListener("input", function () {
            var pos   = input.selectionStart;
            var prev  = input.value.length;
            input.value = formatRut(input.value);
            // Reajusta cursor para no saltar al final mientras se escribe
            var diff  = input.value.length - prev;
            input.setSelectionRange(pos + diff, pos + diff);
        });

        // Al salir del campo, valida el dígito verificador
        input.addEventListener("blur", function () {
            input.value = formatRut(input.value);
        });
    });


    /* ════════════════════════════════════════
       3. MENSAJES FLASH — fallback
          (navbar.js ya lo maneja; esto es por
          si este template no carga navbar.js)
       ════════════════════════════════════════ */
    document.querySelectorAll(".flash-message").forEach(function (msg) {
        // Auto-cierra en 5 s
        setTimeout(function () {
            msg.style.transition = "opacity 0.5s ease, max-height 0.4s ease";
            msg.style.opacity    = "0";
            msg.style.maxHeight  = "0";
            msg.style.overflow   = "hidden";
            setTimeout(function () { msg.remove(); }, 500);
        }, 5000);

        // Botón ✕ manual
        var closeBtn = msg.querySelector(".flash-close");
        if (closeBtn) {
            closeBtn.addEventListener("click", function () {
                msg.style.transition = "opacity 0.3s ease";
                msg.style.opacity    = "0";
                setTimeout(function () { msg.remove(); }, 300);
            });
        }
    });

})();
