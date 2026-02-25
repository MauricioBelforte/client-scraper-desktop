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
            "fondo_tarjeta": "#ffffff",  # Fondo tarjeta (Blanco)
            "acento": "#c69f3a",         # Dorado oscuro
            
            # --- Variables V2 ---
            "fondo_botones": "#efc355",
            "fondo_botones_hover": "#c69f3a",
            "texto_botones": "#181818",
            "texto_general": "#e9e9e9",
            "texto_hero": "#ffffff",
            "texto_cards": "#181818",    # Texto oscuro para tarjeta blanca
            "titulos": "#efc355",
            "titulo_h1": "#ffffff",
            "titulo_h2": "#e9e9e9",
            "fondo_general": "#111111",
            "fondo_cards": "#ffffff",
            "overlay_hero": "#000000b8",
            "borde_sutil": "rgba(255,255,255,0.1)",

            # --- Variables V1 (Específicas One Page) ---
            "v1_hero_titulo": "#efc355",      # Dorado impactante
            "v1_hero_lema": "#ffffff",        # Blanco puro
            "v1_boton_fondo": "#efc355",      # Botón dorado
            "v1_boton_texto": "#111111",      # Texto negro para contraste
            "v1_seccion_fondo": "#111111",    # Fondo oscuro continuo
            "v1_seccion_titulos": "#efc355",  # Títulos dorados
            "v1_seccion_texto": "#cccccc",    # Texto gris claro
            "v1_card_fondo": "#1a1a1a",       # Tarjetas gris muy oscuro
            "v1_card_texto": "#e0e0e0",       # Texto claro
            "v1_card_borde": "#333333"        # Borde sutil
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
            "primario": "#ffcfe7",       # Rosa Pastel
            "fondo": "#fffde7",          # Amarillo muy claro (Pastel) para un fondo suave y luminoso
            "texto": "#4e342e",          # Marrón oscuro para buen contraste y legibilidad
            "texto_inverso": "#4e342e",  # Marrón oscuro para texto sobre el rosa pastel (en lugar de blanco, para mejor legibilidad)
            "overlay": "#0000004f",      # 
            "fondo_tarjeta": "#ffffff",  # Fondo tarjeta blanco para mantener la limpieza visual
            "acento": "#fa9fcb",         # Rosa más claro para acentos y detalles, manteniendo la armonía pastel

            # --- Variables V2 ---
            "fondo_botones": "#ffcfe7",
            "fondo_botones_hover": "#fa9fcb",
            "texto_botones": "#4e342e",
            "texto_general": "#4e342e",
            "texto_hero": "#ffffff",
            "texto_cards": "#4e342e",
            "titulos": "#9a4972",        # Títulos suaves
            "titulo_h1": "#ffffff",
            "titulo_h2": "#4e342e",
            "fondo_general": "#fffde7",
            "fondo_cards": "#ffffff",
            "overlay_hero": "#0000004f",
            "borde_sutil": "rgba(0,0,0,0.05)",

            # --- Variables V1 (Específicas One Page) ---
            "v1_hero_titulo": "#4e342e",      # Marrón chocolate
            "v1_hero_lema": "#4e342e",
            "v1_boton_fondo": "#ffcfe7",      # Rosa pastel
            "v1_boton_texto": "#4e342e",      # Texto chocolate
            "v1_seccion_fondo": "#fffde7",    # Crema suave
            "v1_seccion_titulos": "#9a4972",  # Rosa oscuro/Frambuesa
            "v1_seccion_texto": "#5d4037",    # Marrón medio
            "v1_card_fondo": "#ffffff",       # Blanco puro
            "v1_card_texto": "#5d4037",
            "v1_card_borde": "#ffcfe7"        # Borde rosa
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
            "fondo_tarjeta": "#ffffff",  # Fondo tarjeta
            "acento": "#0b5ed7",         # Azul intenso

            # --- Variables V2 ---
            "fondo_botones": "#0d6efd",
            "fondo_botones_hover": "#0b5ed7",
            "texto_botones": "#ffffff",
            "texto_general": "#212529",
            "texto_hero": "#ffffff",
            "texto_cards": "#212529",
            "titulos": "#0d6efd",
            "titulo_h1": "#ffffff",
            "titulo_h2": "#212529",
            "fondo_general": "#dbdce2",
            "fondo_cards": "#ffffff",
            "overlay_hero": "#00000066", # Un poco de oscuridad para que el texto blanco del hero se lea
            "borde_sutil": "rgba(0,0,0,0.1)",

            # --- Variables V1 (Específicas One Page) ---
            "v1_hero_titulo": "#ffffff",      # Blanco clínico
            "v1_hero_lema": "#e3f2fd",        # Azul muy pálido
            "v1_boton_fondo": "#0d6efd",      # Azul Bootstrap
            "v1_boton_texto": "#ffffff",      # Blanco
            "v1_seccion_fondo": "#f8f9fa",    # Gris muy claro (casi blanco)
            "v1_seccion_titulos": "#0b5ed7",  # Azul oscuro
            "v1_seccion_texto": "#495057",    # Gris oscuro
            "v1_card_fondo": "#ffffff",       # Blanco
            "v1_card_texto": "#212529",       # Negro suave
            "v1_card_borde": "#dee2e6"        # Borde gris
        },
        "categorias": [
            "medico", "médico", "medicos", "médicos", "odont", "odontologo", 
            "odontólogo", "odontologos", "odontólogos", "odontologia", "odontología", 
            "kinesio", "kinesiologo", "kinesiólogo", "kinesiologos", "kinesiólogos", 
            "kinesiologia", "kinesiología", "salud", "clinic", "clínic", "clinica", 
            "clínica", "clinicas", "clínicas", "farmacia", "farmacias", 
            "veterinaria", "veterinarias", "veterinario", "veterinarios", "psicolog", 
            "psicologo", "psicólogo", "psicologos", "psicólogos", "psicologia", 
            "psicología", "nutricion", "nutrición", "nutricionista", "nutricionistas", 
            "consultorio", "consultorios"
        ]
    },
    "ELEGANTE_SERIO": {
        "colores": {
            "primario": "#95c0ff",      # Azul claro (Titulos)
            "fondo": "#313447",         # Fondo oscuro elegante
            "texto": "#c5ccd3",         # Texto gris claro
            "texto_inverso": "#152141", # Texto oscuro para botones
            "overlay": "#00000066",     # Overlay
            "fondo_tarjeta": "#ffffff", # Tarjeta blanca
            "acento": "#5280c3",        # Azul medio (Hover)

            # --- Variables V2 ---
            "fondo_botones": "#b5b5b5",
            "fondo_botones_hover": "#5280c3",
            "texto_botones": "#152141",
            "texto_botones_hover": "#ffffff",
            "texto_general": "#c5ccd3",
            "texto_hero": "#ffffff",
            "texto_cards": "#214061",
            "titulos": "#95c0ff",
            "titulo_h1": "#ffffff",
            "titulo_h2": "#e7f3ff",
            "fondo_general": "#313447",
            "fondo_cards": "#ffffff",
            "overlay_hero": "#00000066",
            "borde_sutil": "rgba(0, 0, 0, 0.1)",

            # --- Variables V1 (Específicas One Page) ---
            "v1_hero_titulo": "#ffffff",      # Blanco
            "v1_hero_lema": "#c5ccd3",        # Gris azulado claro
            "v1_boton_fondo": "#95c0ff",      # Azul claro elegante
            "v1_boton_texto": "#152141",      # Azul oscuro
            "v1_seccion_fondo": "#f4f6f8",    # Gris muy claro (profesional)
            "v1_seccion_titulos": "#152141",  # Azul marino profundo
            "v1_seccion_texto": "#4a5568",    # Gris pizarra
            "v1_card_fondo": "#ffffff",       # Blanco
            "v1_card_texto": "#2d3748",       # Gris oscuro
            "v1_card_borde": "#cbd5e0"        # Borde gris azulado
        },
        "categorias": [
            "abogado", "abogados", "abogacia", "abogacía", "contab", "contador", 
            "contadores", "contable", "contables", "estudio", "estudios", 
            "inmobiliaria", "inmobiliarias", "arquitecto", "arquitectos", 
            "arquitectura", "escribania", "escribanía", "consultora", "consultoria",
            "consultor", "consultores", "notaria", "notaría"
        ]
    },
    "ESTETICA_BELLEZA": {
        "colores": {
            "primario": "#d63384",       # Rosa fuerte
            "fondo": "#fff0f5",          # Lavanda muy claro / Blanco rosado
            "texto": "#7a3c5c",          
            "texto_inverso": "#ffffff",  # Blanco sobre rosa
            "overlay": "#0000004f",      # Oscurecer fondo (Overlay negro semitransparente)   
            "fondo_tarjeta": "#ffe5fa",  # Fondo tarjeta (Rosa claro)
            "acento": "#c21b6c",         # Rosa oscuro

            # --- Variables V2 ---
            "fondo_botones": "#d63384",
            "fondo_botones_hover": "#c21b6c",
            "texto_botones": "#ffffff",
            "texto_general": "#7a3c5c",
            "texto_hero": "#ffffff",
            "texto_cards": "#7a3c5c",
            "titulos": "#d63384",
            "titulo_h1": "#ffffff",
            "titulo_h2": "#7a3c5c",
            "fondo_general": "#fff0f5",
            "fondo_cards": "#ffe5fa",
            "overlay_hero": "#0000004f",
            "borde_sutil": "rgba(214, 51, 132, 0.1)", # Borde rosado muy sutil

            # --- Variables V1 (Específicas One Page) ---
            "v1_hero_titulo": "#ffffff",
            "v1_hero_lema": "#ffe5fa",
            "v1_boton_fondo": "#d63384",      # Rosa fuerte
            "v1_boton_texto": "#ffffff",
            "v1_seccion_fondo": "#fff0f5",    # Lavanda blush
            "v1_seccion_titulos": "#d63384",  # Rosa
            "v1_seccion_texto": "#7a3c5c",    # Púrpura oscuro
            "v1_card_fondo": "#ffffff",
            "v1_card_texto": "#7a3c5c",
            "v1_card_borde": "#f8bbd0"        # Rosa pastel borde
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
            "fondo_tarjeta": "#ffffff",  # Fondo tarjeta
            "acento": "#804020",         # Marrón oscuro

            # --- Variables V2 ---
            "fondo_botones": "#A0522D",
            "fondo_botones_hover": "#804020",
            "texto_botones": "#ffffff",
            "texto_general": "#514a4a",
            "texto_hero": "#ffffff",
            "texto_cards": "#514a4a",
            "titulos": "#A0522D",
            "titulo_h1": "#ffffff",
            "titulo_h2": "#514a4a",
            "fondo_general": "#F8F8F8",
            "fondo_cards": "#ffffff",
            "overlay_hero": "#00000047",
            "borde_sutil": "rgba(160, 82, 45, 0.1)",

            # --- Variables V1 (Específicas One Page) ---
            "v1_hero_titulo": "#ffffff",
            "v1_hero_lema": "#f0f0f0",
            "v1_boton_fondo": "#A0522D",      # Sienna
            "v1_boton_texto": "#ffffff",
            "v1_seccion_fondo": "#fafafa",    # Casi blanco
            "v1_seccion_titulos": "#8B4513",  # SaddleBrown
            "v1_seccion_texto": "#514a4a",    # Gris cálido
            "v1_card_fondo": "#ffffff",
            "v1_card_texto": "#514a4a",
            "v1_card_borde": "#d7ccc8"        # Marrón muy claro
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
            "texto": "#1e4d2b",          # Verde muy oscuro (Corregido para contraste)
            "texto_inverso": "#ffffff",  # Blanco
            "overlay": "#00000066",      # Overlay oscuro para contraste
            "fondo_tarjeta": "#ffffff",  # Fondo tarjeta blanco
            "acento": "#218838",         # Verde oscuro

            # --- Variables V2 ---
            "fondo_botones": "#28a745",
            "fondo_botones_hover": "#218838",
            "texto_botones": "#ffffff",
            "texto_general": "#1e4d2b",
            "texto_hero": "#ffffff",
            "texto_cards": "#1e4d2b",
            "titulos": "#28a745",
            "titulo_h1": "#ffffff",
            "titulo_h2": "#1e4d2b",
            "fondo_general": "#f0fff0",
            "fondo_cards": "#ffffff",
            "overlay_hero": "#00000066",
            "borde_sutil": "rgba(40, 167, 69, 0.1)",

            # --- Variables V1 (Específicas One Page) ---
            "v1_hero_titulo": "#ffffff",
            "v1_hero_lema": "#e8f5e9",
            "v1_boton_fondo": "#28a745",      # Verde
            "v1_boton_texto": "#ffffff",
            "v1_seccion_fondo": "#f1f8e9",    # Verde muy claro
            "v1_seccion_titulos": "#1b5e20",  # Verde bosque
            "v1_seccion_texto": "#33691e",    # Verde oliva oscuro
            "v1_card_fondo": "#ffffff",
            "v1_card_texto": "#1e4d2b",
            "v1_card_borde": "#c8e6c9"        # Verde pálido
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
            "texto_inverso": "#111111",
            "overlay": "#000000b8",     # Overlay oscuro
            "fondo_tarjeta": "#2a2a2a", # Tarjeta oscura (Gris muy oscuro)
            "acento": "#a67f4d",        # Bronce oscuro

            # --- Variables V2 ---
            "fondo_botones": "#c89f68",
            "fondo_botones_hover": "#a67f4d",
            "texto_botones": "#111111",
            "texto_general": "#f0f0f0",
            "texto_hero": "#ffffff",
            "texto_cards": "#f0f0f0",   # Texto claro sobre tarjeta oscura
            "titulos": "#c89f68",
            "titulo_h1": "#ffffff",
            "titulo_h2": "#f0f0f0",
            "fondo_general": "#1a1a1a",
            "fondo_cards": "#2a2a2a",
            "overlay_hero": "#000000b8",
            "borde_sutil": "rgba(255,255,255,0.05)", # Borde claro sutil

            # --- Variables V1 (Específicas One Page) ---
            "v1_hero_titulo": "#c89f68",      # Dorado vintage
            "v1_hero_lema": "#f0f0f0",
            "v1_boton_fondo": "#c89f68",
            "v1_boton_texto": "#111111",
            "v1_seccion_fondo": "#1a1a1a",    # Oscuro
            "v1_seccion_titulos": "#c89f68",  # Dorado
            "v1_seccion_texto": "#dcdcdc",    # Gris claro
            "v1_card_fondo": "#2a2a2a",       # Gris oscuro
            "v1_card_texto": "#dcdcdc",
            "v1_card_borde": "#444444"
        }
    },
    "TATTOO_INK": {
        "categorias": ["tattoo", "tatuajes", "tatoo", "tatuador"],
        "colores": {
            "primario": "#e53935",      # Un rojo intenso como acento
            "fondo": "#121212",         # Fondo muy oscuro, casi negro
            "texto": "#ffffff",         # Texto blanco puro
            "texto_inverso": "#000000", # Negro
            "overlay": "#000000b3",     # Overlay muy oscuro (casi negro)
            "fondo_tarjeta": "#1e1e1e", # Tarjeta gris oscuro (casi negro)
            "acento": "#c62828",        # Rojo oscuro

            # --- Variables V2 ---
            "fondo_botones": "#e53935",
            "fondo_botones_hover": "#c62828",
            "texto_botones": "#ffffff", # Blanco sobre rojo
            "texto_general": "#ffffff",
            "texto_hero": "#ffffff",
            "texto_cards": "#ffffff",   # Blanco sobre tarjeta oscura
            "titulos": "#e53935",
            "titulo_h1": "#ffffff",
            "titulo_h2": "#ffffff",
            "fondo_general": "#121212",
            "fondo_cards": "#1e1e1e",
            "overlay_hero": "#000000d9",
            "borde_sutil": "rgba(255,255,255,0.08)",

            # --- Variables V1 (Específicas One Page) ---
            "v1_hero_titulo": "#ffffff",
            "v1_hero_lema": "#e53935",        # Rojo
            "v1_boton_fondo": "#e53935",
            "v1_boton_texto": "#ffffff",
            "v1_seccion_fondo": "#000000",    # Negro puro
            "v1_seccion_titulos": "#ffffff",  # Blanco
            "v1_seccion_texto": "#b0b0b0",    # Gris medio
            "v1_card_fondo": "#121212",       # Casi negro
            "v1_card_texto": "#e0e0e0",
            "v1_card_borde": "#333333"
        }
    },
    "FUERZA_TECNICA": {
        "colores": {
            "primario": "#ff4500",       # Naranja Rojizo (OrangeRed)
            "fondo": "#1a1a1a",          # Gris muy oscuro
            "texto": "#f0f0f0",          # Blanco grisáceo
            "texto_inverso": "#ffffff",  # Blanco sobre naranja
            "overlay": "#000000d9",      # Oscurecer fondo fuerte
            "fondo_tarjeta": "#ffffff",  # Fondo tarjeta (Blanco)
            "acento": "#cc3700",         # Naranja oscuro

            # --- Variables V2 ---
            "fondo_botones": "#ff4500",
            "fondo_botones_hover": "#cc3700",
            "texto_botones": "#ffffff",
            "texto_general": "#f0f0f0",
            "texto_hero": "#ffffff",
            "texto_cards": "#1a1a1a",    # Texto oscuro sobre tarjeta blanca (Inverso del general)
            "titulos": "#ff4500",
            "titulo_h1": "#ffffff",
            "titulo_h2": "#f0f0f0",
            "fondo_general": "#1a1a1a",
            "fondo_cards": "#ffffff",
            "overlay_hero": "#000000d9",
            "borde_sutil": "rgba(255,255,255,0.1)",

            # --- Variables V1 (Específicas One Page) ---
            "v1_hero_titulo": "#ff4500",      # Naranja industrial
            "v1_hero_lema": "#ffffff",
            "v1_boton_fondo": "#ff4500",
            "v1_boton_texto": "#ffffff",
            "v1_seccion_fondo": "#212121",    # Gris oscuro industrial
            "v1_seccion_titulos": "#ff4500",
            "v1_seccion_texto": "#f5f5f5",    # Blanco humo
            "v1_card_fondo": "#333333",       # Gris maquinaria
            "v1_card_texto": "#ffffff",
            "v1_card_borde": "#ff4500"        # Borde naranja
        },
        "categorias": [
            "taller", "talleres", "mecanic", "mecánic", "mecanico", "mecánico", 
            "mecanicos", "mecánicos", "mecanica", "mecánica", "gimnasio", "gimnasios", 
            "gym", "crossfit", "fitness", "ferreteria", "ferretería", "ferreterias", 
            "ferreterías", "construc", "construccion", "construcción", "constructora", 
            "constructoras", "obra", "obras", "repuestos", "repuesto", 
            "computacion", "computación", "tecnic",
            "técnic", "tecnico", "técnico", "tecnicos", "técnicos", "tecnica", 
            "técnica", "reparacion", "reparación", "reparaciones", "kiosco", "kioscos", 
            "quiosco", "quioscos",
            "electricista", "electricistas", "electricidad", "plomero", "plomeros", 
            "plomeria", "plomería", "pintureria", "pinturería", "pinturerias", 
            "pinturerías"
        ]
    },
    "MASCOTAS_VIBRANTE": {
        "colores": {
            "primario": "#fdee52",      # Amarillo vibrante (Botones)
            "fondo": "#292929",         # Gris oscuro (Secciones)
            "texto": "#ffffff",         # Blanco
            "texto_inverso": "#12121f", # Azul oscuro casi negro (Texto botones)
            "overlay": "#00000000",     # Transparente (Solicitado)
            "fondo_tarjeta": "#333333", # Gris medio
            "acento": "#e7abc3",        # Rosa (Títulos secciones)

            # --- Variables V2 ---
            "fondo_botones": "#fdee52",
            "fondo_botones_hover": "#e7abc3",
            "texto_botones": "#12121f",
            "texto_botones_hover": "#12121f",
            "texto_general": "#ffffff",
            "texto_hero": "#272727",    # Título Hero oscuro
            "texto_cards": "#ffffff",
            "titulos": "#e7abc3",
            "titulo_h1": "#272727",
            "titulo_h2": "#e7abc3",
            "fondo_general": "#292929",
            "fondo_cards": "#333333",
            "overlay_hero": "#00000000",
            "borde_sutil": "#3d3a43",

            # --- Variables V1 (Específicas One Page) ---
            "v1_hero_titulo": "#272727",
            "v1_hero_lema": "#65edff",
            "v1_boton_fondo": "#fdee52",
            "v1_boton_texto": "#12121f",
            "v1_seccion_fondo": "#292929",
            "v1_seccion_titulos": "#e7abc3",
            "v1_seccion_texto": "#ffffff",
            "v1_card_fondo": "#333333",
            "v1_card_texto": "#ffffff",
            "v1_card_borde": "#3d3a43"
        },
        "categorias": [
            "pet shop", "pet shops", "petshop", "petshops", "mascota", "mascotas", 
            "alimento balanceado", "forrajeria", "forrajería"
        ]
    },
    "CARNICERIA_CLASICA": {
        "colores": {
            "primario": "#c8102e",      # Rojo clásico
            "fondo": "#f8f9fa",         # Gris muy claro (limpio)
            "texto": "#212529",         # Negro suave
            "texto_inverso": "#ffffff", # Blanco
            "overlay": "#0000001a",     # Overlay muy sutil para el hero
            "fondo_tarjeta": "#ffffff", # Tarjetas blancas
            "acento": "#a41e22",        # Rojo oscuro para hover

            # --- Variables V2 ---
            "fondo_botones": "#c8102e",
            "fondo_botones_hover": "#a41e22",
            "texto_botones": "#ffffff",
            "texto_botones_hover": "#ffffff",
            "texto_general": "#212529",
            "texto_hero": "#ffffff",    # Texto blanco sobre imagen de hero
            "texto_cards": "#212529",
            "titulos": "#c8102e",
            "titulo_h1": "#ffffff",
            "titulo_h2": "#212529",
            "fondo_general": "#f8f9fa",
            "fondo_cards": "#ffffff",
            "overlay_hero": "#0000004d", # Overlay para que el texto blanco del hero se lea
            "borde_sutil": "#dee2e6",

            # --- Variables V1 (Específicas One Page) ---
            "v1_hero_titulo": "#ffffff",
            "v1_hero_lema": "#ffffff",
            "v1_boton_fondo": "#c8102e",
            "v1_boton_texto": "#ffffff",
            "v1_seccion_fondo": "#f8f9fa",
            "v1_seccion_titulos": "#a41e22",
            "v1_seccion_texto": "#212529",
            "v1_card_fondo": "#ffffff",
            "v1_card_texto": "#212529",
            "v1_card_borde": "#dee2e6"
        },
        "categorias": [
            "carniceria", "carnicería", "carnicerias", "carnicerías",
            "polleria", "pollería", "pollerias", "pollerías"
        ]
    }
}