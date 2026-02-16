# src/constants.py
# Este archivo contendrá todas las constantes y configuraciones estáticas de la aplicación.

RUBROS_SUGERIDOS = [
    "Gimnasios", "Restaurantes", "Talleres Mecánicos", "Peluquerías",
    "Odontólogos", "Abogados", "Inmobiliarias", "Cervecerías",
    "Veterinarias", "Pizzerías", "Farmacias", "Escuelas de danza",
    "Estudios Contables", "Ferreterías", "Centros de Estética",
    "Barberías", "Psicólogos", "Nutricionistas", "Kinesiólogos",
    "Arquitectos", "Constructoras", "Salones de Eventos",
    "Servicios de Catering", "Escuelas de Idiomas", "Pet Shops",
    "Mueblerías", "Casas de Repuestos", "Heladerías", "Cafeterías"
]

# Nombres de las carpetas del sistema.
# Si se requiere cambiar el nombre de una carpeta, se cambia el texto de la derecha, no el nombre de la variable.
DATA_FOLDER = "fichas_leads"
PROFILE_FOLDER = "selenium_profile"

# --- CONFIGURACIÓN DE ESTILO (UI) ---

# Colores Generales
COLOR_BG = "#f8f9fa"
COLOR_PRIMARY = "#1a73e8"
COLOR_WHITE = "white"
COLOR_BORDER = "#dee2e6"
COLOR_TEXT_MUTED = "#6c757d"
COLOR_TEXT_DARK = "#212529"
COLOR_TEXT_LABEL = "#495057"
COLOR_STATUS_BG = "#e9ecef"

# Colores de Acciones/Marcas
COLOR_WHATSAPP = "#25D366"
COLOR_DANGER = "#dc3545"
COLOR_FACEBOOK = "#3b5998"
COLOR_INSTAGRAM = "#833AB4"
COLOR_EMAIL = "#ffc107"
COLOR_DARK_BTN = "#343a40"
COLOR_INFO_BTN = "#17a2b8"
COLOR_SEARCH_BTN = "#6f42c1"

# Fuentes
FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_SUBTITLE = ("Segoe UI", 14, "bold")
FONT_NORMAL = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_SMALL = ("Segoe UI", 9)
FONT_SMALL_BOLD = ("Segoe UI", 9, "bold")
FONT_ITALIC = ("Segoe UI", 10, "italic")
FONT_TINY = ("Segoe UI", 8, "italic")
FONT_LINK = ("Segoe UI", 10, "underline")

# --- TEXTOS DE LA INTERFAZ (UI) ---
APP_TITLE = "Trelew Digital Leads - Prospector de Negocios"
HEADER_TEXT = "TRELEW LEAD PROSPECTOR"
SEARCH_FRAME_TITLE = " Gestión de Búsquedas "
LABEL_NEW_SEARCH = "Nueva Búsqueda (Google Maps):"
BTN_SEARCH = "🔍 BUSCAR Y GUARDAR"
BTN_ENRICH = "🌍 ENRIQUECER TODOS"
LABEL_LOAD_FILE = "📂 Cargar Ficha Guardada:"
BTN_LOAD = "CARGAR"
LABEL_RESULTS = "Emprendimientos Encontrados"
COL_NAME = "Nombre"
COL_STATUS = "Estado"
CARD_PLACEHOLDER = "Selecciona un comercio\npara ver el detalle"
STATUS_READY = "Listo para prospectar en Trelew"
CARD_HEADER = "DETALLE DEL CLIENTE"
LABEL_PHONE = "📱 Teléfono:"
LABEL_WEB = "🌐 Web:"
LABEL_CITY = "📍 Ciudad:"
VALUE_NO_WEB = "No posee (Oportunidad)"
VALUE_CITY = "Trelew, Chubut"
BTN_CONTACT_ALL = "CONTACTAR POR TODOS LOS MEDIOS"
BTN_VIEW_SHEET = "📄 VER FICHA TÉCNICA (WEB DEMO)"
BTN_GOOGLE_SEARCH = "🌍 BUSCAR DATOS EXTRA (GOOGLE)"
SHEET_HEADER = "DATOS PÚBLICOS PARA WEB DEMO"
SECTION_COMMENTS = "Últimos Comentarios (Testimonios):"
MSG_NO_COMMENTS = "No se encontraron comentarios recientes."
FOOTER_NOTE = "* Los datos se guardan automáticamente en la carpeta 'fichas_leads'"

# --- MENSAJES Y ALERTAS ---
MSG_WARN_RUBRO = "Ingresa un rubro comercial para comenzar."
MSG_ERR_NO_PHONE = "Este comercio no dispone de un teléfono válido."
MSG_WARN_NO_LIST = "Primero debes buscar o cargar una lista de emprendimientos."
MSG_CONFIRM_ENRICH = "Esto buscará datos extra en Google para {} contactos.\nEl proceso puede tardar unos minutos.\n¿Deseas continuar?"
MSG_BROWSER_LOCKED = "No se pudo iniciar el robot.\n\nCierra todas las ventanas de Chrome (o el script de configuración) antes de buscar."