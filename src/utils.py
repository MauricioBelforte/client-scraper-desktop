# src/utils.py
# Utilidades generales para la aplicación y gestión de datos
import datetime

def get_open_status_and_next_time(detailed_hours):
    """
    Calcula si el negocio está abierto o cerrado y la próxima hora de cambio de estado.
    Asume la hora local del sistema.

    Args:
        detailed_hours (list): Lista de strings con el formato "Día: HH:MM-HH:MM".
                               Ej: ["Lunes: 09:00-18:00", "Martes: 09:00-18:00", "Sábado: 10:00-14:00"]

    Returns:
        tuple: (status_text, next_time_text)
               status_text: "Abierto ahora", "Cerrado", "Abierto hasta HH:MM", "Cerrado hasta HH:MM"
               next_time_text: "Hoy HH:MM", "Mañana HH:MM", "Día HH:MM"
    """
    now = datetime.datetime.now()
    current_weekday = now.weekday() # Lunes es 0, Domingo es 6
    current_time = now.time()

    day_map = {
        "lunes": 0, "martes": 1, "miércoles": 2, "miercoles": 2, "jueves": 3,
        "viernes": 4, "sábado": 5, "sabado": 5, "domingo": 6
    }
    reverse_day_map = {v: k.capitalize() for k, v in day_map.items()}

    today_hours = []
    all_parsed_hours = []

    for entry in detailed_hours:
        parts = entry.split(': ', 1)
        if len(parts) < 2:
            continue
        day_str = parts[0].lower().strip()
        time_ranges_str = parts[1]

        day_num = day_map.get(day_str)
        if day_num is None:
            continue

        for time_range_str in time_ranges_str.split(', '):
            if 'cerrado' in time_range_str.lower():
                continue
            
            try:
                start_str, end_str = time_range_str.split('-')
                start_time = datetime.datetime.strptime(start_str.strip(), '%H:%M').time()
                end_time = datetime.datetime.strptime(end_str.strip(), '%H:%M').time()
                
                all_parsed_hours.append({
                    'day_num': day_num,
                    'start': start_time,
                    'end': end_time,
                    'day_name': reverse_day_map[day_num]
                })

                if day_num == current_weekday:
                    today_hours.append({
                        'start': start_time,
                        'end': end_time
                    })
            except ValueError:
                continue

    today_hours.sort(key=lambda x: x['start'])

    is_open = False
    next_change_time = None
    status_text = "Cerrado"
    next_time_text = ""

    for period in today_hours:
        if period['start'] <= current_time < period['end']:
            is_open = True
            next_change_time = period['end']
            status_text = f"Abierto hasta {next_change_time.strftime('%H:%M')}"
            break
    
    if not is_open:
        for period in today_hours:
            if current_time < period['start']:
                next_change_time = period['start']
                status_text = "Cerrado"
                next_time_text = f"Abre hoy a las {next_change_time.strftime('%H:%M')}"
                break
        
        if not next_change_time:
            future_hours = []
            for i in range(1, 8): # Check next 7 days
                next_day_num = (current_weekday + i) % 7
                for period in all_parsed_hours:
                    if period['day_num'] == next_day_num:
                        future_hours.append({
                            'day_num': period['day_num'],
                            'start': period['start'],
                            'day_name': period['day_name'],
                            'offset': i # Days from now
                        })
            
            future_hours.sort(key=lambda x: (x['offset'], x['start']))
            
            if future_hours:
                next_period = future_hours[0]
                next_day_name = next_period['day_name']
                next_open_time = next_period['start']
                
                if next_period['offset'] == 1:
                    next_time_text = f"Abre mañana a las {next_open_time.strftime('%H:%M')}"
                else:
                    next_time_text = f"Abre el {next_day_name} a las {next_open_time.strftime('%H:%M')}"
            else:
                next_time_text = "Horarios no disponibles"

    return status_text, next_time_text

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