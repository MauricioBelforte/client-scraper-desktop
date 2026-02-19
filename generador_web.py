import os
import re
import json
import urllib.parse
import datetime
import random
import requests
from src.constants import PALETAS_COLORES

def generar_y_guardar_imagen(prompt: str, ruta_guardado: str):
    """
    Genera una imagen usando Cloudflare Workers AI y la guarda en un archivo.

    Args:
        prompt (str): El prompt para la generación de la imagen.
        ruta_guardado (str): La ruta completa del archivo donde se guardará la imagen.

    Returns:
        bool: True si la imagen se generó y guardó, False en caso de error.
    """
    try:
        account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
        api_token = os.getenv("CLOUDFLARE_API_TOKEN")
        if not account_id or not api_token:
            print("[AVISO] Variables de entorno CLOUDFLARE_ACCOUNT_ID o CLOUDFLARE_API_TOKEN no encontradas. Omitiendo generación de imagen.")
            return False

        # Modelo recomendado para velocidad y calidad general.
        model = "@cf/stabilityai/stable-diffusion-xl-base-1.0"
        url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}"
        
        headers = {"Authorization": f"Bearer {api_token}"}
        payload = {"prompt": prompt}

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            with open(ruta_guardado, 'wb') as f:
                f.write(response.content)
            return True
        else:
            print(f"[ERROR] Error al generar imagen con Cloudflare ({response.status_code}): {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Excepción al llamar a la API de Cloudflare: {e}")
        return False

def detectar_genero_nombre(nombre):
    """
    Intenta inferir el género de un nombre para ajustar los prompts de imagen.
    Retorna "hombre", "mujer" o "persona" (neutral/desconocido).
    """
    if not nombre:
        return "persona"

    nombre_lower = nombre.lower().split(' ')[0] # Solo la primera palabra del nombre

    # Nombres femeninos comunes en español
    nombres_femeninos = [
        'maria', 'ana', 'laura', 'sofia', 'carmen', 'lucia', 'paula', 'elena',
        'isabel', 'teresa', 'valentina', 'camila', 'daniela', 'victoria', 'josefina',
        'rocio', 'pilar', 'clara', 'julia', 'martina', 'emilia', 'agustina', 'andrea'
    ]
    # Nombres masculinos comunes en español
    nombres_masculinos = [
        'juan', 'pedro', 'carlos', 'miguel', 'david', 'javier', 'daniel',
        'alejandro', 'sergio', 'pablo', 'jose', 'martin', 'facundo', 'agustin',
        'santiago', 'franco', 'enzo', 'matias', 'lucas', 'manuel', 'andres'
    ]

    if nombre_lower in nombres_femeninos:
        return "mujer"
    elif nombre_lower in nombres_masculinos:
        return "hombre"
    elif nombre_lower.endswith('a') and nombre_lower not in ['jose', 'luca', 'matias']: # Algunas excepciones donde 'a' no es femenino
        return "mujer"
    elif nombre_lower.endswith('o') and nombre_lower not in ['rocio', 'consuelo']: # Algunas excepciones donde 'o' no es masculino
        return "hombre"
    
    return "persona" # Por defecto, neutral

