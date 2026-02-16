# src/utilidades.py
# Este módulo contendrá funciones de utilidad general que no dependen del estado de la aplicación.

import webbrowser
from tkinter import messagebox
import src.constants as constantes

def abrir_whatsapp(nombre, tel):
    """Procesa el contacto y abre el navegador con la API de WhatsApp."""
    if "Sin" in tel or not tel:
        messagebox.showwarning("Error", constantes.MSJ_ERROR_SIN_TELEFONO)
        return

    # Limpieza de número para formato internacional
    numero_limpio = "".join(filter(str.isdigit, tel))
    if not numero_limpio.startswith("54"):
        numero_limpio = "549" + numero_limpio

    mensaje = f"Hola {nombre}, vi tu negocio en Maps. Noté que no tienen sitio web propio y me gustaría enviarte una propuesta para potenciar su presencia digital en Trelew. ¿Te interesaría conversar?"
    url = f"https://wa.me/{numero_limpio}?text={mensaje.replace(' ', '%20')}"
    webbrowser.open(url)