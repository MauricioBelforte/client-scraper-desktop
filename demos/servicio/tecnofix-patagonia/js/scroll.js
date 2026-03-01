
document.addEventListener("DOMContentLoaded", function() {
    /* --pocicion inicial */
    let ubicacionPrincipal = window.pageYOffset;
    let $nav = document.querySelector("nav");
    var logo = document.getElementById("logo");

    if (!$nav || !logo) return; // Evitar errores si los elementos no existen

    /* --Inicializar estado del menu para que sea visible al cargar */
    $nav.style.top = "0px";

    /* --evento scroll */
    window.addEventListener("scroll", function () {
        /* --donde nos encontramos actualmente */
        let desplazamientoActual = window.pageYOffset;

        /* --condicon para ocultar o mostrar el menu */
        if (ubicacionPrincipal >= desplazamientoActual || desplazamientoActual < 50) {
            /* --si es mayor o igual se muesta (Scroll UP) o si estamos muy arriba */
            logo.style.transform = "scale(1)";
            $nav.style.top = "0px";
        } else {
            /* --sino lo ocultamos añadiendo un top negativo (Scroll DOWN) */
            $nav.style.top = "-100px";
            logo.style.transform = "scale(0.8)";
        }

        /* --actulizamos la ubicacion principal */
        ubicacionPrincipal = desplazamientoActual;
    });
});
        