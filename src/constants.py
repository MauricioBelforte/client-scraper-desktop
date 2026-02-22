# src/constants.py
# Este archivo contendrá todas las constantes y configuraciones estáticas de la aplicación.

RUBROS_SUGERIDOS = [
    "Gimnasios", "Restaurantes", "Talleres Mecánicos", "Peluquerías",
    "Odontólogos", "Abogados", "Inmobiliarias", "Cervecerías", "Veterinarias",
    "Pizzerías", "Farmacias", "Escuelas de danza", "Estudios Contables",
    "Ferreterías", "Centros de Estética", "Barberías", "Psicólogos",
    "Nutricionistas", "Kinesiólogos", "Arquitectos", "Constructoras",
    "Salones de Eventos", "Servicios de Catering", "Escuelas de Idiomas",
    "Pet Shops", "Mueblerías", "Casas de Repuestos", "Heladerías", "Barbería",   # <-- Añadir
    "Tattoo",     # <-- Añadir
    "Bares",      # <-- Añadir
    "Cafeterías", "Pastelerías", "Panaderías", "Kioscos", "Carnicerías",
    "Pollerías", "Verdulerías"
]

# Nombres de las carpetas del sistema.
# Si se requiere cambiar el nombre de una carpeta, se cambia el texto de la derecha, no el nombre de la variable.
CARPETA_DATOS = "fichas_leads"
CARPETA_PERFIL = "selenium_profile"

# --- CONFIGURACIÓN DE ESTILO (UI) ---

# Colores Generales
COLOR_FONDO = "#f8f9fa"
COLOR_PRIMARIO = "#1a73e8"
COLOR_BLANCO = "white"
COLOR_BORDE = "#dee2e6"
COLOR_TEXTO_TENUE = "#6c757d"
COLOR_TEXTO_OSCURO = "#212529"
COLOR_TEXTO_ETIQUETA = "#495057"
COLOR_FONDO_ESTADO = "#e9ecef"
COLOR_ENLACE = "blue"
COLOR_FONDO_COMENTARIO = "#f1f3f4"
COLOR_TEXTO_COMENTARIO = "#5f6368"

# Colores de Acciones/Marcas
COLOR_WHATSAPP = "#25D366"
COLOR_PELIGRO = "#dc3545"
COLOR_FACEBOOK = "#3b5998"
COLOR_INSTAGRAM = "#833AB4"
COLOR_EMAIL = "#ffc107"
COLOR_BTN_OSCURO = "#343a40"
COLOR_BTN_INFO = "#17a2b8"
COLOR_BTN_BUSCAR = "#6f42c1"

# Fuentes
FUENTE_TITULO = ("Segoe UI", 18, "bold")
FUENTE_SUBTITULO = ("Segoe UI", 14, "bold")
FUENTE_NORMAL = ("Segoe UI", 10)
FUENTE_NEGRITA = ("Segoe UI", 10, "bold")
FUENTE_PEQUENA = ("Segoe UI", 9)
FUENTE_PEQUENA_NEGRITA = ("Segoe UI", 9, "bold")
FUENTE_ITALICA = ("Segoe UI", 10, "italic")
FUENTE_DIMINUTA = ("Segoe UI", 8, "italic")
FUENTE_LINK = ("Segoe UI", 10, "underline")

