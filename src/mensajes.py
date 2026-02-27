import urllib.parse

# --- CONFIGURACIÓN DE PLANTILLAS POR ARCHIVO JSON ---
# Las claves son los nombres de los archivos (sin .json)
# Ejemplos: "Cervecerías", "Restaurantes", "Abogados", etc.

TEMPLATES_POR_ARCHIVO = {
    # Rubros Profesionales y de Servicios
    "Abogados": {
        "intro": "Estoy ofreciendo mis servicios a distintos estudios jurídicos y profesionales locales.",
        "modelos": [
            "Modelo 1: https://patagonia-urbana-inmobiliaria.netlify.app/",
            "Modelo 2: https://valle-azul-propiedades.netlify.app/",
            "Modelo 3: https://espacio-psicologico-conexion.netlify.app/",
            "Modelo 4: https://tinta-austral.netlify.app/"
        ]
    },
    "Inmobiliarias": {
        "intro": "Estoy ofreciendo mis servicios a distintas inmobiliarias y agentes del sector local.",
        "modelos": [
            "Modelo 1: https://valle-azul-propiedades.netlify.app/",
            "Modelo 2: https://patagonia-urbana-inmobiliaria.netlify.app/",
            "Modelo 3: https://patagonia-habitat-inmobiliaria.netlify.app/",
            "Modelo 4: https://valle-azul-inmobiliaria.netlify.app/"
        ]
    },

    # Rubros de Gastronomía
    "Restaurantes": {
        "intro": "Estoy ofreciendo mis servicios a distintos locales gastronomicos y restaurantes de la ciudad.",
        "modelos": [
            "Modelo 1: https://sabores-del-valle.netlify.app/",
            "Modelo 2: https://sabor-patagonico.netlify.app/",
            "Modelo 3: https://centro-psicologico-conexion-interior.netlify.app/",
            "Modelo 4: https://patagonia-urbana-inmobiliaria.netlify.app/",
            "Modelo 5: https://tinta-austral.netlify.app/"
        ]
    },
    "Bares": {
        "intro": "Estoy ofreciendo mis servicios a bares y pubs de la ciudad para mostrar su carta y ambiente.",
        "modelos": [
            "Modelo 1: https://centro-psicologico-conexion-interior.netlify.app/",
            "Modelo 2: https://patagonia-urbana-inmobiliaria.netlify.app/"
        ]
    },
    "Cafeterías": {
        "intro": "Estoy ofreciendo mis servicios a cafeterías y emprendimientos locales para destacar sus productos.",
        "modelos": [
            "Modelo 1: https://centro-psicologico-conexion-interior.netlify.app/",
            "Modelo 2: https://patagonia-urbana-inmobiliaria.netlify.app/"
        ]
    },
    "Cervecerías": {
        "intro": "Estoy ofreciendo mis servicios a cervecerías y bares de la zona.",
        "modelos": [
            "Modelo 1: https://cerveceria-el-galpon-patagonico.netlify.app/",
            "Modelo 2: https://cerveceria-rio-chubut.netlify.app/",
            "Modelo 3: https://patagonia-habitat-inmobiliaria.netlify.app/",
            "Modelo 4: https://centro-psicologico-conexion-interior.netlify.app/",
            "Modelo 5: https://tinta-austral.netlify.app/"
        ]
    },
    "Pizzerías": {
        "intro": "Estoy ofreciendo mis servicios a pizzerías y locales de comida.",
        "modelos": [
            "Modelo 1: https://centro-psicologico-conexion-interior.netlify.app/",
            "Modelo 2: https://patagonia-urbana-inmobiliaria.netlify.app/"
        ]
    },
    "Panaderías": {
        "intro": "Estoy ofreciendo mis servicios a panaderías y locales de barrio.",
        "modelos": [
            "Modelo 1: https://centro-psicologico-conexion-interior.netlify.app/",
            "Modelo 2: https://patagonia-urbana-inmobiliaria.netlify.app/"
        ]
    },
    "Carnicerías": {
        "intro": "Estoy ofreciendo mis servicios a carnicerías y locales de barrio para destacar sus productos.",
        "modelos": [
            "Modelo 1: https://centro-psicologico-conexion-interior.netlify.app/",
            "Modelo 2: https://patagonia-urbana-inmobiliaria.netlify.app/"
        ]
    },
    "Kioscos": {
        "intro": "Estoy ofreciendo mis servicios a kioscos y pequeños comercios para destacar sus productos.",
        "modelos": [
            "Modelo 1: https://centro-psicologico-conexion-interior.netlify.app/",
            "Modelo 2: https://patagonia-urbana-inmobiliaria.netlify.app/"
        ]
    },

    # Rubros de Salud y Bienestar
    "Gimnasios": {
        "intro": "Estoy ofreciendo mis servicios a gimnasios y centros de fitness locales.",
        "modelos": [
            "Modelo 1: https://espacio-psicologico-conexion.netlify.app/",
            "Modelo 2: https://patagonia-urbana-inmobiliaria.netlify.app/"
        ]
    },
    "Odontólogos": {
        "intro": "Estoy ofreciendo mis servicios a odontólogos y profesionales de la salud dental de la localidad.",
        "modelos": [
            "Modelo 1: https://espacio-psicologico-conexion.netlify.app/",
            "Modelo 2: https://patagonia-urbana-inmobiliaria.netlify.app/"
        ]
    },
    "Veterinarias": {
        "intro": "Estoy ofreciendo mis servicios a veterinarias, clínicas veterinarias y pet shops de la ciudad.",
        "modelos": [
            "Modelo 1: https://espacio-psicologico-conexion.netlify.app/",
            "Modelo 2: https://patagonia-urbana-inmobiliaria.netlify.app/"
        ]
    },
    "Pet Shops": {
        "intro": "Estoy ofreciendo mis servicios a veterinarias, pet shops y tiendas de productos para mascotas.",
        "modelos": [
            "Modelo 1: https://espacio-psicologico-conexion.netlify.app/",
            "Modelo 2: https://patagonia-urbana-inmobiliaria.netlify.app/"
        ]
    },
    "Nutricionistas": {
        "intro": "Estoy ofreciendo mis servicios a nutricionistas y consultorios de salud.",
        "modelos": [
            "Modelo 1: https://espacio-psicologico-conexion.netlify.app/",
            "Modelo 2: https://patagonia-urbana-inmobiliaria.netlify.app/"
        ]
    },
    "Kinesiólogos": {
        "intro": "Estoy ofreciendo mis servicios a kinesiólogos y centros de rehabilitación.",
        "modelos": [
            "Modelo 1: https://espacio-psicologico-conexion.netlify.app/",
            "Modelo 2: https://patagonia-urbana-inmobiliaria.netlify.app/"
        ]
    },

    # Rubros de Belleza y Estética
    "Peluquerías": {
        "intro": "Estoy ofreciendo mis servicios a distintas peluquerías locales.",
        "modelos": [
            "Modelo 1: https://tinta-austral.netlify.app/",
            "Modelo 2: https://patagonia-urbana-inmobiliaria.netlify.app/"
        ]
    },
    "Centros de Estética": {
        "intro": "Estoy ofreciendo mis servicios a centros de estética y profesionales de la belleza.",
        "modelos": [
            "Modelo 1: https://tinta-austral.netlify.app/",
            "Modelo 2: https://patagonia-urbana-inmobiliaria.netlify.app/"
        ]
    },
    "Barbería": {
        "intro": "Estoy ofreciendo mis servicios a barberías y peluquerías locales.",
        "modelos": [
            "Modelo 1: https://tinta-austral.netlify.app/",
            "Modelo 2: https://patagonia-urbana-inmobiliaria.netlify.app/"
        ]
    },
    "Tatuajes": {
        "intro": "Estoy ofreciendo mis servicios a estudios de tatuajes y tatuadores locales.",
        "modelos": [
            "Modelo 1: https://tinta-austral.netlify.app/",
            "Modelo 2: https://tinta-patagonica-tattoo-studio.netlify.app/",
            "Modelo 3: https://patagonia-urbana-inmobiliaria.netlify.app/",
            "Modelo 4: https://valle-azul-propiedades.netlify.app/",
            "Modelo 5: https://centro-psicologico-conexion-interior.netlify.app/"
        ]
    },

    # Otros Rubros
    "Talleres Mecánicos": {
        "intro": "Estoy ofreciendo mis servicios a talleres mecánicos y de chapa y pintura.",
        "modelos": [
            "Modelo 1: https://patagonia-urbana-inmobiliaria.netlify.app/",
            "Modelo 2: https://valle-azul-propiedades.netlify.app/"
        ]
    },
    "Mueblerías": {
        "intro": "Estoy ofreciendo mis servicios a mueblerías y locales de venta de muebles.",
        "modelos": [
            "Modelo 1: https://patagonia-urbana-inmobiliaria.netlify.app/",
            "Modelo 2: https://valle-azul-propiedades.netlify.app/"
        ]
    },
    "Verdulerías": {
        "intro": "Estoy ofreciendo mis servicios a locales comerciales y tiendas para destacar sus productos y atraer clientes.",
        "modelos": [
            "Modelo 1: https://patagonia-urbana-inmobiliaria.netlify.app/",
            "Modelo 2: https://valle-azul-propiedades.netlify.app/"
        ]
    },
    "Psicólogos": {
        "intro": "Estoy ofreciendo mis servicios a psicólogos y profesionales de la salud mental.",
        "modelos": [
            "Modelo 1: https://espacio-psicologico-conexion.netlify.app/",
            "Modelo 2: https://centro-psicologico-conexion-interior.netlify.app/",
            "Modelo 3: https://patagonia-urbana-inmobiliaria.netlify.app/",
            "Modelo 4: https://valle-azul-propiedades.netlify.app/",
            "Modelo 5: https://tinta-austral.netlify.app/"
        ]
    },
    "Servicios de Catering": {
        "intro": "Estoy ofreciendo mis servicios a empresas de catering y organización de eventos.",
        "modelos": [
            "Modelo 1: https://centro-psicologico-conexion-interior.netlify.app/",
            "Modelo 2: https://patagonia-urbana-inmobiliaria.netlify.app/"
        ]
    },
}

