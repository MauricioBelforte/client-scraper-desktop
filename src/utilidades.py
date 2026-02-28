import webbrowser
from tkinter import messagebox

def create_whatsapp_url(nombre, tel):
    """
    Genera la URL de la API de WhatsApp para iniciar un chat.
    Limpia el número y formatea el mensaje.
    """
    if "Sin" in str(tel) or not tel:
        return None

    # Limpieza de número para formato internacional
    numero_limpio = "".join(filter(str.isdigit, str(tel)))
    
    # Eliminar 0 inicial si existe (ej: 0280 -> 280) para evitar 5490...
    if numero_limpio.startswith("0"):
        numero_limpio = numero_limpio[1:]
    
    # Eliminar '15' (prefijo móvil local) si existe y el número es largo
    # Ej: 280 15 4123456 (12 dígitos) -> 280 4123456 (10 dígitos)
    if len(numero_limpio) >= 11 and "15" in numero_limpio:
        numero_limpio = numero_limpio.replace("15", "", 1)
    
    # Heurística simple para Argentina (si no tiene código de país, asumimos 549)
    if not numero_limpio.startswith("54"):
        numero_limpio = "549" + numero_limpio

    mensaje = f"Hola {nombre}, vi tu negocio en Maps. Noté que no tienen sitio web propio y me gustaría enviarte una propuesta para potenciar su presencia digital en Trelew. ¿Te interesaría conversar?"
    # Codificación básica de URL para espacios
    mensaje_codificado = mensaje.replace(' ', '%20')
    
    return f"https://wa.me/{numero_limpio}?text={mensaje_codificado}"

def abrir_whatsapp(nombre, tel):
    """
    Abre el navegador con el chat de WhatsApp listo para enviar.
    """
    url = create_whatsapp_url(nombre, tel)
    
    if url:
        webbrowser.open(url)
    else:
        messagebox.showwarning("Error", "Este comercio no dispone de un teléfono válido.")