def generar_web_profesional(nombre_negocio, data_json, textos_ai=None, carpeta_salida="sitios"):
    """
    Genera un sitio web completo para un negocio.
    
    Args:
        nombre_negocio (str): El nombre del negocio.
        data_json (dict): Los datos crudos del scraper.
        textos_ai (dict, optional): Contenido generado por IA. 
                                    Debe contener: 'titulo_hero', 'descripcion', 'lema_corto', 'beneficios'.
        carpeta_salida (str): Carpeta raíz donde se guardará la web (default: "sitios").
    """
    categoria_raw = data_json.get('categoria', 'negocio').lower().strip()
    # Crea un slug simple de la categoría, ej: "Centro de Estética" -> "centro"
    # Aseguramos que siempre haya un slug válido, incluso si la categoría viene vacía
    primera_palabra = categoria_raw.split(" ")[0] if categoria_raw else "general"
    categoria_slug = re.sub(r'[\W_]+', '_', primera_palabra) or "general"

    nombre_slug = re.sub(r'[\W_]+', '_', nombre_negocio.lower())
    
    # Nueva ruta dinámica: {carpeta_salida}/{categoria_slug}/{nombre_slug}
    ruta_web = f"{carpeta_salida}/{categoria_slug}/{nombre_slug}"
    os.makedirs(ruta_web, exist_ok=True)
    
    # Crear estructura para assets futuros (Punto 12)
    os.makedirs(f"{ruta_web}/assets/img", exist_ok=True)
    # Guardar respaldo de los datos usados
    with open(f"{ruta_web}/datos_negocio.json", "w", encoding="utf-8") as f:
        json.dump(data_json, f, ensure_ascii=False, indent=2)

    # --- SISTEMA DE PALETAS DE COLORES ---
    # Ahora usamos PALETAS_COLORES importado de src.constants

    # Lógica de Selección
    paleta_seleccionada = None
    texto_busqueda = (categoria_raw + " " + nombre_negocio).lower() # Buscamos en categoría y nombre
    
    # 1. Buscar coincidencia en las listas definidas
    for nombre_paleta, datos in PALETAS_COLORES.items():
        # Verificamos si alguna keyword de la paleta está en el texto de búsqueda
        if any(keyword in texto_busqueda for keyword in datos["categorias"]):
            paleta_seleccionada = datos["colores"]
            print(f"[DISEÑO] Categoría detectada: '{nombre_paleta}'. Aplicando paleta predefinida.")
            break
    
    # 2. Si no hubo coincidencia, usar Default (NOCTURNA_GOURMET) y permitir sugerencia IA
    if not paleta_seleccionada:
        print("[DISEÑO] Categoría no reconocida. Usando Default (Nocturna) y consultando IA...")
        paleta_seleccionada = PALETAS_COLORES["NOCTURNA_GOURMET"]["colores"].copy() # Copia para no modificar la original
        
        # Solo en este caso (Default) escuchamos a la IA
        if textos_ai and "sugerencia_colores" in textos_ai:
            sug = textos_ai["sugerencia_colores"]
            if all(k in sug for k in ["color_primario", "color_fondo", "color_texto"]):
                print("[DISEÑO] Aplicando sugerencia de colores de la IA.")
                paleta_seleccionada["primario"] = sug["color_primario"]
                paleta_seleccionada["fondo"] = sug["color_fondo"]
                paleta_seleccionada["texto"] = sug["color_texto"]
                # Ajuste simple de contraste para texto inverso
                paleta_seleccionada["texto_inverso"] = "#ffffff" 

    # --- Lógica de Prompts de Imagen ---
    # Elige el conjunto de prompts correcto basado en la categoría para darle un estilo visual específico.
    prompts_por_categoria = {
        "SALUD": {
            "keywords": ["veterinaria", "odont", "medico", "médico", "kinesio", "salud", "clinic", "clínica", "farmacia", "psicolog", "nutricion", "consultorio"],
            "prompts": {
                "logo": f"clean modern minimalist logo for health service, {nombre_slug}",
                "fondo": "bright modern medical office interior, clean, professional, high-key lighting, minimalist",
                "testimonio": "happy patient talking to a professional, bright ambient, clean background"
            }
        },
        "ESTETICA": {
            "keywords": ["peluqu", "estetic", "estética", "belleza", "uñas", "makeup", "spa", "moda"],
            "prompts": {
                "logo": f"elegant stylish logo for beauty salon, {nombre_slug}",
                "fondo": "bright luxury beauty salon interior, elegant, clean, high-key lighting, minimalist",
                "testimonio": "client with a beautiful hairstyle smiling, bright ambient, soft focus"
            }
        },
        "NOCTURNO_GOURMET": {
            "keywords": ["restaurante", "bar", "cerveceria", "cervecería", "pub", "disco", "hamburgueseria", "hamburguesería", "pizzeria", "pizzería", "sushi", "parrilla", "gastrono", "cafeteria", "cafetería", "evento", "hotel"],
            "prompts": {
                "logo": f"elegant logo for restaurant or bar, {nombre_slug}",
                "fondo": "cozy restaurant or bar interior with warm lighting, cinematic, dramatic shadows",
                "testimonio": "happy customers eating and drinking, warm ambient, bokeh"
            }
        },
        "FITNESS": {
            "keywords": ["gimnasio", "gym", "crossfit", "fitness", "entrenam", "deport", "pilates", "yoga"],
            "prompts": {
                "logo": f"strong bold modern logo for fitness gym, {nombre_slug}, vector style",
                "fondo": "modern gym interior with equipment, dramatic lighting, high contrast, professional photography",
                "testimonio": "person training in a gym, happy, sweating, fitness lifestyle"
            }
        },
        "OFICIOS_TALLER": {
            "keywords": ["taller", "mecanic", "mecánic", "ferreteria", "construc", "reparacion", "repuestos", "automotor", "chapa", "pintura", "obra", "electricista", "plomero"],
            "prompts": {
                "logo": f"professional emblem logo for mechanic workshop or hardware store, {nombre_slug}, industrial style",
                "fondo": "clean organized mechanic workshop interior with cars and tools, professional lighting",
                "testimonio": "mechanic professional talking to a client, friendly, workshop background"
            }
        },
        "default": {
            "keywords": [], # no keywords, it's the fallback
            "prompts": {
                "logo": f"clean professional logo for {nombre_slug}",
                "fondo": f"modern local business interior, cinematic lighting, for a {categoria_raw}",
                "testimonio": "satisfied client in a shop"
            }
        }
    }
    
    # Lógica de selección de prompts de imagen
    prompts = prompts_por_categoria["default"]["prompts"] # Empezamos con el default
    for key, data in prompts_por_categoria.items():
        if key != "default" and any(keyword in texto_busqueda for keyword in data["keywords"]):
            prompts = data["prompts"]
            print(f"[IMAGEN] Categoría de imagen detectada: '{key}'. Aplicando prompts específicos.")
            break

    # Generar y guardar imágenes, obteniendo sus rutas relativas
    ruta_logo_local = f"{ruta_web}/assets/img/logo.png"
    if generar_y_guardar_imagen(prompts["logo"], ruta_logo_local):
        url_logo = "assets/img/logo.png"
    else:
        url_logo = "https://via.placeholder.com/300" # Fallback

    # Para el fondo, lo guardamos pero lo referenciamos en el CSS
    ruta_fondo_local = f"{ruta_web}/assets/img/fondo_hero.jpg"
    generar_y_guardar_imagen(prompts["fondo"], ruta_fondo_local)
    # La URL del fondo se inyectará directamente en el CSS
    url_fondo_css = "assets/img/fondo_hero.jpg"


    # --- Link de WhatsApp (definido antes para usarlo como fallback) ---
    tel = "".join(filter(str.isdigit, data_json.get('telefono', '')))
    wa_link = f"https://wa.me/549{tel}" if tel else "#"

    # --- Adaptación a IA (Punto 10) ---
    # Si la IA no proveyó textos o falla, usamos genéricos robustos.
    textos_ai = textos_ai or {} # Asegurar que sea un diccionario para usar .get()
    titulo_hero = textos_ai.get('titulo_hero', f"Bienvenido a {nombre_negocio}")
    cta_button_text = textos_ai.get('cta_button_text', "CONTACTAR AHORA")
    cta_button_link = textos_ai.get('cta_button_link', wa_link) # Por defecto, WhatsApp
    descripcion_presentacion = textos_ai.get('descripcion', f"Visítanos en nuestra dirección en {data_json.get('direccion', 'el corazón de la ciudad')} para recibir la mejor atención en {data_json.get('categoria', 'nuestros servicios')}.")
    lema_hero = textos_ai.get('lema_corto', f"Calidad y confianza en cada detalle.")

    # Procesar Reseñas
    comentarios_reales = data_json.get('comentarios', [])
    comentarios_filtrados = []
    
    # 1. Filtrar solo reseñas buenas (4 o 5 estrellas/puntos)
    for c in comentarios_reales:
        rating_raw = str(c.get('rating', '')).lower()
        if '4' in rating_raw or '5' in rating_raw:
            comentarios_filtrados.append(c)
            
    # 2. Seleccionar top 3 o rellenar con ficticios
    comentarios_finales = comentarios_filtrados[:3]
    
    nombres_fake = ["Juan Pérez", "María González", "José López", "Ana Martínez", "Carlos Rodríguez"]
    textos_fake = [
        "¡Excelente servicio! Superaron mis expectativas totalmente.",
        "Muy profesionales y atentos. Definitivamente volveré.",
        "La calidad es increíble y el trato muy amable. 100% recomendado.",
        "Una experiencia fantástica, cuidaron cada detalle.",
        "Me encantó, son los mejores en lo que hacen."
    ]
    
    while len(comentarios_finales) < 3:
        idx = len(comentarios_finales)
        comentarios_finales.append({
            "autor": nombres_fake[idx % len(nombres_fake)],
            "texto": textos_fake[idx % len(textos_fake)],
            "rating": "⭐⭐⭐⭐⭐"
        })

    comentarios_html = ""
    for i, c in enumerate(comentarios_finales):
        # Detectar género del autor
        genero = detectar_genero_nombre(c.get('autor', ''))
        
        # Obtener el prompt base para testimonios de la categoría actual
        base_testimonio_prompt = prompts["testimonio"]
        
        # Ajustar el prompt según el género detectado
        prompt_testimonio_ajustado = base_testimonio_prompt
        if genero == "hombre":
            # Reemplazos específicos para hacer el prompt más masculino
            prompt_testimonio_ajustado = prompt_testimonio_ajustado.replace("patient", "male patient").replace("client", "male client").replace("person", "man").replace("professional", "male professional")
            # Para "customers" (plural), podemos ser más directos
            if "customers" in prompt_testimonio_ajustado:
                prompt_testimonio_ajustado = "happy male customers eating and drinking, warm ambient, bokeh"
            elif not any(term in prompt_testimonio_ajustado for term in ["male patient", "male client", "man", "male professional", "male customers"]):
                 prompt_testimonio_ajustado = "happy man " + base_testimonio_prompt
        elif genero == "mujer":
            # Reemplazos específicos para hacer el prompt más femenino
            prompt_testimonio_ajustado = prompt_testimonio_ajustado.replace("patient", "female patient").replace("client", "female client").replace("person", "woman").replace("professional", "female professional")
            # Para "customers" (plural)
            if "customers" in prompt_testimonio_ajustado:
                prompt_testimonio_ajustado = "happy female customers eating and drinking, warm ambient, bokeh"
            elif not any(term in prompt_testimonio_ajustado for term in ["female patient", "female client", "woman", "female professional", "female customers"]):
                prompt_testimonio_ajustado = "happy woman " + base_testimonio_prompt
        # Si genero es "persona" (neutral), se usa el prompt base sin modificar.

        ruta_testimonio_local = f"{ruta_web}/assets/img/testimonio_{i}.jpg"
        if generar_y_guardar_imagen(prompt_testimonio_ajustado, ruta_testimonio_local):
            url_testimonio = f"assets/img/testimonio_{i}.jpg"
        else:
            url_testimonio = "https://via.placeholder.com/150" # Fallback
        comentarios_html += f'''
        <article class="tarjeta-testimonio">
            <img src="{url_testimonio}" alt="Foto de {c.get('autor')}">
            <span class="comillas-testimonio">“</span>
            <p class="texto-testimonio">"{c.get('texto')[:140]}..."</p>
            <div class="estrellas-testimonio">⭐⭐⭐⭐⭐</div>
            <h3 class="autor-testimonio">{c.get('autor')}</h3>
        </article>
        '''

    # Generar HTML para los beneficios extraídos por la IA
    beneficios_html = ""
    beneficios = textos_ai.get('beneficios', [])
    if beneficios:
        beneficios_html = '<section class="seccion-beneficios"><h2 class="el-messiri">Por qué elegirnos</h2><div class="contenedor-tarjetas">'
        for beneficio in beneficios:
            beneficios_html += f'''
            <article class="tarjeta-producto tarjeta-beneficio">
                <h3 class="libre-baskerville">✓ {beneficio}</h3>
            </article>
            '''
        beneficios_html += '</div></section>'

    # --- NUEVO: Sección de Contacto / Redes Sociales ---
    facebook_url = data_json.get('facebook', 'No detectado')
    instagram_url = data_json.get('instagram', 'No detectado')
    has_facebook = facebook_url and "No detectado" not in facebook_url
    has_instagram = instagram_url and "No detectado" not in instagram_url
    
    # SVGs for social icons
    facebook_svg = '<svg fill="currentColor" role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><title>Facebook</title><path d="M22.675 0h-21.35C.593 0 0 .593 0 1.325v21.351C0 23.407.593 24 1.325 24H12.82v-9.294H9.692v-3.622h3.128V8.413c0-3.1 1.893-4.788 4.659-4.788 1.325 0 2.463.099 2.795.143v3.24l-1.918.001c-1.504 0-1.795.715-1.795 1.763v2.313h3.587l-.467 3.622h-3.12V24h6.116c.732 0 1.323-.593 1.323-1.325V1.325C24 .593 23.407 0 22.675 0z"/></svg>'
    instagram_svg = '<svg fill="currentColor" role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><title>Instagram</title><path d="M12 0C8.74 0 8.333.015 7.053.072 5.775.132 4.905.333 4.14.63c-.789.306-1.459.717-2.126 1.384S.936 3.35.63 4.14C.333 4.905.131 5.775.072 7.053.012 8.333 0 8.74 0 12s.015 3.667.072 4.947c.06 1.277.261 2.148.558 2.913.306.788.717 1.459 1.384 2.126.667.666 1.336 1.079 2.126 1.384.766.296 1.636.499 2.913.558C8.333 23.988 8.74 24 12 24s3.667-.015 4.947-.072c1.277-.06 2.148-.262 2.913-.558.788-.306 1.459-.718 2.126-1.384.666-.667 1.079-1.335 1.384-2.126.296-.765.499-1.636.558-2.913.06-1.28.072-1.687.072-4.947s-.015-3.667-.072-4.947c-.06-1.277-.262-2.149-.558-2.913-.306-.789-.718-1.459-1.384-2.126C21.314.936 20.644.523 19.854.218 19.095-.08 18.225-.282 16.947-.341 15.667-.398 15.26-.413 12-.413h0zm0 2.163c3.204 0 3.584.012 4.85.07 1.17.055 1.805.249 2.227.415.562.217.96.477 1.382.896.419.42.679.819.896 1.381.164.422.36 1.057.413 2.227.057 1.266.07 1.646.07 4.85s-.012 3.584-.07 4.85c-.055 1.17-.249 1.805-.413 2.227-.217.562-.477.96-.896 1.382-.42.419-.819.679-1.381.896-.422.164-1.057.36-2.227.413-1.266.057-1.646.07-4.85.07s-3.584-.012-4.85-.07c-1.17-.055-1.805-.249-2.227-.413-.562-.217-.96-.477-1.382-.896-.419-.42-.679-.819-.896-1.381-.164-.422-.36-1.057-.413-2.227-.057-1.266-.07-1.646-.07-4.85s.012-3.584.07-4.85c.055-1.17.249-1.805.413-2.227.217-.562.477.96.896-1.382.42-.419.819.679 1.381-.896.422-.164 1.057.36 2.227-.413 1.266-.057 1.646-.07 4.85.07zM12 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.88 1.44 1.44 0 000-2.88z"/></svg>'

    contacto_html = '<section class="seccion-presentacion"><h2 class="el-messiri">Seguinos en Redes</h2><div class="social-icons">'
    
    # Instagram Icon
    if has_instagram:
        contacto_html += f'<a href="{instagram_url}" target="_blank" class="social-icon instagram active-link" aria-label="Instagram">{instagram_svg}</a>'
    else:
        contacto_html += f'<a href="javascript:void(0);" class="social-icon instagram" aria-label="Instagram no disponible">{instagram_svg}</a>'
    
    # Facebook Icon
    if has_facebook:
        contacto_html += f'<a href="{facebook_url}" target="_blank" class="social-icon facebook active-link" aria-label="Facebook">{facebook_svg}</a>'
    else:
        contacto_html += f'<a href="javascript:void(0);" class="social-icon facebook" aria-label="Facebook no disponible">{facebook_svg}</a>'
        
    contacto_html += '</div></section>'
    
    # --- NUEVO: Sección de Menú (si aplica) ---
    menu_section_html = ""
    if cta_button_link == "#menu":
        menu_section_html = '<section id="menu" class="seccion-presentacion"><h2 class="el-messiri">Nuestro Menú</h2><p style="max-width: 800px; margin: 0 auto; font-size: 1.2rem;">Explora nuestras deliciosas opciones y especialidades.</p></section>'


    # --- NUEVO: Sección Dónde Estamos ---
    direccion = data_json.get('direccion')
    donde_estamos_html = ""
    if direccion:
        map_link = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(direccion)}"
        donde_estamos_html = f'''
        <section class="seccion-presentacion">
            <h2 class="el-messiri">Dónde Estamos</h2>
            <p style="max-width: 800px; margin: 0 auto; font-size: 1.2rem;">{direccion}</p>
            <a href="{map_link}" target="_blank" class="cta-button" style="margin-top: 1.5rem;">VER EN MAPA</a>
        </section>
        '''

    # --- NUEVO: Lógica para el Footer ---
    current_year = datetime.date.today().year
    footer_html = f"""
    <footer style="background: #181818; padding: 2rem; text-align: center; color: #aaa; font-size: 0.9rem;">
        <p>&copy; {current_year} {nombre_negocio}. Todos los derechos reservados.</p>
    </footer>
    """

    CSS_MASTER = f"""
    /* --- Reset y Variables (Basado en instrucciones_sistema.md) --- */
    :root {{
        /* Colores (adaptados de los valores originales del generador) */
        --color-primario: {paleta_seleccionada['primario']};
        --color-fondo-base: {paleta_seleccionada['fondo']};
        --color-texto-base: {paleta_seleccionada['texto']};
        --color-texto-inverso: {paleta_seleccionada['texto_inverso']};
        --color-overlay: {paleta_seleccionada['overlay']};
        --color-fondo-tarjeta: {paleta_seleccionada.get('fondo_tarjeta', '#ffffff')};
        
        --color-acento-oscuro: #5a1111;
        --color-fondo-claro: #F8F6F4;

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
    body {{ 
        font-family: var(--fuente-base); 
        background: linear-gradient(180deg, var(--color-overlay) 42%, var(--color-overlay) 84%), url('{url_fondo_css}');
        background-size: cover; background-attachment: fixed; 
        color: var(--color-texto-base);
        background-color: var(--color-fondo-base);
        font-size: var(--font-size-xs);
        line-height: 1.6;
        overflow-x: hidden;
    }}
    img {{ max-width: 100%; height: auto; display: block; }}
    h1, h2, h3 {{ font-family: var(--fuente-secundaria); }}

    /* --- Estilos Generales y Componentes --- */
    .barra-navegacion {{ width: 100%; display: flex; flex-direction: column; align-items: center; padding: var(--espaciado-sm); }}
    .logo img {{ width: 10.5rem; height: 10.5rem; border-radius: 50%; border: 3px solid var(--color-primario); }}
    .seccion-hero {{ text-align: center; padding: var(--espaciado-lg) var(--espaciado-md); min-height: 60vh; display: flex; flex-direction: column; justify-content: center; align-items: center; }}
    .seccion-hero h1 {{ font-size: var(--font-size-xxl); }}
    .lema-hero {{ text-transform: uppercase; font-weight: 700; font-size: var(--font-size-xxs); opacity: 0.9; margin-top: var(--espaciado-sm);}}
    .cta-button {{ background-color: var(--color-texto-inverso); color: var(--color-primario); padding: 0.75rem 1.5rem; border-radius: 0.5rem; text-decoration: none; font-weight: 600; display: inline-block; margin-top: var(--espaciado-md); border: 1px solid var(--color-primario); transition: var(--transicion-estandar); }}
    .cta-button:hover {{ background-color: var(--color-primario); color: var(--color-texto-inverso); }}
    .contenedor-tarjetas {{ display: grid; grid-template-columns: 1fr; gap: var(--espaciado-md); }}
    .tarjeta-producto {{ background: var(--color-primario); border-radius: var(--radio-card); padding: 1.5rem; color: var(--color-texto-inverso); transition: var(--transicion-estandar); box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
    .tarjeta-producto:hover {{ transform: translateY(-5px); }}
    .tarjeta-producto img {{ width: 100%; height: 15rem; object-fit: cover; border-radius: 0.5rem; }}
    .tarjeta-beneficio {{ background: #ffffff; color: #333; text-align: center; padding: 2rem 1rem; display: flex; align-items: center; justify-content: center; border: 1px solid #eee; }}
    .tarjeta-beneficio h3 {{ font-size: var(--font-size-sm); }}
    
    /* --- Estilos Nuevos para Testimonios --- */
    .tarjeta-testimonio {{ background: var(--color-fondo-tarjeta); border-radius: var(--radio-card); padding: 2rem; display: flex; flex-direction: column; align-items: center; text-align: center; color: #333; transition: var(--transicion-estandar); position: relative; border: 1px solid #eee; }}
    .tarjeta-testimonio:hover {{ transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.2); }}
    .tarjeta-testimonio img {{ width: 6rem; height: 6rem; border-radius: 50%; object-fit: cover; border: 3px solid var(--color-primario); margin-bottom: 1rem; }}
    .comillas-testimonio {{ font-size: 4rem; line-height: 0.5; font-family: serif; color: var(--color-primario); display: block; margin-bottom: 1rem; margin-top: 0.5rem; opacity: 0.8; }}
    .texto-testimonio {{ font-style: italic; margin-bottom: 1rem; font-size: 1.1rem; }}
    .estrellas-testimonio {{ color: #FFD700; margin-bottom: 0.5rem; font-size: 1.2rem; letter-spacing: 2px; }}
    .autor-testimonio {{ font-weight: bold; font-family: var(--fuente-secundaria); font-size: 1rem; text-transform: uppercase; }}

    .precio-real {{ color: var(--color-acento-oscuro); font-weight: bold; font-size: var(--font-size-sm); margin-top: var(--espaciado-sm); display: block; }}
    .posicion-fixed {{ position: fixed; bottom: 5vh; right: 2vw; background: #2cc748; border-radius: 50%; padding: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); z-index: 1000; }}
    .seccion-beneficios, .seccion-presentacion, .seccion-productos {{ padding: var(--espaciado-lg) var(--espaciado-md); text-align: center; }}
    .seccion-beneficios h2, .seccion-presentacion h2, .seccion-productos h2 {{ margin-bottom: var(--espaciado-md); font-size: var(--font-size-xl); }}
    
    /* --- NUEVO: Estilos para iconos de redes sociales --- */
    .social-icons {{ display: flex; justify-content: center; gap: 2rem; margin-top: 1rem; }}
    .social-icon svg {{ width: 40px; height: 40px; transition: var(--transicion-estandar); }}
    .social-icon.instagram {{ color: #E1306C; }}
    .social-icon.facebook {{ color: #1877F2; }}
    .social-icon {{ cursor: pointer; }}
    .social-icon.active-link:hover {{ opacity: 0.8; transform: scale(1.1); }}

    /* --- Estrategia Responsive (Mobile First) --- */
    /* Tablet */
    @media (min-width: 769px) {{
        .contenedor-tarjetas {{ grid-template-columns: repeat(2, 1fr); }}
    }}

    /* Desktop */
    @media (min-width: 1201px) {{
        .contenedor-tarjetas {{ grid-template-columns: repeat(3, 1fr); max-width: 1200px; margin: 0 auto; }}
        .seccion-hero, .seccion-presentacion, .seccion-beneficios, .seccion-productos {{ padding-left: var(--espaciado-xl); padding-right: var(--espaciado-xl); }}
    }}
    """
    # Template HTML Final inyectando el CSS
    html_final = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{nombre_negocio} | Oficial</title>
        
        <!-- SEO & Metadatos (Privacidad activada: No Index) -->
        <meta name="robots" content="noindex, nofollow">
        <meta name="description" content="{descripcion_presentacion.replace('"', "'")[:160]}">
        <meta property="og:title" content="{nombre_negocio}">
        <meta property="og:description" content="{descripcion_presentacion.replace('"', "'")[:160]}">
        
        <style>{CSS_MASTER}</style>
        <link href="https://fonts.googleapis.com/css2?family=El+Messiri:wght@400;700&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
    </head>
    <body>
        <nav class="barra-navegacion">
            <div class="logo">
                <img src="{url_logo}" alt="Logo de {nombre_negocio}">
            </div>
        </nav>

        <section class="seccion-hero">
            <div class="contenedor-hero">
                <h1 class="el-messiri" style="text-transform: capitalize;">{nombre_negocio}</h1>
                <p style="font-size: 1.5rem; margin-top: 0.5rem; font-weight: 300;">{titulo_hero}</p>
                <div class="texto-adornado">
                    <p class="lema-hero">{lema_hero}</p>
                </div>
                <a href="{cta_button_link}" class="cta-button">{cta_button_text}</a>
            </div>
        </section>

        <section class="seccion-presentacion">
            <h2 class="libre-baskerville">Sobre Nosotros</h2>
            <p style="max-width: 800px; margin: 0 auto; font-size: 1.2rem;">{descripcion_presentacion}</p>
        </section>

        {beneficios_html}

        <section class="seccion-productos">
            <h2 class="el-messiri">Experiencias de nuestros clientes</h2>
            <div class="contenedor-tarjetas">
                {comentarios_html}
            </div>
        </section>

        {menu_section_html}

        {donde_estamos_html}

        {contacto_html}

        <a href="{wa_link}" class="posicion-fixed" aria-label="Contactar por WhatsApp">
            <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="40" height="40">
        </a>

        {footer_html}
    </body>
    </html>
    """

    with open(f"{ruta_web}/index.html", "w", encoding="utf-8") as f:
        f.write(html_final)
    
    return f"[OK] Sitio creado en: {ruta_web}"