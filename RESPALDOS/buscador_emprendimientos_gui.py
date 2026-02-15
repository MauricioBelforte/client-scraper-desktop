import tkinter as tk
from tkinter import ttk, messagebox
import threading
import random
import time
import json
import os
import webbrowser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def create_driver_with_profile():
    options = Options()
    options.add_argument("--lang=es-419")
    options.add_argument("--start-maximized")
    profile_dir = os.path.join(os.getcwd(), "selenium_profile")
    options.add_argument(f"--user-data-dir={profile_dir}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
        })
    except Exception:
        pass
    return driver


def find_scrollable_container(driver, item_selector='div[data-review-id]'):
    # Busca el contenedor con scroll que contiene al menos un elemento de reseña.
    script = '''
    const sel = arguments[0];
    const items = document.querySelectorAll(sel);
    if (!items || items.length === 0) return null;

    // Para cada item, subimos por los padres hasta encontrar uno con overflow scrollable
    for (let i = 0; i < items.length; i++){
        let parent = items[i].parentElement;
        while (parent && parent !== document.body){
            const style = window.getComputedStyle(parent);
            const overflowY = style.overflowY;
            if ((overflowY === 'auto' || overflowY === 'scroll' || parent.scrollTop > 0) && parent.scrollHeight > parent.clientHeight){
                return parent;
            }
            parent = parent.parentElement;
        }
    }

    // Fallback: buscar cualquier elemento scrollable que contenga alguno de los items
    const candidates = Array.from(document.querySelectorAll('*')).filter(e => {
        const st = window.getComputedStyle(e);
        return (st.overflowY === 'auto' || st.overflowY === 'scroll') && e.scrollHeight > e.clientHeight;
    });
    for (let c of candidates){
        for (let it of items){
            if (c.contains(it)) return c;
        }
    }
    return null;
    '''
    return driver.execute_script(script, item_selector)


def find_reviews_container(driver):
    # Localiza el bloque de reseñas saltando secciones como "Pedir en línea".
    script = '''
    // 1) Buscar directamente el div.m6QErb.DxyBCb que contiene scroll y las opciones de ordenar
    // Este div es el que tiene overflow:auto y contiene tanto las opciones como las reseñas
    var containers = document.querySelectorAll('div.m6QErb.DxyBCb');
    for(var i=0; i<containers.length; i++){
        var c = containers[i];
        var st = window.getComputedStyle(c);
        // Verificar que tenga scroll y contenga reseñas
        if((st.overflowY === 'auto' || st.overflowY === 'scroll') && c.scrollHeight > c.clientHeight && c.querySelector('[data-review-id]')){
            return c;
        }
    }

    // 2) Si el selector anterior falla, buscar cualquier div con scroll que contenga [data-review-id]
    var allDivs = document.querySelectorAll('div');
    for(var i=0; i<allDivs.length; i++){
        var d = allDivs[i];
        var st = window.getComputedStyle(d);
        var reviews = d.querySelectorAll('[data-review-id]');
        if((st.overflowY === 'auto' || st.overflowY === 'scroll') && d.scrollHeight > d.clientHeight && reviews.length > 0){
            // Devolver el contenedor más pequeño/profundo que tenga scroll
            if(!d.parentElement || window.getComputedStyle(d.parentElement).overflowY !== 'auto'){
                return d;
            }
        }
    }

    // 3) Fallback: buscar el primer padre scrollable del primer elemento con data-review-id
    var r = document.querySelector('[data-review-id]');
    if(r){
        var p = r.parentElement;
        while(p && p !== document.body){
            var st = window.getComputedStyle(p);
            if((st.overflowY === 'auto' || st.overflowY === 'scroll') && p.scrollHeight>p.clientHeight) return p;
            p = p.parentElement;
        }
        return r.parentElement;
    }
    return null;
    '''
    return driver.execute_script(script)