# --- TEXTOS DE LA INTERFAZ (UI) ---
TITULO_APP = "Trelew Digital Leads - Prospector de Negocios"
TEXTO_ENCABEZADO = "TRELEW LEAD PROSPECTOR"
TITULO_FRAME_BUSQUEDA = " Gestión de Búsquedas "
ETIQUETA_NUEVA_BUSQUEDA = "Nueva Búsqueda (Google Maps):"
BTN_BUSCAR = "🔍 BUSCAR Y GUARDAR"
BTN_MODO_RAPIDO = "⚡ MODO RÁPIDO (JS)"
BTN_MODO_HUMANO = "👤 MODO HUMANO (TECLADO)"
BTN_ENRIQUECER = "🌍 ENRIQUECER TODOS"
ETIQUETA_CARGAR_ARCHIVO = "📂 Cargar Ficha Guardada:"
BTN_CARGAR = "CARGAR"
ETIQUETA_RESULTADOS = "Emprendimientos Encontrados"
COLUMNA_NOMBRE = "Nombre"
COLUMNA_ESTADO = "Estado"
TEXTO_PLACEHOLDER_CARD = "Selecciona un comercio\npara ver el detalle"
ESTADO_LISTO = "Listo para prospectar en Trelew"
ENCABEZADO_CARD = "DETALLE DEL CLIENTE"
ETIQUETA_TELEFONO = "📱 Teléfono:"
ETIQUETA_WEB = "🌐 Web:"
ETIQUETA_CIUDAD = "📍 Ciudad:"
VALOR_SIN_WEB = "No posee (Oportunidad)"
VALOR_CIUDAD = "Trelew, Chubut"
BTN_CONTACTAR_TODOS = "CONTACTAR POR TODOS LOS MEDIOS"
BTN_VER_FICHA = "📄 VER FICHA TÉCNICA (WEB DEMO)"
BTN_BUSCAR_GOOGLE = "🌍 BUSCAR DATOS EXTRA (GOOGLE)"
ENCABEZADO_FICHA = "DATOS PÚBLICOS PARA WEB DEMO"
SECCION_COMENTARIOS = "Últimos Comentarios (Testimonios):"
MSJ_SIN_COMENTARIOS = "No se encontraron comentarios recientes."
NOTA_PIE = "* Los datos se guardan automáticamente en la carpeta 'fichas_leads'"

# --- MENSAJES Y ALERTAS ---
MSJ_ADVERTENCIA_RUBRO = "Ingresa un rubro comercial para comenzar."
MSJ_ERROR_SIN_TELEFONO = "Este comercio no dispone de un teléfono válido."
MSJ_ADVERTENCIA_SIN_LISTA = "Primero debes buscar o cargar una lista de emprendimientos."
MSJ_CONFIRMAR_ENRIQUECIMIENTO = "Esto buscará datos extra en Google para {} contactos.\nEl proceso puede tardar unos minutos.\n¿Deseas continuar?"
MSJ_NAVEGADOR_BLOQUEADO = "No se pudo iniciar el robot.\n\nCierra todas las ventanas de Chrome (o el script de configuración) antes de buscar."