# Configuración por defecto (si el archivo no se encuentra en el diccionario)
TEMPLATE_DEFAULT = {
    "intro": "Estoy ofreciendo mis servicios a distintos negocios y profesionales locales.",
    "modelos": [
        "Modelo 1: https://espacio-psicologico-conexion.netlify.app/",
        "Modelo 2: https://centro-psicologico-conexion-interior.netlify.app/",
        "Modelo 3: https://valle-azul-propiedades.netlify.app/",
        "Modelo 4: https://patagonia-urbana-inmobiliaria.netlify.app/",
        "Modelo 5: https://tinta-austral.netlify.app/",
    ]
}

def generar_mensaje_whatsapp(nombre_negocio, nombre_archivo):
    """
    Genera el mensaje de WhatsApp personalizado basado en el nombre del archivo JSON.
    
    IMPORTANTE: Esta función ahora funciona diferente que antes.
    
    ANTES (Sistema antiguo - DEPRECADO):
        generar_mensaje_whatsapp(nombre, categoria)  # categoria = "Cervecería artesanal"
    
    AHORA (Sistema nuevo - ACTIVO):
        generar_mensaje_whatsapp(nombre, nombre_archivo)  # nombre_archivo = "Cervecerías"
    
    Args:
        nombre_negocio (str): Nombre del negocio
        nombre_archivo (str): Nombre del archivo JSON (sin extensión), ej: "Cervecerías"
    
    Returns:
        str: Mensaje URL-encoded para WhatsApp
    
    Ejemplos:
        generar_mensaje_whatsapp("BARDO - Cerveza Artesanal", "Cervecerías")
        generar_mensaje_whatsapp("Estudio P&M", "Abogados")
        generar_mensaje_whatsapp("Unknown", "ArchivoNoConfigurado")  # Usa TEMPLATE_DEFAULT
    """
    # Obtener configuración del archivo, si no existe usar default
    config_seleccionada = TEMPLATES_POR_ARCHIVO.get(nombre_archivo, TEMPLATE_DEFAULT)
    
    # Construir lista de modelos
    lista_modelos = "\n".join(config_seleccionada["modelos"])
    
    mensaje = f"""Hola, {nombre_negocio}. Mi nombre es Mauricio Belforte, me dedico al desarrollo de páginas web. 
Soy de Trelew.

{config_seleccionada['intro']}

Si gustan pueden pasar a ver estos ejemplos de plantillas que estoy trabajando actualmente, que tienen un costo accesible y se pueden adaptar o modificar rápidamente:
{lista_modelos}

Sino también podemos trabajar en una página con un diseño más elaborado y funcionalidades más específicas pero a un costo mayor.

Pueden ver más de mis trabajos en mi portfolio: https://mauriciobelforte.github.io/mi-portfolio/.

Si les sirve, no duden en contactarme. Saludos!"""

    return urllib.parse.quote(mensaje)
