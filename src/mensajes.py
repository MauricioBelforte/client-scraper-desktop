import urllib.parse

# --- CONFIGURACIÓN DE PLANTILLAS ---
# Define aquí tus modelos y textos por rubro.
# La clave (key) es la palabra que buscaremos en la categoría del negocio.

TEMPLATES_POR_RUBRO = {
    # Rubros Profesionales y de Servicios
    "abogado": {
        "intro": "Estoy ofreciendo mis servicios a distintos estudios jurídicos y profesionales locales.",
        "modelos": [
            "Modelo 1: ",
            "Modelo 2: ",
            "Modelo 3: ",
            "Modelo 4: "
        ]
    },
    "inmobiliaria": {
        "intro": "Estoy ofreciendo mis servicios a distintas inmobiliarias y agentes del sector local.",
        "modelos": [
            "Modelo 1: https://valle-azul-propiedades.netlify.app/",
            "Modelo 2: https://patagonia-urbana-inmobiliaria.netlify.app/",
            "Modelo 3: https://patagonia-habitat-inmobiliaria.netlify.app/",
            "Modelo 4: https://valle-azul-inmobiliaria.netlify.app/"
        ]
    },
    "arquitecto": {
        "intro": "Estoy ofreciendo mis servicios a arquitectos y estudios de arquitectura para que puedan mostrar sus proyectos.",
        "modelos": ["Modelo 1: ", "Modelo 2: "]
    },
    "contable": {
        "intro": "Estoy ofreciendo mis servicios a estudios contables y asesores financieros.",
        "modelos": ["Modelo 1: ", "Modelo 2: "]
    },
    "constructora": {
        "intro": "Estoy ofreciendo mis servicios a constructoras y empresas del rubro para destacar sus obras.",
        "modelos": ["Modelo 1: ", "Modelo 2: "]
    },

    # Rubros de Gastronomía
    "restaurante": {
        "intro": "Estoy ofreciendo mis servicios a distintos locales gastronomicos y restaurantes de la ciudad.",
        "modelos": ["Modelo 1: ", "Modelo 2: "]
    },
    "bar": {
        "intro": "Estoy ofreciendo mis servicios a bares y pubs de la ciudad para mostrar su carta y ambiente.",
        "modelos": ["Modelo 1: ", "Modelo 2: "]
    },
    "cafeteria": {
        "intro": "Estoy ofreciendo mis servicios a cafeterías y emprendimientos locales para destacar sus productos.",
        "modelos": ["Modelo 1: ", "Modelo 2: "]
    },
    "cerveceria": {
        "intro": "Estoy ofreciendo mis servicios a cervecerías y bares de la zona.",
        "modelos": ["Modelo 1: ", "Modelo 2: "]
    },
    "pizzeria": {
        "intro": "Estoy ofreciendo mis servicios a pizzerías y locales de comida.",
        "modelos": ["Modelo 1: ", "Modelo 2: "]
    },
    "pasteleria": {
        "intro": "Estoy ofreciendo mis servicios a pastelerías y confiterías.",
        "modelos": ["Modelo 1: ", "Modelo 2: "]
    },
    "panaderia": {
        "intro": "Estoy ofreciendo mis servicios a panaderías y locales de barrio.",
        "modelos": ["Modelo 1: ", "Modelo 2: "]
    },
    "heladeria": {
        "intro": "Estoy ofreciendo mis servicios a heladerías y locales comerciales.",
        "modelos": ["Modelo 1: ", "Modelo 2: "]
    },
    "catering": {
        "intro": "Estoy ofreciendo mis servicios a empresas de catering y organización de eventos.",
        "modelos": ["Modelo 1: ", "Modelo 2: "]
    },

    # Rubros de Salud y Bienestar
    "gimnasio": {
        "intro": "Estoy ofreciendo mis servicios a gimnasios y centros de fitness locales.",
        "modelos": ["Modelo 1: ", "Modelo 2: "]
    },
    "odontologo": {
        "intro": "Estoy ofreciendo mis servicios a odontólogos y profesionales de la salud dental de la localidad.",
        "modelos": ["Modelo 1: ", "Modelo 2: "]
    },
    "veterinaria": {
        "intro": "Estoy ofreciendo mis servicios a veterinarias y pet shops de la ciudad.",
        "modelos": ["Modelo 1: ", "Modelo 2: "]
    },
    "farmacia": {
        "intro": "Estoy ofreciendo mis servicios a farmacias y locales del sector salud.",
        "modelos": ["Modelo 1: ", "Modelo 2: "]
    },
    "psicologo": {
        "intro": "Estoy ofreciendo mis servicios a psicólogos y profesionales de la salud mental.",
        "modelos": ["Modelo 1: ", "Modelo 2: "]
    },
    "nutricionista": {
        "intro": "Estoy ofreciendo mis servicios a nutricionistas y consultorios de salud.",
        "modelos": ["Modelo 1: ", "Modelo 2: "]
    },
    "kinesiologo": {
        "intro": "Estoy ofreciendo mis servicios a kinesiólogos y centros de rehabilitación.",
        "modelos": ["Modelo 1: ", "Modelo 2: "]
    },

    # Rubros de Belleza y Estética
    "peluqueria": {
        "intro": "Estoy ofreciendo mis servicios a distintas peluquerías locales.",
        "modelos": ["Modelo 1: ", "Modelo 2: "]
    },
    "estetica": {
        "intro": "Estoy ofreciendo mis servicios a centros de estética y profesionales de la belleza.",
        "modelos": ["Modelo 1: ", "Modelo 2: "]
    },
    "barberia": {
        "intro": "Estoy ofreciendo mis servicios a barberías y peluquerías locales.",
        "modelos": ["Modelo 1: ", "Modelo 2: "]
    },
    "tattoo": {
        "intro": "Estoy ofreciendo mis servicios a estudios de tatuajes y tatuadores locales.",
        "modelos": [
            "Modelo 1: https://tinta-austral.netlify.app/", 
            "Modelo 2: https://tinta-patagonica-tattoo-studio.netlify.app/"
        ]
    },

    # Otros Rubros
    "taller": {
        "intro": "Estoy ofreciendo mis servicios a talleres mecánicos y de chapa y pintura.",
        "modelos": ["Modelo 1: ", "Modelo 2: "]
    },
    "local": {
        "intro": "Estoy ofreciendo mis servicios a locales comerciales y tiendas para destacar sus productos y atraer clientes.",
        "modelos": ["Modelo 1: ", "Modelo 2: "]
    },
}

