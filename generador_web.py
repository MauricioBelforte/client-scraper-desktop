import os
import re
import json
import urllib.parse
import datetime
import random
import requests
import time
from src.constants import PALETAS_COLORES
from maquetas.v1 import generar_maqueta_v1
from maquetas.v2 import generar_maqueta_v2
from src.utils import get_open_status_and_next_time # Import the new utility function

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
        payload = {
            "prompt": prompt,
            "num_steps": 20,
            "guidance": 7.5,
            "negative_prompt": "blurry, low quality, distorted, ugly, text, watermark, bad anatomy, nsfw, nude, darkness, black image"
        }

        # Lógica de reintento para errores transitorios (500, 502, etc.)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=45)

                if response.status_code == 200:
                    # NUEVA VERIFICACIÓN: Asegurarse de que la imagen no esté vacía o sea inválida.
                    # Una imagen negra o un error a veces resulta en una respuesta muy pequeña.
                    # Establecemos un umbral mínimo de 1KB.
                    if len(response.content) > 1024:
                        with open(ruta_guardado, 'wb') as f:
                            f.write(response.content)
                        return True
                    print(f"[AVISO] La imagen generada es demasiado pequeña ({len(response.content)} bytes). Posiblemente es una imagen negra o corrupta. Omitiendo.")
                    return False
                
                response_text = response.text
                print(f"[AVISO] Error Cloudflare ({response.status_code}) - Intento {attempt+1}/{max_retries}: {response_text}")

                # --- NUEVO: Manejo de error de capacidad temporal ---
                if "temporarily at capacity" in response_text.lower():
                    print("[AVISO] API de Cloudflare en capacidad temporal. Esperando 11 segundos como se solicitó...")
                    time.sleep(11)
                    continue # Reintentar
                elif response.status_code >= 500 or response.status_code == 429:
                    time.sleep(3)
                    continue
                return False
            except Exception as e:
                print(f"[AVISO] Error conexión Cloudflare ({e}) - Intento {attempt+1}/{max_retries}")
                time.sleep(3)
        
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

