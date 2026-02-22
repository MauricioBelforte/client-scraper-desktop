# src/utils.py
# Utilidades generales para la aplicación y gestión de datos

def calcular_calidad_lead(lead):
    """
    Calcula un puntaje de calidad para un lead (negocio) basado en la completitud de sus datos.
    Se utiliza para ordenar la lista de prospectos y mostrar primero los más prometedores
    (aquellos con más material para generar una web demo completa).
    """
    score = 0
    
    # 0. Estado de Propuesta - FILTRO PRINCIPAL
    # Si ya se envió propuesta, penalizamos fuertemente para enviarlo al fondo de la lista.
    if lead.get('propuesta_enviada'):
        score -= 2000

    # 0.5. Sitio Web - PENALIZACIÓN MEDIA
    # Si ya tiene sitio web, restamos puntos porque es menos prioritario que los que no tienen.
    if lead.get('website') and "No tiene" not in str(lead.get('website')):
        score -= 200

    # 1. Teléfono - MÁXIMA PRIORIDAD (Contacto directo)
    telefono = lead.get('telefono', '')
    # Validamos que no sea un placeholder de "Sin teléfono"
    if telefono and "Sin" not in str(telefono) and "No" not in str(telefono):
        score += 50

    # 2. Email - SEGUNDA PRIORIDAD
    email = lead.get('email', '')
    if email and "No detectado" not in str(email):
        score += 40

    # 3. Instagram - TERCERA PRIORIDAD
    instagram = lead.get('instagram', '')
    if instagram and "instagram.com" in instagram:
        score += 30

    # --- Bonificaciones por contenido (Para la calidad de la Web Demo) ---

    # Facebook
    facebook = lead.get('facebook', '')
    if facebook and "facebook.com" in facebook:
        score += 15

    # Comentarios (Testimonios)
    comentarios = lead.get('comentarios') or []
    if comentarios:
        score += 10
        # Bonificación por cantidad (hasta 5 comentarios extra suman puntos)
        score += min(len(comentarios), 5) * 2
        
    # Imágenes
    imagenes = lead.get('imagenes') or []
    if imagenes:
        score += 10
        # Bonificación por cantidad
        score += min(len(imagenes), 5) * 2
        
    # Horarios
    if lead.get('horarios'):
        score += 5
        
    return score

def ordenar_leads_por_prioridad(lista_leads):
    """
    Ordena una lista de leads (diccionarios) por su puntaje de calidad (descendente).
    """
    # Ordenamos de mayor a menor puntaje (reverse=True)
    return sorted(lista_leads, key=calcular_calidad_lead, reverse=True)