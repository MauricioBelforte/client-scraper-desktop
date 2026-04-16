import os
import json
import warnings
import time
# Silenciar advertencia de deprecación de google.generativeai
warnings.filterwarnings("ignore", category=FutureWarning)

import google.generativeai as genai
from dotenv import load_dotenv
from google.api_core import exceptions as google_exceptions
from src.constants import PALETAS_COLORES

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configurar la API KEY de Gemini
try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("No se encontró la variable de entorno GOOGLE_API_KEY. Asegúrate de que tu archivo .env está configurado.")
    genai.configure(api_key=api_key)
except Exception as e:
    print(f"[ERROR] Error critico al configurar la API de Gemini: {e}")

# Lista de modelos a probar en orden de preferencia (Restaurados a petición del usuario)
MODELOS_A_PROBAR = [
   
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-1.5-flash-latest",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
    "gemini-1.5-pro",
    "gemini-2.0-flash-exp",
    "gemini-1.5-flash",
]

def generar_contenido_ia(nombre_negocio, data_json):
    """
    Intenta generar contenido creativo para un sitio web usando una lista de modelos de Gemini con fallback.

    Args:
        nombre_negocio (str): El nombre del negocio.
        data_json (dict): Un diccionario con los datos del negocio (scraper).

    Returns:
        dict: Un diccionario con 'titulo_hero' y 'descripcion', o None si todos los modelos fallan.
    """
    
    # --- LÓGICA DE AHORRO DE TOKENS ---
    # Verificamos si la categoría ya tiene una paleta definida en constants.py.
    # Si ya tiene paleta, NO le pedimos colores a la IA.
    solicitar_colores = True
    texto_busqueda = (data_json.get('categoria', '') + " " + nombre_negocio).lower()
    
    for datos in PALETAS_COLORES.values():
        if any(keyword in texto_busqueda for keyword in datos["categorias"]):
            solicitar_colores = False
            break
            
    # Construcción dinámica del prompt
    instruccion_colores = ""
    json_colores = ""
    
    if solicitar_colores:
        instruccion_colores = """
    7. Estética Visual (Sugerencia de Colores):
        - Basado en el rubro, sugiere 3 colores en formato HEX.
        - `color_primario`: Color principal para botones y destacados (ej: #FF5733).
        - `color_fondo`: Color de fondo general (ej: #FFFFFF para salud, #111111 para bares).
        - `color_texto`: Color del texto principal (debe contrastar con el fondo)."""
        
        json_colores = """,
      "sugerencia_colores": {{
        "color_primario": "#...",
        "color_fondo": "#...",
        "color_texto": "#..."
      }}"""
    
    prompt = f"""
    Actúa como un experto en Copywriting Web y SEO Local.
    OBJETIVO: Generar contenido para un negocio de la categoría: "{data_json.get('categoria', 'Negocio Local')}".
    IMPORTANTE: La categoría manda. Si el nombre del negocio es ambiguo (ej: "Tercer Tiempo"), IGNORA su significado literal y céntrate 100% en la categoría (ej: si es "Cervecería", habla de cerveza y comida, NO de deportes).
    
    INFORMACIÓN DEL NEGOCIO:
    - Nombre: {nombre_negocio}
    - Rubro/Categoría: {data_json.get('categoria', 'Negocio Local')}
    - Rating Google Maps: {data_json.get('rating', 'N/A')}
    - Dirección: {data_json.get('direccion', 'Zona céntrica')}
    - Opiniones de Clientes (Úsalas para detectar fortalezas y tono): {str(data_json.get('comentarios', [])[:6])}

    INSTRUCCIONES DE REDACCIÓN:
    1. Tono: Profesional, atractivo y relevante para el rubro.
    2. Hero Title: Un eslogan impactante y corto (Máximo 6 palabras).
    3. Lema: Una frase de autoridad o propuesta de valor (Máximo 5 palabras).
    4. Descripción: Un párrafo de bienvenida de 2 a 3 líneas que resalte la esencia del negocio.
    5. Beneficios: 3 puntos fuertes o características únicas del negocio (Máximo 4 palabras cada uno).
    6. Botón CTA (Call to Action):
        - `cta_button_text`: Texto para el botón principal (ej: "Ver Menú", "Reservar Mesa", "Explorar Cervezas", "Contactar").
        - `cta_button_link`: El enlace al que debe apuntar el botón (ej: "#menu" si es un restaurante, "#contacto" si es un servicio, o un enlace de WhatsApp).
    {instruccion_colores}
    
    OUTPUT ESPERADO (JSON RAW):
    Responde ÚNICAMENTE con un objeto JSON válido (sin bloques de código markdown) con esta estructura:
    {{
      "titulo_hero": "...",
      "lema_corto": "...",
      "descripcion": "Breve bienvenida.",
      "beneficios": ["Beneficio 1", "Beneficio 2", "Beneficio 3"],
      "cta_button_text": "Contactar",
      "cta_button_link": "#"{json_colores}
    }}
    """

    for nombre_modelo in MODELOS_A_PROBAR:
        MAX_RETRIES = 2
        for attempt in range(MAX_RETRIES):
            try:
                print(f">> Intentando generar contenido con {nombre_modelo} (Intento {attempt + 1}/{MAX_RETRIES})...")
                model = genai.GenerativeModel(nombre_modelo)
                response = model.generate_content(prompt)
                
                texto_limpio = response.text.replace('```json', '').replace('```', '').strip()
                textos_ai = json.loads(texto_limpio)
                
                if all(k in textos_ai for k in ("titulo_hero", "descripcion", "beneficios", "cta_button_text", "cta_button_link")):
                    print(f"[OK] Exito. Contenido generado por '{nombre_modelo}' para {nombre_negocio}.")
                    return textos_ai
                else:
                    print(f"[AVISO] El modelo '{nombre_modelo}' devolvio un JSON con formato incorrecto. Reintentando con el siguiente.")
                    break # Ir al siguiente modelo
            except google_exceptions.ResourceExhausted as e:
                delay = 31
                print(f"[AVISO] Cuota excedida para {nombre_modelo}. Reintentando en {delay} segundos...")
                time.sleep(delay)
                # El bucle continuará con el siguiente intento
            except Exception as e:
                # Sanitize error message for printing on Windows consoles to prevent 'charmap' codec errors
                error_message = str(e).encode('ascii', 'ignore').decode('ascii')
                print(f"[ERROR] Error con el modelo '{nombre_modelo}': {error_message}. Probando el siguiente modelo de respaldo...")
                break # Ir al siguiente modelo

    print(f"[FALLO] Fallaron todos los modelos de IA para '{nombre_negocio}'. El generador usara textos por defecto.")
    return None