def descargar_imagen_real(url: str, ruta_guardado: str) -> bool:
    """
    Descarga una imagen desde una URL y la guarda localmente.
    Añade un User-Agent para simular un navegador y evitar bloqueos (ej. 403 Forbidden).
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, timeout=15, headers=headers)
        
        # --- RETRY LOGIC: Fallback para imágenes de Google que fallan con =s0 ---
        if response.status_code in [400, 403, 404] and "googleusercontent" in url and "=s0" in url:
            print(f"[AVATAR] Falló descarga con tamaño original (=s0). Reintentando con tamaño fijo (=s800)...")
            url_fallback = url.replace("=s0", "=s800")
            response = requests.get(url_fallback, timeout=15, headers=headers)
            
        if response.status_code == 200:
            with open(ruta_guardado, 'wb') as f:
                f.write(response.content)
            return True
        else:
            print(f"[AVATAR] Error al descargar imagen real ({response.status_code}) desde: {url}")
            return False
    except Exception as e:
        print(f"[AVATAR] Excepción al descargar imagen real: {e}")
        return False

def generar_avatar_sintetico(autor: str, prompts: dict, ruta_guardado: str) -> bool:
    """
    Genera un avatar sintético con IA basado en el género del autor.
    Encapsula la lógica de construcción del prompt y la llamada a la API.
    """
    genero = detectar_genero_nombre(autor)
    base_testimonio_prompt = prompts["testimonio"]
    
    prompt_testimonio_ajustado = base_testimonio_prompt
    if genero == "hombre":
        # Reemplazos específicos para hacer el prompt más masculino
        prompt_testimonio_ajustado = prompt_testimonio_ajustado.replace("patient", "male patient").replace("client", "male client").replace("person", "man").replace("professional", "male professional")
        # Para "customers" (plural), podemos ser más directos
        if "customers" in prompt_testimonio_ajustado:
            prompt_testimonio_ajustado = "happy male customers eating and drinking, warm ambient, bokeh, photorealistic, real people, 8k, photography style"
        elif not any(term in prompt_testimonio_ajustado for term in ["male patient", "male client", "man", "male professional", "male customers"]):
                prompt_testimonio_ajustado = "happy man " + base_testimonio_prompt
    elif genero == "mujer":
        # Reemplazos específicos para hacer el prompt más femenino
        prompt_testimonio_ajustado = prompt_testimonio_ajustado.replace("patient", "female patient").replace("client", "female client").replace("person", "woman").replace("professional", "female professional")
        # Para "customers" (plural)
        if "customers" in prompt_testimonio_ajustado:
            prompt_testimonio_ajustado = "happy female customers eating and drinking, warm ambient, bokeh, photorealistic, real people, 8k, photography style"
        elif not any(term in prompt_testimonio_ajustado for term in ["female patient", "female client", "woman", "female professional", "female customers"]):
            prompt_testimonio_ajustado = "happy woman " + base_testimonio_prompt
    
    return generar_y_guardar_imagen(prompt_testimonio_ajustado, ruta_guardado)

def generar_web_profesional(nombre_negocio, data_json, textos_ai=None, carpeta_salida="sitios", version="v1"):
    """
    Genera un sitio web completo para un negocio.
    
    Args:
        nombre_negocio (str): El nombre del negocio.
        data_json (dict): Los datos crudos del scraper.
        textos_ai (dict, optional): Contenido generado por IA. 
                                    Debe contener: 'titulo_hero', 'descripcion', 'lema_corto', 'beneficios'.
        carpeta_salida (str): Carpeta raíz donde se guardará la web (default: "sitios").
        version (str): Versión de la maqueta a generar ("v1" o "v2").
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
    texto_busqueda = (categoria_raw + " " + nombre_negocio).lower() # Buscamos en categoría y nombre
    
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
                "logo": f"clean modern minimalist logo for health service, {nombre_negocio}",
                "fondo": "bright modern medical office interior, clean, professional, high-key lighting, minimalist",
                "testimonio": "happy patient talking to a professional, bright ambient, clean background, photorealistic, real person, 8k, photography style"
            }
        },
        "ESTETICA": {
            "keywords": ["peluqu", "estetic", "estética", "belleza", "uñas", "makeup", "spa", "moda"],
            "prompts": {
                "logo": f"elegant stylish logo for beauty salon, {nombre_negocio}",
                "fondo": "bright luxury beauty salon interior, elegant, clean, high-key lighting, minimalist",
                "testimonio": "client with a beautiful hairstyle smiling, bright ambient, soft focus, photorealistic, real person, 8k, photography style"
            }
        },
        "BARBERIA": {
            "keywords": ["barberia", "barber", "barbería"],
            "prompts": {
                "logo": f"vintage masculine logo for a barber shop, {nombre_negocio}, emblem style",
                "fondo": "classic barber shop interior, leather chairs, vintage mirrors, warm moody lighting, cinematic",
                "testimonio": "man with a fresh haircut and beard trim looking confident, barbershop background, photorealistic, real person, 8k, photography style"
            }
        },
        "TATTOO": {
            "keywords": ["tattoo", "tatuajes", "tatoo", "tatuador"],
            "prompts": {
                "logo": f"bold logo for a tattoo studio, {nombre_negocio}, traditional tattoo art style",
                "fondo": "artistic tattoo studio interior, dark walls, art prints, moody lighting, creative atmosphere",
                "testimonio": "happy client showing a new tattoo, artistic, detailed, photorealistic, real person, 8k, photography style"
            }
        },
        "NOCTURNO_GOURMET": {
            "keywords": ["restaurante", "bar", "bares", "cerveceria", "cervecería", "pub", "disco", "hamburgueseria", "hamburguesería", "pizzeria", "pizzería", "sushi", "parrilla", "gastrono", "cafeteria", "cafetería", "evento", "hotel"],
            "prompts": {
                "logo": f"elegant logo for restaurant or bar, {nombre_negocio}",
                "fondo": "cozy restaurant or bar interior with warm lighting, cinematic, dramatic shadows",
                "testimonio": "happy customers eating and drinking, warm ambient, bokeh, photorealistic, real people, 8k, photography style"
            }
        },
        "FITNESS": {
            "keywords": ["gimnasio", "gym", "crossfit", "fitness", "entrenam", "deport", "pilates", "yoga"],
            "prompts": {
                "logo": f"strong bold modern logo for fitness gym, {nombre_negocio}, vector style",
                "fondo": "modern gym interior with equipment, dramatic lighting, high contrast, professional photography",
                "testimonio": "person training in a gym, happy, sweating, fitness lifestyle, photorealistic, real person, 8k, photography style"
            }
        },
        "OFICIOS_TALLER": {
            "keywords": ["taller", "mecanic", "mecánic", "ferreteria", "construc", "reparacion", "repuestos", "automotor", "chapa", "pintura", "obra", "electricista", "plomero"],
            "prompts": {
                "logo": f"professional emblem logo for mechanic workshop or hardware store, {nombre_negocio}, industrial style",
                "fondo": "clean organized mechanic workshop interior with cars and tools, professional lighting",
                "testimonio": "mechanic professional talking to a client, friendly, workshop background, photorealistic, real people, 8k, photography style"
            }
        },
        "MUEBLERIA": {
            "keywords": ["muebleria", "mueblería", "muebles", "decoracion", "decoración", "interiorismo", "sofa", "colchon"],
            "prompts": {
                "logo": f"elegant modern furniture store logo, minimalist, {nombre_negocio}, wood texture elements",
                "fondo": "modern living room interior with stylish furniture, warm lighting, professional photography, high resolution, cozy atmosphere",
                "testimonio": "happy family sitting on a comfortable sofa, smiling, bright living room background, photorealistic, real people, 8k, photography style"
            }
        },
        "NATURALEZA": {
            "keywords": ["verduleria", "botanica", "jardineria", "jardinero", "vivero", "floreria", "organico", "dietetica", "fruteria"],
            "prompts": {
                "logo": f"clean modern minimalist logo for a fresh market or garden store, {nombre_negocio}, green leaf icon",
                "fondo": "bright modern grocery store interior with fresh vegetables and fruits, clean, natural light, professional photography",
                "testimonio": "happy customer holding a basket of fresh vegetables, smiling, bright natural background, photorealistic, real person, 8k, photography style"
            }
        },
        "default": {
            "keywords": [], # no keywords, it's the fallback
            "prompts": {
                "logo": f"clean professional logo for {nombre_negocio}",
                "fondo": f"modern local business interior, cinematic lighting, for a {categoria_raw}",
                "testimonio": "satisfied client in a shop, photorealistic, real person, 8k, photography style"
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
    print(f"[LOGO] Generando logotipo para '{nombre_negocio}'...")
    if generar_y_guardar_imagen(prompts["logo"], ruta_logo_local):
        url_logo = "assets/img/logo.png"
        print(f"  -> Éxito. Logo generado con IA.")
    else:
        print(f"  -> Falló generación. Usando placeholder.")
        url_logo = "https://via.placeholder.com/300" # Fallback

    # Para el fondo, lo guardamos pero lo referenciamos en el CSS
    ruta_fondo_local = f"{ruta_web}/assets/img/fondo_hero.jpg"
    print(f"[FONDO] Generando imagen de fondo para '{categoria_raw}'...")
    if generar_y_guardar_imagen(prompts["fondo"], ruta_fondo_local):
        # La URL del fondo se inyectará directamente en el CSS
        url_fondo_css = "assets/img/fondo_hero.jpg"
        print(f"  -> Éxito. Fondo generado con IA.")
    else:
        # Fallback si falla la generación
        print(f"  -> Falló generación. Usando fondo de stock (Unsplash).")
        url_fondo_css = "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=1920&q=80"


    # --- Link de WhatsApp (definido antes para usarlo como fallback) ---
    # Corrección: Convertir a string explícitamente para evitar error si el valor es None
    tel = "".join(filter(str.isdigit, str(data_json.get('telefono') or '')))
    wa_link = f"https://wa.me/549{tel}" if tel else "#"
    tel_raw = str(data_json.get('telefono') or '')
    tel = "".join(filter(str.isdigit, tel_raw))
    
    if tel:
        # --- CORRECCIÓN DE FORMATO ARGENTINA ---
        if tel.startswith("0"):
            tel = tel[1:]
        if not tel.startswith("54"):
            tel = "549" + tel
        if tel.startswith("5490"):
            tel = "549" + tel[4:]
        wa_link = f"https://wa.me/{tel}"
    else:
        wa_link = "#"

    # --- Adaptación a IA (Punto 10) ---
    # Si la IA no proveyó textos o falla, usamos genéricos robustos.
    textos_ai = textos_ai or {} # Asegurar que sea un diccionario para usar .get()
    titulo_hero = textos_ai.get('titulo_hero', f"Bienvenido a {nombre_negocio}")
    cta_button_text = textos_ai.get('cta_button_text', "CONTACTAR AHORA")
    cta_button_link = textos_ai.get('cta_button_link', wa_link) # Por defecto, WhatsApp
    descripcion_presentacion = textos_ai.get('descripcion', f"Visítanos en nuestra dirección en {data_json.get('direccion', 'el corazón de la ciudad')} para recibir la mejor atención en {data_json.get('categoria', 'nuestros servicios')}.")
    lema_hero = textos_ai.get('lema_corto', f"Calidad y confianza en cada detalle.")

    # Procesar Reseñas
    # Hacemos la carga más robusta. Si la IA devuelve 'null' para comentarios, lo convertimos en lista vacía.
    comentarios_reales = data_json.get('comentarios') or []
    comentarios_filtrados = []
    
    for c in comentarios_reales: # type: ignore
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
    for i, c in enumerate(comentarios_finales): # type: ignore
        url_testimonio = "https://via.placeholder.com/150" # Fallback por defecto

        # --- NUEVA ESTRATEGIA DE AVATARES ---
        # Criterio de elección: la primera imagen de la reseña. Es simple y efectivo.
        if c.get("imagenes"):
            url_real = c["imagenes"][0]
            ruta_local_real = f"{ruta_web}/assets/img/testimonio_real_{i}.jpg"
            print(f"[AVATAR] Testimonio {i} tiene imagen real. Intentando descargar...")
            
            if descargar_imagen_real(url_real, ruta_local_real):
                url_testimonio = f"assets/img/testimonio_real_{i}.jpg"
                print(f"  -> Éxito. Usando imagen real.")
            else:
                print(f"  -> Falló descarga. Se usará placeholder.")
        else:
            # Si no hay imagen real, generamos una con IA
            print(f"[AVATAR] Testimonio {i} no tiene imagen. Generando con IA...")
            ruta_sintetica_local = f"{ruta_web}/assets/img/testimonio_sintetico_{i}.jpg"
            if generar_avatar_sintetico(c.get('autor', ''), prompts, ruta_sintetica_local):
                url_testimonio = f"assets/img/testimonio_sintetico_{i}.jpg"
                print(f"  -> Éxito. Usando imagen sintética.")
            else:
                print(f"  -> Falló generación. Se usará placeholder.")

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
    # Hacemos la carga más robusta. Si la IA devuelve 'null' para beneficios, lo convertimos en lista vacía.
    beneficios = textos_ai.get('beneficios') or []
    
    # --- NUEVO: Sección de Contacto / Redes Sociales ---
    facebook_url = data_json.get('facebook', 'No detectado')
    instagram_url = data_json.get('instagram', 'No detectado')
    has_facebook = facebook_url and "No detectado" not in facebook_url
    has_instagram = instagram_url and "No detectado" not in instagram_url
    
    # --- NUEVO: Sección Dónde Estamos ---
    direccion = data_json.get('direccion')
    
    # --- NUEVO: Estado de Horarios (Abierto/Cerrado) ---
    open_status_text = ""
    next_time_info = ""
    if data_json.get('horarios_detallados'):
        open_status_text, next_time_info = get_open_status_and_next_time(data_json['horarios_detallados'])
    
    # --- Empaquetado de Datos para las Maquetas ---
    # Reunimos todo lo necesario en un diccionario para pasarlo limpio a las funciones de diseño
    datos_web = {
        "nombre_negocio": nombre_negocio,
        "paleta": paleta_seleccionada,
        "url_logo": url_logo,
        "url_fondo_css": url_fondo_css,
        "titulo_hero": titulo_hero,
        "lema_hero": lema_hero,
        "cta_button_text": cta_button_text,
        "cta_button_link": cta_button_link,
        "descripcion_presentacion": descripcion_presentacion,
        "beneficios": beneficios,
        "comentarios_html": comentarios_html,
        "wa_link": wa_link,
        "has_facebook": has_facebook,
        "facebook_url": facebook_url,
        "has_instagram": has_instagram,
        "instagram_url": instagram_url,
        "direccion": direccion,
        "open_status_text": open_status_text,
        "next_time_info": next_time_info,
        "horarios_detallados": data_json.get('horarios_detallados', []) # Pass detailed hours
    }
    
    # --- CREACIÓN DE CARPETA DE ASSETS ADICIONALES (JS, CSS) ---
    # Para la V2, necesitaremos archivos JS externos.
    os.makedirs(f"{ruta_web}/js", exist_ok=True)


    # --- SELECCIÓN DE MAQUETA ---
    html_final = ""
    if version == "v2":
        # ---> AQUÍ SE GENERA LA MAQUETA 2 (Si el botón fue V2)
        html_final = generar_maqueta_v2(datos_web)
    else:
        # ---> AQUÍ SE GENERA LA MAQUETA 1 (Si el botón fue V1 o por defecto)
        html_final = generar_maqueta_v1(datos_web)

    # --- ESCRITURA DE ARCHIVOS ADICIONALES (JS para V2) ---
    if version == "v2":
        js_menu_hamburguesa = """
function openNav() {
    document.getElementById("menu-movil").style.width = "100%";
}

function closeNav() {
    document.getElementById("menu-movil").style.width = "0%";
}
        """
        js_scroll_suave = """
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
        """
        with open(f"{ruta_web}/js/main.js", "w", encoding="utf-8") as f:
            f.write(js_menu_hamburguesa)
        with open(f"{ruta_web}/js/scroll.js", "w", encoding="utf-8") as f:
            f.write(js_scroll_suave)

    with open(f"{ruta_web}/index.html", "w", encoding="utf-8") as f:
        f.write(html_final)
    
    return f"[OK] Sitio creado en: {ruta_web}"