# Configuración por defecto (si no coincide ninguna categoría)
TEMPLATE_DEFAULT = {
    "intro": "Estoy ofreciendo mis servicios a distintos negocios y profesionales locales.",
    "modelos": [
        "Modelo General 1: ",
        "Modelo General 2: "
    ]
}

def generar_mensaje_whatsapp(nombre_negocio, categoria):
    """
    Genera el mensaje de WhatsApp personalizado basado en la categoría.
    """
    categoria_lower = str(categoria).lower()
    config_seleccionada = TEMPLATE_DEFAULT
    
    # Buscar coincidencia de palabras clave
    for keyword, config in TEMPLATES_POR_RUBRO.items():
        if keyword in categoria_lower:
            config_seleccionada = config
            break
    
    # Construir lista de modelos
    lista_modelos = "\n".join(config_seleccionada["modelos"])
    
    mensaje = f"""Hola, {nombre_negocio}. Mi nombre es Mauricio Belforte, me dedico al desarrollo de páginas web. 
Soy de Trelew.

{config_seleccionada['intro']}

Si gustan pueden pasar a ver estos modelos de plantillas que estoy trabajando para su rubro. Se pueden adaptar y modificar rápidamente:
{lista_modelos}

Sino también podemos trabajar en una página con un diseño más elaborado y funcionalidades más específicas pero a un costo mayor.

Pueden ver más de mis trabajos en mi portfolio: https://mauriciobelforte.github.io/mi-portfolio/.

Si les sirve, no duden en contactarme. Saludos!"""

    return urllib.parse.quote(mensaje)