def limpiar_datos_ia(data_json):
    """
    Usa la IA para normalizar y limpiar los datos del negocio (teléfonos, nombres, etc).
    
    Args:
        data_json (dict): Datos crudos del scraper.
        
    Returns:
        dict: Datos limpios o el mismo diccionario original si falla.
    """
    prompt = f"""
    Actúa como un analista de datos experto. Tu tarea es limpiar y estandarizar el siguiente JSON de un negocio local.
    
    JSON ENTRADA:
    {json.dumps(data_json, ensure_ascii=False)}
    
    INSTRUCCIONES:
    1. Nombre: Capitalizar correctamente (Title Case). Eliminar emojis o sufijos innecesarios.
    2. Teléfono: Estandarizar a formato internacional (+54 9 ...) si es posible, o local legible.
    3. Redes: Eliminar parámetros de tracking (?fbclid=...) de las URLs de Facebook/Instagram.
    4. Dirección: Corregir errores tipográficos evidentes.
    
    Responde SOLO con el JSON corregido (sin bloques de código markdown).
    """

    for nombre_modelo in MODELOS_A_PROBAR:
        MAX_RETRIES = 2
        for attempt in range(MAX_RETRIES):
            try:
                print(f">> Intentando limpiar datos con {nombre_modelo} (Intento {attempt + 1}/{MAX_RETRIES})...")
                model = genai.GenerativeModel(nombre_modelo)
                response = model.generate_content(prompt)
                texto_limpio = response.text.replace('```json', '').replace('```', '').strip()
                datos_limpios = json.loads(texto_limpio)
                print(f"[LISTO] Datos limpiados con IA ({nombre_modelo})")
                return datos_limpios
            except google_exceptions.ResourceExhausted as e:
                delay = 31
                print(f"[AVISO] Cuota excedida para {nombre_modelo}. Reintentando en {delay} segundos...")
                time.sleep(delay)
            except Exception as e:
                # Sanitize error message for printing on Windows consoles
                error_message = str(e).encode('ascii', 'ignore').decode('ascii')
                print(f"[AVISO] Fallo limpieza con {nombre_modelo}: {error_message}")
                break # Ir al siguiente modelo
            
    print("[ERROR] No se pudieron limpiar los datos con IA. Se usaran los originales.")
    return data_json

