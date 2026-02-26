import datetime
import urllib.parse
import json

def generar_maqueta_v2(datos):
    """
    Genera el HTML/CSS para la Versión 2 (Diseño con Menú Lateral / Dark Mode).
    [MAQUETA 2]
    [EN CONSTRUCCIÓN]
    """
    # Desempaquetar datos para facilitar uso
    nombre_negocio = datos["nombre_negocio"]
    paleta = datos["paleta"]
    url_logo = datos["url_logo"]
    url_fondo_css = datos["url_fondo_css"]
    titulo_hero = datos["titulo_hero"]
    lema_hero = datos["lema_hero"]
    cta_button_link = datos["cta_button_link"]
    cta_button_text = datos["cta_button_text"]
    descripcion_presentacion = datos["descripcion_presentacion"]
    beneficios = datos["beneficios"]
    comentarios_html = datos["comentarios_html"]
    wa_link = datos["wa_link"]
    has_instagram = datos["has_instagram"]
    instagram_url = datos["instagram_url"]
    has_facebook = datos["has_facebook"]
    facebook_url = datos["facebook_url"]
    direccion = datos["direccion"]
    horarios_detallados = datos["horarios_detallados"]
    open_status_text = datos["open_status_text"]
    next_time_info = datos["next_time_info"]


    # Lógica específica de V2 para secciones HTML
    beneficios_html = ""
    if beneficios:
        beneficios_html = '<section id="beneficios" class="seccion-beneficios"><h2 class="el-messiri">Por qué elegirnos</h2><div class="contenedor-tarjetas">'
        for beneficio in beneficios:
            beneficios_html += f'<article class="tarjeta-producto tarjeta-beneficio"><h3 class="libre-baskerville">✓ {beneficio}</h3></article>'
        beneficios_html += '</div></section>'

    facebook_svg = '<svg fill="currentColor" role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><title>Facebook</title><path d="M22.675 0h-21.35C.593 0 0 .593 0 1.325v21.351C0 23.407.593 24 1.325 24H12.82v-9.294H9.692v-3.622h3.128V8.413c0-3.1 1.893-4.788 4.659-4.788 1.325 0 2.463.099 2.795.143v3.24l-1.918.001c-1.504 0-1.795.715-1.795 1.763v2.313h3.587l-.467 3.622h-3.12V24h6.116c.732 0 1.323-.593 1.323-1.325V1.325C24 .593 23.407 0 22.675 0z"/></svg>'
    instagram_svg = '<svg fill="currentColor" role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" fill-rule="evenodd"><title>Instagram</title><path d="M12 0C8.74 0 8.333.015 7.053.072 5.775.132 4.905.333 4.14.63c-.789.306-1.459.717-2.126 1.384S.936 3.35.63 4.14C.333 4.905.131 5.775.072 7.053.012 8.333 0 8.74 0 12s.015 3.667.072 4.947c.06 1.277.261 2.148.558 2.913.306.788.717 1.459 1.384 2.126.667.666 1.336 1.079 2.126 1.384.766.296 1.636.499 2.913.558C8.333 23.988 8.74 24 12 24s3.667-.015 4.947-.072c1.277-.06 2.148-.262 2.913-.558.788-.306 1.459-.718 2.126-1.384.666-.667 1.079-1.335 1.384-2.126.296-.765.499-1.636.558-2.913.06-1.28.072-1.687.072-4.947s-.015-3.667-.072-4.947c-.06-1.277-.262-2.149-.558-2.913-.306-.789-.718-1.459-1.384-2.126C21.314.936 20.644.523 19.854.218 19.095-.08 18.225-.282 16.947-.341 15.667-.398 15.26-.413 12-.413h0zm0 2.163c3.204 0 3.584.012 4.85.07 1.17.055 1.805.249 2.227.415.562.217.96.477 1.382.896.419.42.679.819.896 1.381.164.422.36 1.057.413 2.227.057 1.266.07 1.646.07 4.85s-.012 3.584-.07 4.85c-.055 1.17-.249 1.805-.413 2.227-.217.562-.477.96-.896 1.382-.42.419-.819.679-1.381.896-.422.164-1.057.36-2.227.413-1.266.057-1.646.07-4.85.07s-3.584-.012-4.85-.07c-1.17-.055-1.805-.249-2.227-.413-.562-.217-.96-.477-1.382-.896-.419-.42-.679-.819-.896-1.381-.164-.422-.36-1.057-.413-2.227-.057-1.266-.07-1.646-.07-4.85s.012-3.584.07-4.85c.055-1.17.249-1.805.413-2.227.217-.562.477.96.896-1.382.42-.419.819.679 1.381-.896.422-.164 1.057.36 2.227-.413 1.266-.057 1.646-.07 4.85.07zM12 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.88 1.44 1.44 0 000-2.88z"/></svg>'              
    
    donde_estamos_html = ""
    if direccion:
        map_link = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(direccion)}"
        donde_estamos_html = f'''
         <section id="ubicacion" class="seccion-ubicacion">
            <h2 class="el-messiri">Dónde Estamos</h2>
            <p style="max-width: 800px; margin: 0 auto; font-size: 1.2rem;">{direccion}</p>
            <a href="{map_link}" target="_blank" class="cta-button" style="margin-top: 1.5rem;">VER EN MAPA</a>
        </section>
        '''

    current_year = datetime.date.today().year
    instagram_icon_html = f'<a href="{instagram_url}" target="_blank" class="social-icon instagram active-link" aria-label="Instagram">{instagram_svg}</a>' if has_instagram else f'<a href="javascript:void(0);" class="social-icon instagram" aria-label="Instagram no disponible">{instagram_svg}</a>'
    facebook_icon_html = f'<a href="{facebook_url}" target="_blank" class="social-icon facebook active-link" aria-label="Facebook">{facebook_svg}</a>' if has_facebook else f'<a href="javascript:void(0);" class="social-icon facebook" aria-label="Facebook no disponible">{facebook_svg}</a>'

    footer_html = f"""
    <footer id="contacto" style="background: #181818; padding: 4rem 2rem; text-align: center; color: #aaa; font-size: 0.9rem;">
        <h2 class="el-messiri" style="color: white; margin-bottom: 2rem;">Contacto y Redes Sociales</h2>
        <div class="social-icons">
            {instagram_icon_html}
            {facebook_icon_html}
        </div>
        <p style="margin-top: 2rem;">&copy; {current_year} {nombre_negocio}. Todos los derechos reservados.</p>
    </footer>
    """

    CSS_V2 = f"""
    :root {{
        /* --- SISTEMA DE COLORES SEMÁNTICO (Reestructuración V2) --- */
        
        /* Botones (CTA y Navegación) */
        --color-fondo-botones: {paleta.get('fondo_botones', paleta['primario'])};
        --color-fondo-botones-hover: {paleta.get('fondo_botones_hover', paleta.get('acento', '#4f4d4d'))};
        --color-texto-botones: {paleta.get('texto_botones', paleta['texto_inverso'])};
        --color-texto-botones-hover: {paleta.get('texto_botones_hover', paleta['texto_inverso'])};

        /* Textos Generales */
        --color-texto-general: {paleta.get('texto_general', paleta['texto'])};
        --color-texto-hero: {paleta.get('texto_hero', '#ffffff')}; /* El hero siempre tiene fondo oscuro/imagen */
        --color-texto-cards: {paleta.get('texto_cards', paleta['texto_inverso'])}; /* Solicitado explícitamente */
        
        /* Títulos */
        --color-titulos: {paleta.get('titulos', paleta['primario'])}; /* Para detalles, iconos o subtítulos destacados */
        --color-titulo-h1: {paleta.get('titulo_h1', '#ffffff')}; /* Título principal en Hero */
        --color-titulo-h2: {paleta.get('titulo_h2', paleta['texto'])}; /* Títulos de secciones */

        /* Fondos y Estructura */
        --color-fondo-general: {paleta.get('fondo_general', paleta['fondo'])};
        --color-fondo-cards: {paleta.get('fondo_cards', paleta.get('fondo_tarjeta', '#ffffff'))};
        --color-overlay-hero: {paleta.get('overlay_hero', paleta['overlay'])};
        --color-borde-sutil: {paleta.get('borde_sutil', '#838383')};

        /* Fuentes (de las instrucciones) */
        --fuente-base: 'El Messiri', 'Georgia', sans-serif;
        --fuente-secundaria: 'Libre Baskerville', serif;

        /* Tamaños de Fuente (de las instrucciones) */
        --font-size-xxs: 0.875rem;
        --font-size-xs: 1rem;
        --font-size-sm: 1.25rem;
        --font-size-md: 1.5rem;
        --font-size-lg: 1.75rem;
        --font-size-xl: 2.5rem;
        --font-size-xxl: 3.5rem;

        /* Espaciados (de las instrucciones) */
        --espaciado-sm: 1rem;
        --espaciado-md: 1.5rem;
        --espaciado-lg: 2rem;
        --espaciado-xl: 4rem;

        /* Utilidades */
        --transicion-estandar: all 0.3s ease;
        --radio-card: 0.75rem;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; }}
    body {{ font-family: var(--fuente-base); background-color: var(--color-fondo-general); color: var(--color-texto-general); line-height: 1.6; }}
    img {{ max-width: 100%; height: auto; display: block; }}
    h1, h2, h3 {{ font-family: var(--fuente-secundaria); text-shadow: 0 1px 3px rgba(0,0,0,0.4); }}
    
    /* --- Barra de Navegación (Extraída de la web de ejemplo) --- */
    #nav {{ 
        position: fixed; 
        top: 0; 
        width: 100%; 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        padding: 15px 2%; 
        transition: top 0.5s ease-in-out, background-color 0.3s; 
        background-color: var(--color-fondo-general); 
        box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
        height: 85px;
        z-index: 1000;
    }}
    .logo {{ transition: transform 0.5s ease; }}
    .logo img {{ height: 60px; width: auto; transition: transform 0.3s; display: block; }}
    .nav-links {{ list-style: none; display: flex; gap: 2rem; }}
    .nav-links a {{ color: var(--color-texto-general); text-decoration: none; font-weight: 500; font-size: 1.2rem; transition: color 0.3s; padding: 10px; }}
    .nav-links a:hover {{ color: var(--color-titulos); }}
    .btn button {{ background-color: var(--color-fondo-botones); color: var(--color-texto-botones); border: none; padding: 0.75rem 1.5rem; border-radius: 5px; cursor: pointer; font-weight: bold; transition: background-color 0.3s; }}
    .btn button:hover {{ background-color: var(--color-fondo-botones-hover); color: var(--color-texto-botones-hover); }}
    .menu-hamburguesa {{ display: none; }}
    .overlay {{ height: 100%; width: 0; position: fixed; z-index: 1001; top: 0; left: 0; background-color: rgba(0,0,0, 0.95); overflow-x: hidden; transition: 0.5s; }}
    .overlay-content {{ position: relative; top: 25%; width: 100%; text-align: center; margin-top: 30px; }}
    .overlay a {{ padding: 8px; text-decoration: none; font-size: 36px; color: #818181; display: block; transition: 0.3s; }}
    .overlay a:hover, .overlay a:focus {{ color: var(--color-titulos); }}
    .overlay .close {{ position: absolute; top: 20px; right: 45px; font-size: 60px; }}

    /* --- Secciones Principales --- */
    main {{ }} /* El padding se quita para que el hero ocupe todo el top */
    .seccion-hero {{ 
        position: relative;
        width: 100%;
        text-align: center; 
        padding: 11em 2rem 1rem;
        min-height: 80vh; 
        display: flex; 
        flex-direction: column; 
        justify-content: center; 
        align-items: center; 
        background: linear-gradient(var(--color-overlay-hero), #00000073), url('{url_fondo_css}');
        background-size: cover;
        background-position: center;
        color: var(--color-texto-hero);
    }}
    .seccion-hero h1 {{ font-size: 3.5rem; color: var(--color-titulo-h1); }}
    .seccion-presentacion {{ padding: 4rem 2rem; text-align: center; }}
    .seccion-beneficios, .seccion-productos {{ padding: 4rem 2rem; text-align: center; }}
    .seccion-ubicacion {{ padding: 4rem 2rem; text-align: center; }}
    .seccion-presentacion h2, .seccion-beneficios h2, .seccion-productos h2, .seccion-ubicacion h2 {{ margin-bottom: 2rem; font-size: 2.5rem; color: var(--color-titulo-h2); }}
    .cta-button {{ background-color: var(--color-fondo-botones); color: var(--color-texto-botones); padding: 0.75rem 1.5rem; border-radius: 5px; text-decoration: none; font-weight: 600; display: inline-block; margin-top: 1.5rem; transition: all 0.3s; }}
    .cta-button:hover {{ background-color: var(--color-fondo-botones-hover); color: var(--color-texto-botones-hover); transform: scale(1.05); }}

    /* Testimonios y Tarjetas (Reutilizados de V1 con estilo oscuro) */
    .contenedor-tarjetas {{ display: grid; grid-template-columns: 1fr; gap: 1.5rem; max-width: 1200px; margin: 0 auto; }}
    .tarjeta-testimonio {{ background: var(--color-fondo-cards); border-radius: 0.75rem; padding: 2rem; display: flex; flex-direction: column; align-items: center; text-align: center; color: var(--color-texto-cards); border: 1px solid var(--color-borde-sutil); box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: all 0.3s ease; position: relative; }}
    .tarjeta-testimonio:hover {{ transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.2); }}
    .tarjeta-testimonio img {{ width: 6rem; height: 6rem; border-radius: 50%; object-fit: cover; border: 3px solid var(--color-titulos); margin-bottom: 1rem; }}
    .comillas-testimonio {{ font-size: 4rem; line-height: 0.5; font-family: serif; color: var(--color-titulos); opacity: 0.8; }}
    .texto-testimonio {{ font-style: italic; margin-bottom: 1rem; font-size: 1.1rem; }}
    .estrellas-testimonio {{ color: #FFD700; margin-bottom: 0.5rem; }}
    .autor-testimonio {{ font-weight: bold; font-size: 1rem; text-transform: uppercase; }}
    .tarjeta-beneficio {{ background: var(--color-fondo-cards); color: var(--color-texto-cards); text-align: center; padding: 2rem 1rem; border-radius: 1rem; border: 1px solid var(--color-borde-sutil); box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: all 0.3s ease; }}
    .tarjeta-beneficio:hover {{ transform: translateY(-5px); box-shadow: 0 8px 15px rgba(0,0,0,0.1); }}

    /* --- Footer y Redes --- */
    .social-icons {{ display: flex; justify-content: center; gap: 2rem; }}
    .social-icon svg {{ width: 40px; height: 40px; transition: var(--transicion-estandar); }}
    .social-icon.instagram {{ color: #E1306C; }}
    .social-icon.facebook {{ color: #1877F2; }}
    .social-icon.active-link:hover svg {{ transform: scale(1.1); }}
    .social-icon:not(.active-link) {{ cursor: default; opacity: 0.5; }}
    .posicion-fixed {{ position: fixed; bottom: 2rem; right: 2rem; z-index: 1000; }}

    /* --- Responsive --- */
    @media screen and (max-width: 768px) {{
        .nav-links, .btn {{ display: none; }}
        .menu-hamburguesa {{ display: block; }}
    }}
    @media (min-width: 769px) {{
        .contenedor-tarjetas {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    @media (min-width: 1201px) {{
        .contenedor-tarjetas {{ grid-template-columns: repeat(3, 1fr); }}
    }}
    """

    html_final = f"""
    <!DOCTYPE html> <!-- MAQUETA V2 -->
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{nombre_negocio} | Oficial</title>
        <meta name="robots" content="noindex, nofollow">
        <style>{CSS_V2}</style>
        <link href="https://fonts.googleapis.com/css2?family=El+Messiri:wght@400;700&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
    </head>
    <body>
        <nav id="nav" class="menu-principal">
            <div id="logo" class="logo">
                <img src="{url_logo}" alt="Logo de {nombre_negocio}">
            </div>
            <ul class="nav-links">
                <li><a href="#hero" class="normal">Inicio</a></li>
                <li><a href="#beneficios" class="normal">Beneficios</a></li>
                <li><a href="#testimonios" class="normal">Testimonios</a></li>
            </ul>
            <a href="#contacto" class="btn"><button>Contacto</button></a>
            <a onclick="openNav()" class="menu-hamburguesa" href="#"><button><img src="https://upload.wikimedia.org/wikipedia/commons/b/b2/Hamburger_icon.svg" width="40" height="40" alt="Menú"></button></a>
            <div class="overlay" id="menu-movil">
                <a onclick="closeNav()" class="close normal" href="#">&times;</a>
                <div class="overlay-content">
                    <a onclick="closeNav()" class="normal" href="#hero">Inicio</a>
                    <a onclick="closeNav()" class="normal" href="#beneficios">Beneficios</a>
                    <a onclick="closeNav()" class="normal" href="#testimonios">Testimonios</a>
                    <a onclick="closeNav()" class="normal" href="#contacto">Contacto</a>
                </div>
            </div>
        </nav>

        <main>
            <section id="hero" class="seccion-hero">
                <h1 class="el-messiri" style="text-transform: capitalize;">{nombre_negocio}</h1>
                <p style="font-size: 1.5rem; margin-top: 0.5rem; font-weight: 300;">{lema_hero}</p>
                <a href="{cta_button_link}" class="cta-button">{cta_button_text}</a>
                <p style="font-size: 2rem; margin-top: 20vh;margin-bottom: 0.5rem; font-weight: 700;">{titulo_hero}</p>
            </section>

            <section id="sobre-nosotros" class="seccion-ubicacion">
                <h2 class="libre-baskerville">Sobre Nosotros</h2>
                <p style="max-width: 800px; margin: 0 auto 5rem; font-size: 1.2rem;">{descripcion_presentacion}</p>
                
                <!-- NUEVO: Sección de Horarios (Implementación V2) -->
                <div style="margin-top: 2rem; padding-top: 5.5rem; border-top: 1px solid var(--color-borde-sutil);">
                    <h3 class="libre-baskerville" style="font-size: 2rem; margin-bottom: 1rem;">Horarios</h3>
                    <p id="estado-horario" style="font-weight: bold; font-size: 1.5rem; color: var(--color-titulos); margin-bottom: 0.5rem;">{open_status_text}</p>
                    <p id="proximo-horario" style="font-size: 1.2rem; margin-bottom: 1.5rem;">{next_time_info}</p>
                    
                    <!-- Horarios detallados -->
                    <div style="font-size: 1.1rem; color: var(--color-texto-general); opacity: 0.9;">
                        {''.join([f'<p>{h}</p>' for h in horarios_detallados]) if horarios_detallados else '<p>Horarios no especificados.</p>'}
                    </div>
                </div>
            </section>

            {beneficios_html}

            <section id="testimonios" class="seccion-productos">
                <h2 class="el-messiri">Experiencias de nuestros clientes</h2>
                <div class="contenedor-tarjetas">{comentarios_html}</div>
            </section>

            {donde_estamos_html}
        </main>

        <a href="{wa_link}" class="posicion-fixed" aria-label="Contactar por WhatsApp">
            <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="50" height="50">
        </a>

        {footer_html}

        <script src="js/main.js"></script>
        <script src="js/scroll.js"></script>
        <script>
        (function() {{
            const horarios = {json.dumps(horarios_detallados)};
            const statusEl = document.getElementById('estado-horario');
            const nextEl = document.getElementById('proximo-horario');
            
            if (!statusEl || !horarios || horarios.length === 0) return;

            const diasSemana = ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado'];
            const now = new Date();
            const diaActual = now.getDay(); // 0-6
            const minutosActuales = now.getHours() * 60 + now.getMinutes();

            // Parsear horarios
            const agenda = {{}};
            
            horarios.forEach(h => {{
                const partes = h.split(': ');
                if (partes.length < 2) return;
                
                let diaNombre = partes[0].toLowerCase().trim();
                // Normalizar nombres
                diaNombre = diaNombre.replace('é', 'e').replace('á', 'a');
                if (diaNombre === 'miercoles') diaNombre = 'miércoles';
                if (diaNombre === 'sabado') diaNombre = 'sábado';

                const rangosStr = partes[1];
                if (rangosStr.toLowerCase().includes('cerrado')) return;

                const diaIndex = diasSemana.indexOf(diaNombre);
                if (diaIndex === -1) return;

                const rangos = [];
                rangosStr.split(', ').forEach(r => {{
                    const [inicio, fin] = r.split('-');
                    if (inicio && fin) {{
                        const [h1, m1] = inicio.split(':').map(Number);
                        const [h2, m2] = fin.split(':').map(Number);
                        rangos.push({{
                            inicio: h1 * 60 + m1,
                            fin: h2 * 60 + m2
                        }});
                    }}
                }});
                agenda[diaIndex] = rangos.sort((a, b) => a.inicio - b.inicio);
            }});

            function formatearHora(minutos) {{
                const h = Math.floor(minutos / 60).toString().padStart(2, '0');
                const m = (minutos % 60).toString().padStart(2, '0');
                return `${{h}}:${{m}}`;
            }}

            // Determinar estado
            let estaAbierto = false;
            let textoEstado = "Cerrado";
            let textoProximo = "";
            let color = "#dc3545"; // Rojo

            const rangosHoy = agenda[diaActual] || [];
            let cierreHoy = null;

            for (const rango of rangosHoy) {{
                if (minutosActuales >= rango.inicio && minutosActuales < rango.fin) {{
                    estaAbierto = true;
                    cierreHoy = rango.fin;
                    break;
                }}
            }}

            if (estaAbierto) {{
                textoEstado = "Abierto ahora";
                color = "#28a745"; // Verde
                textoProximo = `Cierra a las ${{formatearHora(cierreHoy)}}`;
            }} else {{
                // Buscar próxima apertura
                let encontrado = false;
                // 1. Resto de hoy
                for (const rango of rangosHoy) {{
                    if (minutosActuales < rango.inicio) {{
                        textoProximo = `Abre hoy a las ${{formatearHora(rango.inicio)}}`;
                        encontrado = true;
                        break;
                    }}
                }}
                // 2. Días siguientes
                if (!encontrado) {{
                    for (let i = 1; i <= 7; i++) {{
                        const diaCheck = (diaActual + i) % 7;
                        const rangosCheck = agenda[diaCheck];
                        if (rangosCheck && rangosCheck.length > 0) {{
                            const diaNombre = i === 1 ? "mañana" : "el " + diasSemana[diaCheck];
                            textoProximo = `Abre ${{diaNombre}} a las ${{formatearHora(rangosCheck[0].inicio)}}`;
                            encontrado = true;
                            break;
                        }}
                    }}
                }}
                if (!encontrado) textoProximo = "Horarios no disponibles";
            }}

            statusEl.textContent = textoEstado;
            statusEl.style.color = color;
            if (nextEl) nextEl.textContent = textoProximo;
        }})();
        </script>
    </body>
    </html>
    """
    
    return html_final