def enhanced_scroll_reviews(driver, item_selector='div[data-review-id]', pause=0.8, max_empty=5):
    # Estrategia combinada: identificar contenedor, click safe, scrollBy, WheelEvent, PageDown y MutationObserver de espera
    prev_count = 0
    empty_cycles = 0

    # Primero, intentar localizar específicamente el bloque de reseñas (salteando 'Pedir en línea')
    container = find_reviews_container(driver)
    if not container:
        # Si falla, caemos a la detección genérica por items
        container = find_scrollable_container(driver, item_selector)
    if not container:
        fallbacks = ['.section-scrollbox', 'div[role="main"]', 'div[aria-label="Reseñas"]']
        for s in fallbacks:
            container = find_scrollable_container(driver, s)
            if container:
                break

    # Si tenemos contenedor, intentar darle foco con un click en su zona central evitando headers flotantes
    if container:
        try:
            w = container.size.get('width', 300)
            h = container.size.get('height', 300)
            # escoge un punto seguro dentro del contenedor (20% desde la izquierda, 50% altura)
            x_off = int(w * 0.2)
            y_off = int(h * 0.5)
            ActionChains(driver).move_to_element_with_offset(container, x_off, y_off).click().perform()
            time.sleep(0.3)
        except Exception:
            pass

    def wait_reviews_stable(timeout=10, stable_ms=800):
        # Ejecuta un MutationObserver en la página para esperar hasta que no aparezcan nuevas reseñas
        try:
            return driver.execute_async_script(
                "var selector=arguments[0]; var timeout=arguments[1]; var stable=arguments[2]; var cb=arguments[arguments.length-1];"
                "var last=document.querySelectorAll(selector).length; var timer=setTimeout(function(){observer.disconnect(); cb(last);}, timeout*1000);"
                "var stableTimer=null; var observer=new MutationObserver(function(){var c=document.querySelectorAll(selector).length; if(c!==last){ last=c; if(stableTimer) clearTimeout(stableTimer); stableTimer=setTimeout(function(){observer.disconnect(); clearTimeout(timer); cb(last);}, stable); }});"
                "observer.observe(document, {childList:true, subtree:true});"
                "setTimeout(function(){ try{observer.disconnect();}catch(e){} cb(document.querySelectorAll(selector).length); }, timeout*1000);",
                item_selector, timeout, stable_ms)
        except Exception:
            return None

    # Bucle de scroll: repetimos hasta que no aparezcan nuevos items
    while True:
        elems = driver.find_elements(By.CSS_SELECTOR, item_selector)
        count = len(elems)
        if count > prev_count:
            empty_cycles = 0
            prev_count = count
        else:
            empty_cycles += 1
            if empty_cycles >= max_empty:
                break

        try:
            if container:
                # Scroll dentro del contenedor
                driver.execute_script("arguments[0].scrollBy(0, Math.floor(arguments[0].clientHeight*0.8));", container)
                # Disparar WheelEvent sobre el punto central visible para que burbujee correctamente
                driver.execute_script(
                    "var r=arguments[0].getBoundingClientRect(); var el=document.elementFromPoint(r.left+Math.floor(r.width/2), r.top+Math.floor(r.height/2)); if(el) el.dispatchEvent(new WheelEvent('wheel',{deltaY:800,bubbles:true,cancelable:true}));",
                    container)
                # Intentar PageDown vía teclado como respaldo
                try:
                    ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
                except Exception:
                    pass
            else:
                # Sin contenedor, operamos sobre el último elemento visible
                if elems:
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", elems[-1])
                    driver.execute_script("var r=arguments[0].getBoundingClientRect(); var el=document.elementFromPoint(r.left+Math.floor(r.width/2), r.top+Math.floor(r.height/2)); if(el) el.dispatchEvent(new WheelEvent('wheel',{deltaY:800,bubbles:true,cancelable:true}));", elems[-1])
                    try:
                        ActionChains(driver).move_to_element(elems[-1]).click().send_keys(Keys.PAGE_DOWN).perform()
                    except Exception:
                        pass
                else:
                    try:
                        ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
                    except Exception:
                        pass

        except Exception:
            try:
                # intento final: forzar scrollTop en padres desde el último elemento
                if elems:
                    driver.execute_script("var p=arguments[0]; while(p){ if(p.scrollHeight>p.clientHeight){p.scrollTop=p.scrollHeight; break;} p=p.parentElement; }", elems[-1])
                else:
                    driver.execute_script("window.scrollBy(0, window.innerHeight);")
            except Exception:
                pass

        # Esperar hasta que las reviews terminen de cargarse o timeout
        wait_reviews_stable(timeout=6, stable_ms=700)
        time.sleep(pause)

    return driver.find_elements(By.CSS_SELECTOR, item_selector)


class TrelewLeadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Trelew Digital Leads - Prospector de Negocios")
        self.root.geometry("1100x700")
        self.root.configure(bg="#f8f9fa")

        if not os.path.exists("fichas_leads"):
            os.makedirs("fichas_leads")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        self.style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=10)

        self.prospectos_datos = {}
        self.setup_ui()

    def setup_ui(self):
        header = tk.Frame(self.root, bg="#1a73e8", height=70)
        header.pack(fill="x")
        tk.Label(header, text="TRELEW LEAD PROSPECTOR", font=("Segoe UI", 18, "bold"), bg="#1a73e8", fg="white").pack(pady=15)

        search_frame = tk.LabelFrame(self.root, text=" Gestión de Búsquedas ", font=("Segoe UI", 10, "bold"), bg="#f8f9fa", pady=10, padx=10)
        search_frame.pack(fill="x", padx=20)

        rubros_sugeridos = ["Gimnasios", "Restaurantes", "Pizzerías", "Peluquerías", "Pet Shops"]
        self.entry_rubro = ttk.Combobox(search_frame, values=rubros_sugeridos, width=28)
        self.entry_rubro.pack(side="left", padx=5)
        self.entry_rubro.set("Gimnasios")

        self.btn_buscar = ttk.Button(search_frame, text="🔍 BUSCAR Y GUARDAR", command=self.start_scraping_thread)
        self.btn_buscar.pack(side="left", padx=10)

        ttk.Separator(search_frame, orient="vertical").pack(side="left", fill="y", padx=20)

        tk.Label(search_frame, text="📂 Cargar Ficha Guardada:", font=("Segoe UI", 9), bg="#f8f9fa").pack(side="left")
        self.combo_fichas = ttk.Combobox(search_frame, width=25, state="readonly")
        self.combo_fichas.pack(side="left", padx=5)
        self.actualizar_lista_fichas()

        self.btn_cargar = ttk.Button(search_frame, text="ABRIR FICHA", command=self.cargar_ficha_offline)
        self.btn_cargar.pack(side="left", padx=5)

        main_container = tk.Frame(self.root, bg="#f8f9fa")
        main_container.pack(fill="both", expand=True, padx=20, pady=10)

        left_panel = tk.Frame(main_container, bg="white", relief="flat")
        left_panel.pack(side="left", fill="both", expand=True)

        tk.Label(left_panel, text="Emprendimientos Encontrados", font=("Segoe UI", 10, "bold"), bg="white", pady=5).pack()

        columns = ("nombre", "estado")
        self.tree = ttk.Treeview(left_panel, columns=columns, show="headings")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("estado", text="Estado")
        self.tree.column("nombre", width=250)
        self.tree.column("estado", width=100)

        scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.mostrar_detalle)

        self.right_panel = tk.Frame(main_container, width=350, bg="#f8f9fa", padx=20)
        self.right_panel.pack(side="right", fill="both")
        self.right_panel.pack_propagate(False)

        self.card_placeholder = tk.Label(self.right_panel, text="Selecciona un comercio\npara ver el detalle", font=("Segoe UI", 10, "italic"), fg="#6c757d", bg="#f8f9fa", pady=100)
        self.card_placeholder.pack()

        self.detail_card = tk.Frame(self.right_panel, bg="white", highlightbackground="#dee2e6", highlightthickness=1)

        self.status_label = tk.Label(self.root, text="Listo para prospectar en Trelew", bd=1, relief="flat", anchor="w", bg="#e9ecef", padx=10)
        self.status_label.pack(side="bottom", fill="x")

    def log(self, mensaje):
        self.status_label.config(text=f"⚙️ {mensaje}")
        self.root.update_idletasks()

    def actualizar_lista_fichas(self):
        fichas = [f.replace(".json", "") for f in os.listdir("fichas_leads") if f.endswith(".json")]
        self.combo_fichas['values'] = fichas
        if fichas:
            self.combo_fichas.current(0)

    def cargar_ficha_offline(self):
        seleccion = self.combo_fichas.get()
        if not seleccion:
            return
        filepath = os.path.join("fichas_leads", f"{seleccion}.json")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                datos_cargados = json.load(f)
            self.tree.delete(*self.tree.get_children())
            self.prospectos_datos = datos_cargados
            for nombre in self.prospectos_datos:
                self.tree.insert("", "end", iid=nombre, values=(nombre, "GUARDADO 💾"))
            self.log(f"Ficha '{seleccion}' cargada exitosamente. ({len(datos_cargados)} registros)")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la ficha: {e}")

    def mostrar_detalle(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        for widget in self.detail_card.winfo_children():
            widget.destroy()
        self.card_placeholder.pack_forget()
        self.detail_card.pack(fill="x", pady=20)
        item_id = selected[0]
        nombre = self.tree.item(item_id)['values'][0]
        datos = self.prospectos_datos.get(nombre, {})
        card_header = tk.Frame(self.detail_card, bg="#1a73e8", pady=10)
        card_header.pack(fill="x")
        tk.Label(card_header, text="DETALLE DEL CLIENTE", font=("Segoe UI", 9, "bold"), bg="#1a73e8", fg="white").pack()
        body = tk.Frame(self.detail_card, bg="white", padx=15, pady=15)
        body.pack(fill="x")
        tk.Label(body, text=nombre, font=("Segoe UI", 14, "bold"), bg="white", wraplength=280, justify="center").pack(pady=(0, 10))
        self.create_info_row(body, "📱 Teléfono:", datos.get('telefono', 'No disponible'))
        self.create_info_row(body, "🌐 Web:", "No posee (Oportunidad)")
        self.create_info_row(body, "📍 Ciudad:", "Trelew, Chubut")
        tk.Frame(body, height=1, bg="#dee2e6").pack(fill="x", pady=15)
        btn_wa = tk.Button(body, text="ENVIAR PROPUESTA POR WA", bg="#25D366", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", command=lambda: self.abrir_whatsapp(nombre, datos.get('telefono', '')))
        btn_wa.pack(fill="x", pady=5)
        btn_info = tk.Button(body, text="📄 VER FICHA TÉCNICA (WEB DEMO)", bg="#17a2b8", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", command=lambda: self.mostrar_info_detallada(nombre, datos))
        btn_info.pack(fill="x", pady=5)

    def mostrar_info_detallada(self, nombre, datos):
        top = tk.Toplevel(self.root)
        top.title(f"Ficha Técnica: {nombre}")
        top.geometry("600x700")
        top.attributes('-topmost', True)
        top.configure(bg="white")
        container = tk.Frame(top, bg="white")
        container.pack(fill="both", expand=True)
        canvas = tk.Canvas(container, bg="white")
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        info_frame = tk.Frame(canvas, bg="white", padx=20)
        info_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        window_id = canvas.create_window((0, 0), window=info_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(window_id, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        tk.Label(info_frame, text="DATOS PÚBLICOS PARA WEB DEMO", font=("Segoe UI", 14, "bold"), bg="white", fg="#1a73e8", pady=15).pack()
        def add_row(label, value):
            f = tk.Frame(info_frame, bg="white", pady=8)
            f.pack(fill="x", side="top")
            tk.Label(f, text=label, font=("Segoe UI", 10, "bold"), bg="white", width=15, anchor="w", fg="#495057").pack(side="left")
            if str(value).startswith("http"):
                lbl_link = tk.Label(f, text=value, font=("Segoe UI", 10, "underline"), bg="white", fg="blue", cursor="hand2", wraplength=350, justify="left")
                lbl_link.pack(side="left", fill="x")
                lbl_link.bind("<Button-1>", lambda e: webbrowser.open(value))
            else:
                tk.Label(f, text=value, font=("Segoe UI", 10), bg="white", wraplength=350, justify="left").pack(side="left", fill="x")
            tk.Frame(info_frame, height=1, bg="#e9ecef").pack(fill="x")
        add_row("Nombre:", nombre)
        add_row("Rubro/Categoría:", datos.get("categoria", "No especificado"))
        add_row("Dirección:", datos.get("direccion", "No disponible"))
        add_row("Horarios:", datos.get("horario", "No disponible"))
        add_row("Valoración:", datos.get("rating", "Sin reseñas"))
        add_row("Teléfono:", datos.get("telefono", "Sin teléfono"))
        if datos.get("facebook"): add_row("Facebook:", datos["facebook"]) 
        if datos.get("instagram"): add_row("Instagram:", datos["instagram"]) 
        tk.Label(info_frame, text="Últimos Comentarios (Testimonios):", font=("Segoe UI", 10, "bold"), bg="white", pady=10).pack(anchor="w")
        comentarios_frame = tk.Frame(info_frame, bg="#f1f3f4", padx=10, pady=10)
        comentarios_frame.pack(fill="x")
        comentarios = datos.get("comentarios", [])
        if comentarios:
            for i, com in enumerate(comentarios, 1):
                tk.Label(comentarios_frame, text=f"👤 {com['autor']} ({com['rating']})", font=("Segoe UI", 9, "bold"), bg="#f1f3f4", anchor="w").pack(fill="x")
                tk.Label(comentarios_frame, text=f"💬 {com['texto'][:100]}...", font=("Segoe UI", 9, "italic"), bg="#f1f3f4", anchor="w", fg="#5f6368").pack(fill="x", pady=(0, 5))
        else:
            tk.Label(comentarios_frame, text="No se encontraron comentarios recientes.", bg="#f1f3f4").pack()
        tk.Label(info_frame, text="* Los datos se guardan automáticamente en la carpeta 'fichas_leads'", font=("Segoe UI", 8, "italic"), bg="white", pady=15, fg="#6c757d").pack()

    def create_info_row(self, parent, label, value):
        row = tk.Frame(parent, bg="white")
        row.pack(fill="x", pady=2)
        tk.Label(row, text=label, font=("Segoe UI", 9, "bold"), bg="white", fg="#495057").pack(side="left")
        tk.Label(row, text=value, font=("Segoe UI", 9), bg="white", fg="#212529").pack(side="left", padx=5)

    def start_scraping_thread(self):
        rubro = self.entry_rubro.get()
        if not rubro:
            messagebox.showwarning("Atención", "Ingresa un rubro comercial para comenzar.")
            return
        self.btn_buscar.config(state="disabled")
        self.tree.delete(*self.tree.get_children())
        self.prospectos_datos = {}
        archivo_previo = f"fichas_leads/{rubro}.json"
        if os.path.exists(archivo_previo):
            try:
                with open(archivo_previo, 'r', encoding='utf-8') as f:
                    self.prospectos_datos = json.load(f)
                for nombre in self.prospectos_datos:
                    self.tree.insert("", "end", iid=nombre, values=(nombre, "HISTÓRICO 📁"))
                self.log(f"Se cargaron {len(self.prospectos_datos)} registros previos. Buscando actualizaciones...")
            except Exception:
                self.prospectos_datos = {}
        threading.Thread(target=self.ejecutar_scraping, args=(rubro,), daemon=True).start()

    def abrir_whatsapp(self, nombre, tel):
        if "Sin" in tel or not tel:
            messagebox.showwarning("Error", "Este comercio no dispone de un teléfono válido.")
            return
        numero_limpio = "".join(filter(str.isdigit, tel))
        if not numero_limpio.startswith("54"):
            numero_limpio = "549" + numero_limpio
        mensaje = f"Hola {nombre}, vi tu negocio en Maps. Noté que no tienen sitio web propio y me gustaría enviarte una propuesta para potenciar su presencia digital en Trelew. ¿Te interesaría conversar?"
        url = f"https://wa.me/{numero_limpio}?text={mensaje.replace(' ', '%20')}"
        webbrowser.open(url)

    def ejecutar_scraping(self, rubro):
        self.log(f"Iniciando búsqueda para: {rubro}")
        driver = None
        try:
            driver = create_driver_with_profile()
            wait = WebDriverWait(driver, 15)
            query = f"{rubro} en Trelew"
            driver.get(f"https://www.google.com/maps/search/{query.replace(' ', '+')}")
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="feed"]')))
                time.sleep(random.uniform(4, 7))
            except Exception:
                self.log("No se encontraron resultados o la carga fue muy lenta.")
                driver.quit()
                self.btn_buscar.config(state="normal")
                return

            # Scroll feed para cargar más locales
            try:
                feed = driver.find_element(By.XPATH, '//div[@role="feed"]')
                for _ in range(4):
                    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", feed)
                    time.sleep(random.uniform(4, 7))
            except Exception:
                pass

            self.log("Identificando negocios sin sitio web...")
            locales = driver.find_elements(By.CSS_SELECTOR, "div[role='feed'] > div > div[jsaction]")
            for local in locales[:60]:
                try:
                    try:
                        nombre = local.find_element(By.CSS_SELECTOR, "a[href*='/maps/place/']").get_attribute("aria-label")
                    except:
                        nombre = local.text.split("\n")[0]
                    botones_web = [b for b in local.find_elements(By.TAG_NAME, "a") if "Sitio web" in str(b.get_attribute("aria-label"))]
                    es_lead = False
                    estado_lead = "SIN WEB 🎯"
                    social_url = ""
                    if not botones_web:
                        es_lead = True
                    else:
                        url_destino = botones_web[0].get_attribute("href")
                        if "facebook.com" in url_destino or "instagram.com" in url_destino:
                            es_lead = True
                            estado_lead = "SOLO REDES 📱"
                            social_url = url_destino
                    if es_lead:
                        self.log(f"Oportunidad hallada: {nombre}")
                        driver.execute_script("arguments[0].scrollIntoView();", local)
                        local.click()
                        time.sleep(random.uniform(2, 4))
                        datos_extra = {
                            "telefono": "Sin teléfono",
                            "direccion": "No disponible",
                            "categoria": "General",
                            "rating": "N/A",
                            "horario": "No especificado",
                            "comentarios": [],
                            "facebook": social_url if "facebook.com" in social_url else "No detectado",
                            "instagram": social_url if "instagram.com" in social_url else "No detectado"
                        }
                        try:
                            tel_element = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Teléfono:')]")
                            datos_extra["telefono"] = tel_element.get_attribute("aria-label").replace("Teléfono: ", "")
                        except: pass
                        try:
                            dir_element = driver.find_element(By.CSS_SELECTOR, "button[aria-label*='Dirección:']")
                            datos_extra["direccion"] = dir_element.get_attribute("aria-label").replace("Dirección: ", "")
                        except: pass
                        try:
                            cat_element = driver.find_element(By.CSS_SELECTOR, "button[jsaction*='category']")
                            datos_extra["categoria"] = cat_element.text
                        except: pass
                        try:
                            datos_extra["rating"] = driver.find_element(By.CSS_SELECTOR, "span[role='img'][aria-label*='estrellas']").get_attribute("aria-label")
                        except: pass
                        try:
                            datos_extra["horario"] = driver.find_element(By.CSS_SELECTOR, "button[aria-label*='Horario:']").get_attribute("aria-label").replace("Horario: ", "")
                        except: pass

                        # Extracción de comentarios usando la nueva estrategia robusta
                        try:
                            tab_xpath = "//button[contains(@aria-label, 'Opiniones')] | //button[contains(@aria-label, 'Reseñas')] | //div[contains(text(), 'Opiniones')]"
                            tab_opiniones = driver.find_element(By.XPATH, tab_xpath)
                            tab_opiniones.click()
                            time.sleep(2.5)  # Espera más larga para que se estabilice el panel
                            try:
                                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-review-id]")))
                            except:
                                time.sleep(2)

                            # Llamada a la función mejorada de scroll para reseñas
                            reviews = enhanced_scroll_reviews(driver, item_selector='div[data-review-id]', pause=1.5, max_empty=6)
                            # Tomar hasta 5 reseñas procesables
                            for rev in reviews[:5]:
                                try:
                                    comentario = {}
                                    raw_author = rev.get_attribute("aria-label") or ""
                                    comentario['autor'] = raw_author.replace("Reseña de ", "").split("\n")[0]
                                    try:
                                        comentario['texto'] = rev.find_element(By.CSS_SELECTOR, "span[dir='ltr']").text
                                    except:
                                        try:
                                            comentario['texto'] = rev.find_element(By.CLASS_NAME, "wiI7pd").text
                                        except:
                                            comentario['texto'] = "Sin texto"
                                    try:
                                        comentario['rating'] = rev.find_element(By.CSS_SELECTOR, "span[role='img']").get_attribute("aria-label")
                                    except:
                                        comentario['rating'] = "Sin rating"
                                    if comentario['texto'] and comentario['texto'] != "Sin texto":
                                        datos_extra["comentarios"].append(comentario)
                                except:
                                    continue
                            # Volver a Información
                            try:
                                driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Información')] | //div[contains(text(), 'Información')]").click()
                            except: pass
                        except Exception:
                            pass

                        datos_previos = self.prospectos_datos.get(nombre, {})
                        campos_verificar = ["telefono", "direccion", "categoria", "rating", "horario", "facebook", "instagram"]
                        valores_nulos = ["Sin teléfono", "No disponible", "No especificado", "N/A", "No detectado", "", None]
                        for campo in campos_verificar:
                            nuevo_valor = datos_extra.get(campo)
                            viejo_valor = datos_previos.get(campo)
                            if nuevo_valor in valores_nulos and viejo_valor not in valores_nulos:
                                datos_extra[campo] = viejo_valor
                        if not datos_extra["comentarios"] and datos_previos.get("comentarios"):
                            datos_extra["comentarios"] = datos_previos["comentarios"]

                        self.prospectos_datos[nombre] = datos_extra
                        def actualizar_ui(n):
                            if self.tree.exists(n):
                                self.tree.item(n, values=(n, "ACTUALIZADO ✨" if estado_lead == "SIN WEB 🎯" else estado_lead))
                            else:
                                self.tree.insert("", "end", iid=n, values=(n, estado_lead))
                        self.root.after(0, lambda n=nombre: actualizar_ui(n))
                    time.sleep(random.uniform(2, 4))
                except Exception:
                    continue

            if self.prospectos_datos:
                nombre_archivo = f"fichas_leads/{rubro}.json"
                with open(nombre_archivo, 'w', encoding='utf-8') as f:
                    json.dump(self.prospectos_datos, f, ensure_ascii=False, indent=4)
                self.log(f"Datos guardados en {nombre_archivo}")
                self.root.after(0, self.actualizar_lista_fichas)

            driver.quit()
            self.log("Proceso completado con éxito.")
            self.btn_buscar.config(state="normal")
        except Exception as e:
            self.log(f"Error: {e}")
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            self.btn_buscar.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = TrelewLeadApp(root)
    root.mainloop()