def generar_datos_demo(categoria):
    """
    Genera datos ficticios para un negocio de una categoría específica para fines de demostración.
    """
    prompt = f"""
    Actúa como un generador de datos sintéticos para pruebas de software.
    Tu tarea es inventar un perfil de negocio realista para la categoría: "{categoria}".
    Ubicación: Trelew, Chubut, Argentina.
    
    Genera un JSON con esta estructura exacta:
    {{
      "nombre": "Nombre Creativo del Negocio",
      "categoria": "{categoria}",
      "direccion": "Calle Nueva 123, Trelew, Chubut",
      "telefono": "+54 9 280 4123456",
      "rating": "4.8",
      "horarios_detallados": [
        "Lunes: 09:00-13:00, 16:00-20:00",
        "Martes: 09:00-13:00, 16:00-20:00",
        "Miércoles: 09:00-13:00, 16:00-20:00",
        "Jueves: 09:00-13:00, 16:00-20:00",
        "Viernes: 09:00-13:00, 16:00-20:00",
        "Sábado: 10:00-14:00",
        "Domingo: Cerrado"
      ],
      "comentarios": [
        {{"autor": "Nombre 1", "texto": "Reseña positiva corta...", "rating": "5 estrellas"}},
        {{"autor": "Nombre 2", "texto": "Reseña positiva corta...", "rating": "5 estrellas"}}
      ],
      "facebook": "https://facebook.com/demo",
      "instagram": "https://instagram.com/demo"
    }}
    """

    for nombre_modelo in MODELOS_A_PROBAR:
        MAX_RETRIES = 2
        for attempt in range(MAX_RETRIES):
            try:
                print(f">> Intentando generar demo con {nombre_modelo} (Intento {attempt + 1}/{MAX_RETRIES})...")
                model = genai.GenerativeModel(nombre_modelo)
                response = model.generate_content(prompt)
                texto_limpio = response.text.replace('```json', '').replace('```', '').strip()
                datos = json.loads(texto_limpio)
                datos["categoria"] = categoria # Forzamos la categoría solicitada para evitar alucinaciones
                return datos
            except google_exceptions.ResourceExhausted as e:
                delay = 31
                print(f"[AVISO] Cuota excedida para {nombre_modelo}. Reintentando en {delay} segundos...")
                time.sleep(delay)
            except Exception as e:
                # Sanitize error message for printing on Windows consoles
                error_message = str(e).encode('ascii', 'ignore').decode('ascii')
                print(f"[AVISO] Fallo generación demo con {nombre_modelo}: {error_message}")
                break # Ir al siguiente modelo
            
    return None