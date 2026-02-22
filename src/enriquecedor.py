# src/enriquecedor.py
import os
import json
import time
import random
import re
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import src.constants as constantes

def buscar_datos_externos(driver, nombre, categoria, log_callback=None):
    """
    Busca en Google Search datos de contacto (Email, Redes) para un negocio.
    Abre una nueva pestaña, busca y extrae información de los resultados.
    """
    if log_callback: log_callback(f"🔍 Buscando en Google: {nombre} ({categoria})...")
    nuevos_datos = {}
    
    try:
        original_window = driver.current_window_handle
        driver.switch_to.new_window('tab')
        
        # Búsqueda OSINT: Combinamos nombre, ciudad y palabras clave
        query = f"{nombre} {categoria} Trelew contacto email instagram facebook"
        driver.get(f"https://www.google.com/search?q={query.replace(' ', '+')}")
        time.sleep(random.uniform(2.5, 4)) # Espera humana
        
        # 1. Buscar Emails SOLO en los resultados
        try:
            contenedor = driver.find_element(By.ID, "search")
            texto_analisis = contenedor.get_attribute("innerHTML")
        except:
            texto_analisis = driver.find_element(By.TAG_NAME, "body").text

        # Regex para emails
        emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", texto_analisis)
        # Filtrar basura técnica
        emails_validos = [e for e in emails if not any(x in e for x in ['google.com', 'w3.org', 'rating', 'example', 'sentry', 'png', 'jpg', 'noreply'])]
        if emails_validos:
            nuevos_datos['email'] = emails_validos[0]

        # 2. Buscar Redes Sociales
        social_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'facebook.com') or contains(@href, 'instagram.com')]")
        for link in social_links:
            url = link.get_attribute("href")
            if not url: continue
            if "sharer" in url or "login" in url or "google.com" in url: continue
            
            if "instagram.com" in url and "instagram" not in nuevos_datos:
                nuevos_datos['instagram'] = url
            elif "facebook.com" in url and "facebook" not in nuevos_datos:
                nuevos_datos['facebook'] = url
        
        driver.close()
        driver.switch_to.window(original_window)
        
    except Exception as e:
        if log_callback: log_callback(f"⚠️ Falló búsqueda externa: {e}")
        try:
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
        except: pass
    
    return nuevos_datos

def ejecutar_enriquecimiento_global(gestor_datos, log_callback):
    """
    Ejecuta el proceso de enriquecimiento para TODOS los archivos JSON existentes.
    """
    if log_callback: log_callback("🚀 Iniciando Enriquecedor Global...")
    
    # 1. Configuración del Driver (Anti-detección)
    options = Options()
    options.add_argument("--lang=es-419")
    options.add_argument("--disable-blink-features=AutomationControlled") 
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--start-maximized") 
    profile_dir = os.path.join(os.getcwd(), constantes.CARPETA_PERFIL)
    options.add_argument(f"--user-data-dir={profile_dir}")
    
    driver = None
    archivo_estado = "estado_enriquecimiento.json"
    
    try:
        # 2. Cargar Estado Anterior
        estado = {"archivo": "", "indice": 0}
        if os.path.exists(archivo_estado):
            try:
                with open(archivo_estado, 'r') as f:
                    estado = json.load(f)
                if log_callback: log_callback(f"🔄 Reanudando desde: {estado['archivo']} (Lead #{estado['indice']})")
            except: pass

        # 3. Obtener lista de archivos ordenada alfabéticamente
        archivos = sorted(gestor_datos.obtener_archivos())
        archivos = [f + ".json" for f in archivos]
        
        # Filtrar archivos ya procesados
        inicio_archivos = 0
        if estado["archivo"] in archivos:
            inicio_archivos = archivos.index(estado["archivo"])
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
        })

        # 4. Bucle Principal de Archivos
        for i in range(inicio_archivos, len(archivos)):
            nombre_archivo = archivos[i]
            if log_callback: log_callback(f"📂 Procesando archivo: {nombre_archivo}...")
            
            datos_archivo = gestor_datos.cargar_datos(nombre_archivo)
            if not datos_archivo: continue

            items_lista = sorted(list(datos_archivo.items()), key=lambda x: x[0])
            
            inicio_leads = 0
            if nombre_archivo == estado["archivo"]:
                inicio_leads = estado["indice"]
            
            cambios_en_archivo = False
            
            # 5. Bucle de Leads dentro del archivo
            for j in range(inicio_leads, len(items_lista)):
                nombre_lead, datos_lead = items_lista[j]
                
                # Actualizar estado actual
                estado["archivo"] = nombre_archivo
                estado["indice"] = j
                with open(archivo_estado, 'w') as f:
                    json.dump(estado, f)

                # --- CRITERIOS DE SALTO ---
                if datos_lead.get("propuesta_enviada"):
                    continue
                    
                tiene_email = datos_lead.get("email") and "No detectado" not in datos_lead.get("email")
                tiene_redes = (datos_lead.get("instagram") and "No detectado" not in datos_lead.get("instagram")) or \
                              (datos_lead.get("facebook") and "No detectado" not in datos_lead.get("facebook"))
                
                if tiene_email and tiene_redes:
                    continue

                # --- ENRIQUECIMIENTO ---
                if log_callback: log_callback(f"🔍 Buscando datos para: {nombre_lead} ({j+1}/{len(items_lista)} del archivo)...")
                categoria = datos_lead.get("categoria", "")
                
                # Usamos la función local del módulo
                nuevos_datos = buscar_datos_externos(driver, nombre_lead, categoria, log_callback)
                
                if nuevos_datos:
                    actualizado = False
                    for k, v in nuevos_datos.items():
                        if v and datos_lead.get(k) == 'No detectado':
                            datos_lead[k] = v
                            actualizado = True
                    
                    if actualizado:
                        datos_archivo[nombre_lead] = datos_lead
                        cambios_en_archivo = True
                        gestor_datos.guardar_datos(nombre_archivo, datos_archivo)
                
                time.sleep(random.uniform(2, 5))

            estado["indice"] = 0 
            
        if log_callback: log_callback("✅ Enriquecimiento Global Finalizado.")
        if os.path.exists(archivo_estado):
            os.remove(archivo_estado)
        messagebox.showinfo("Proceso Terminado", "Se han revisado todas las fichas exitosamente.")

    except Exception as e:
        if log_callback: log_callback(f"❌ Error en proceso global: {e}")
    finally:
        if driver: driver.quit()