# --- SISTEMA DE PALETAS DE COLORES (DEFINICIÓN CENTRAL) ---
PALETAS_COLORES = {
    "NOCTURNA_GOURMET": {
        "colores": {
            "primario": "#efc355",       # Dorado
            "fondo": "#111111",          # Negro
            "texto": "#e9e9e9",          # Blanco humo
            "texto_inverso": "#181818",  # Texto oscuro sobre dorado
            "overlay": "#000000b8",      # Oscurecer fondo
            "fondo_tarjeta": "#ffffff"   # Fondo tarjeta
        },
        "categorias": [
            "restaurante", "restaurantes", "bar", "bares", "cerveceria", "cervecería", 
            "cervecerias", "cervecerías", "pub", "pubs", "disco", "discos", "discoteca", 
            "discotecas", "hamburgueseria", "hamburguesería", "hamburgueserias", 
            "hamburgueserías", "pizzeria", "pizzería", "pizzerias", "pizzerías", 
            "sushi", "sushis", "parrilla", "parrillas", "gastrono", "gastronó", 
            "gastronomia", "gastronomía", "cafeteria", "cafetería", "cafeterias", 
            "cafeterías", "evento", "eventos", "catering", "caterings", "hotel", 
            "hoteles", "bodega", "bodegas", "vinoteca", "vinotecas"
        ]
    },
    "DULCE_PASTEL": {
        "colores": {
            "primario": "#29b6f6",       # Celeste
            "fondo": "#fffde7",          # Amarillo Pastel muy claro
            "texto": "#4e342e",          # Marrón Oscuro (Chocolate)
            "texto_inverso": "#000000",  # Negro sobre celeste para legibilidad
            "overlay": "#0000004f",      # Overlay estándar
            "fondo_tarjeta": "#fce4ec"   # Rosa Pastel
        },
        "categorias": [
            "heladeria", "heladería", "heladerias", "heladerías", "pasteleria", 
            "pastelería", "pastelerias", "pastelerías", "panaderia", "panadería", 
            "panaderias", "panaderías", "confiteria", "confitería", "confiterias", 
            "confiterías", "reposteria", "repostería", "reposterias", "reposterías",
            "chocolate", "chocolates", "chocolateria", "chocolatería"
        ]
    },
    "SALUD_PROFESIONAL": {
        "colores": {
            "primario": "#0d6efd",       # Azul Profesional
            "fondo": "#dbdce2",          
            "texto": "#212529",          # Gris oscuro
            "texto_inverso": "#ffffff",  # Blanco sobre azul
            "overlay": "#ffffff00",      # Aclarar fondo (Overlay blanco)
            "fondo_tarjeta": "#ffffff"   # Fondo tarjeta
        },
        "categorias": [
            "medico", "médico", "medicos", "médicos", "odont", "odontologo", 
            "odontólogo", "odontologos", "odontólogos", "odontologia", "odontología", 
            "kinesio", "kinesiologo", "kinesiólogo", "kinesiologos", "kinesiólogos", 
            "kinesiologia", "kinesiología", "salud", "clinic", "clínic", "clinica", 
            "clínica", "clinicas", "clínicas", "farmacia", "farmacias", "abogado", 
            "abogados", "abogacia", "abogacía", "contab", "contador", "contadores", 
            "contable", "contables", "estudio", "estudios", "inmobiliaria", 
            "inmobiliarias", "arquitecto", "arquitectos", "arquitectura", 
            "veterinaria", "veterinarias", "veterinario", "veterinarios", "psicolog", 
            "psicologo", "psicólogo", "psicologos", "psicólogos", "psicologia", 
            "psicología", "nutricion", "nutrición", "nutricionista", "nutricionistas", 
            "consultorio", "consultorios"
        ]
    },
    "ESTETICA_BELLEZA": {
        "colores": {
            "primario": "#d63384",       # Rosa fuerte
            "fondo": "#fff0f5",          # Lavanda muy claro / Blanco rosado
            "texto": "#ffe8ea",          
            "texto_inverso": "#ffffff",  # Blanco sobre rosa
            "overlay": "#0000004f",      # Oscurecer fondo (Overlay negro semitransparente)   
            "fondo_tarjeta": "#ffe5fa"   # Fondo tarjeta (Rosa claro solicitado)
        },
        "categorias": [
            "peluqu", "peluqueria", "peluquería", "peluquerias", "peluquerías", 
            "peluquero", "peluqueros", "estetic", "estétic", "estetica", "estética", 
            "esteticas", "estéticas", "belleza", "uñas", "uña", "makeup", "maquillaje", 
            "moda", "modas", "ropa", "ropas", "indumentaria", "zapateria", "zapatería", 
            "zapaterias", "zapaterías", "lenceria", "lencería", "lencerias", 
            "lencerías", "danza", "danzas", "spa", "spas", "masaje", "masajes", 
            "masajista", "masajistas", "depilacion", "depilación", "manicura", 
            "manicuria", "manicuría", "pedicura", "pedicuria", "pedicuría", 
            "barberia", "barbería", "barberias", "barberías"
        ]
    },
    "ESTILO_MADERA": {
        "colores": {
            "primario": "#A0522D",       # Marrón Sienna (Madera)
            "fondo": "#F8F8F8",          # Blanco humo / Gris muy claro
            "texto": "#514a4a",          # Blanco
            "texto_inverso": "#ffffff",  # Blanco
            "overlay": "#00000047",      # Oscuro semitransparente
            "fondo_tarjeta": "#ffffff"   # Blanco
        },
        "categorias": [
            "muebleria", "mueblería", "mueblerias", "mueblerías", "muebles", "mueble", 
            "decoracion", "decoración", "decoraciones", "interiorismo", "sofa", "sofá", 
            "sofas", "sofás", "colchon", "colchón", "colchones", "colchonería", 
            "colchonerias", "carpinteria", "carpintería", "carpinterias", "carpinterías"
        ]
    },
    "NATURALEZA_FRESCA": {
        "colores": {
            "primario": "#28a745",       # Verde éxito (Bootstrap Success Green)
            "fondo": "#f0fff0",          # Honeydew (Verde muy pálido)
            "texto": "#eceaea",          
            "texto_inverso": "#ffffff",  # Blanco
            "overlay": "#00000066",      # Overlay oscuro para contraste
            "fondo_tarjeta": "#ffffff"   # Fondo tarjeta blanco
        },
        "categorias": [
            "verduleria", "verdulería", "verdulerias", "verdulerías", "botanica", 
            "botánica", "botanicas", "botánicas", "jardineria", "jardinería", 
            "jardinerias", "jardinerías", "jardinero", "jardineros", "vivero", 
            "viveros", "floreria", "florería", "florerias", "florerías", "organico", 
            "orgánico", "organicos", "orgánicos", "dietetica", "dietética", 
            "dieteticas", "dietéticas", "fruteria", "frutería", "fruterias", 
            "fruterías", "paisajismo", "paisajista"
        ]
    },   
    "BARBERIA_VINTAGE": {
        "categorias": ["barberia", "barber", "barbería"],
        "colores": {
            "primario": "#c89f68",      # Un dorado/bronce vintage
            "fondo": "#1a1a1a",         # Fondo oscuro
            "texto": "#f0f0f0",         # Texto claro
            "texto_inverso": "#111111"
        }
    },
    "TATTOO_INK": {
        "categorias": ["tattoo", "tatuajes", "tatoo", "tatuador"],
        "colores": {
            "primario": "#e53935",      # Un rojo intenso como acento
            "fondo": "#121212",         # Fondo muy oscuro, casi negro
            "texto": "#ffffff",         # Texto blanco puro
            "texto_inverso": "#000000"
        }
    },
    "FUERZA_TECNICA": {
        "colores": {
            "primario": "#ff4500",       # Naranja Rojizo (OrangeRed)
            "fondo": "#1a1a1a",          # Gris muy oscuro
            "texto": "#f0f0f0",          # Blanco grisáceo
            "texto_inverso": "#ffffff",  # Blanco sobre naranja
            "overlay": "#000000d9",      # Oscurecer fondo fuerte
            "fondo_tarjeta": "#ffffff"   # Fondo tarjeta
        },
        "categorias": [
            "taller", "talleres", "mecanic", "mecánic", "mecanico", "mecánico", 
            "mecanicos", "mecánicos", "mecanica", "mecánica", "gimnasio", "gimnasios", 
            "gym", "crossfit", "fitness", "ferreteria", "ferretería", "ferreterias", 
            "ferreterías", "construc", "construccion", "construcción", "constructora", 
            "constructoras", "obra", "obras", "repuestos", "repuesto", "pet shop", 
            "pet shops", "petshop", "petshops", "computacion", "computación", "tecnic", 
            "técnic", "tecnico", "técnico", "tecnicos", "técnicos", "tecnica", 
            "técnica", "reparacion", "reparación", "reparaciones", "kiosco", "kioscos", 
            "quiosco", "quioscos", "carniceria", "carnicería", "carnicerias", 
            "carnicerías", "polleria", "pollería", "pollerias", "pollerías", 
            "electricista", "electricistas", "electricidad", "plomero", "plomeros", 
            "plomeria", "plomería", "pintureria", "pinturería", "pinturerias", 
            "pinturerías"
        ]
    }
}