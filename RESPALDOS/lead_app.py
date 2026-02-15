import tkinter as tk
from tkinter import ttk, messagebox
import threading
import random
import time
import json
import os
import webbrowser
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class TrelewLeadApp:
    """
    Aplicación principal para la prospección de clientes en Trelew.
    Gestiona la interfaz de usuario y la lógica de scraping de Google Maps.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Trelew Digital Leads - Prospector de Negocios")
        self.root.geometry("1100x700")
        self.root.configure(bg="#f8f9fa")

        # Crear carpeta de almacenamiento si no existe
        if not os.path.exists("fichas_leads"):
            os.makedirs("fichas_leads")

        # Configuración de Estilos para una apariencia moderna
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        self.style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=10)
        
        self.prospectos_datos = {} # Memoria temporal de datos recolectados
        self.setup_ui()

    def setup_ui(self):
        # --- Header Principal ---
        header = tk.Frame(self.root, bg="#1a73e8", height=70)
        header.pack(fill="x")
        
        tk.Label(header, text="TRELEW LEAD PROSPECTOR", font=("Segoe UI", 18, "bold"), 
                 bg="#1a73e8", fg="white").pack(pady=15)

        # --- Panel de Control: Búsqueda ---
        search_frame = tk.LabelFrame(self.root, text=" Gestión de Búsquedas ", font=("Segoe UI", 10, "bold"), bg="#f8f9fa", pady=10, padx=10)
        search_frame.pack(fill="x", padx=20)

        # Sección 1: Nueva Búsqueda (Online)
        tk.Label(search_frame, text="Nueva Búsqueda (Google Maps):", font=("Segoe UI", 9), bg="#f8f9fa").pack(side="left")
        
        # Lista desplegable con rubros sugeridos (editable)
        rubros_sugeridos = [
            "Gimnasios", "Restaurantes", "Talleres Mecánicos", "Peluquerías", 
            "Odontólogos", "Abogados", "Inmobiliarias", "Cervecerías", 
            "Veterinarias", "Pizzerías", "Farmacias", "Escuelas de danza", 
            "Estudios Contables", "Ferreterías", "Centros de Estética", 
            "Barberías", "Psicólogos", "Nutricionistas", "Kinesiólogos", 
            "Arquitectos", "Constructoras", "Salones de Eventos", 
            "Servicios de Catering", "Escuelas de Idiomas", "Pet Shops", 
            "Mueblerías", "Casas de Repuestos", "Heladerías", "Cafeterías"
        ]
        self.entry_rubro = ttk.Combobox(search_frame, values=rubros_sugeridos, width=28)
        self.entry_rubro.pack(side="left", padx=5)
        self.entry_rubro.set("Gimnasios")

        self.btn_buscar = ttk.Button(search_frame, text="🔍 BUSCAR Y GUARDAR", command=self.start_scraping_thread)
        self.btn_buscar.pack(side="left", padx=10)

        # Botón para enriquecimiento masivo
        self.btn_enrich_all = ttk.Button(search_frame, text="🌍 ENRIQUECER TODOS", command=self.lanzar_enriquecimiento_masivo)
        self.btn_enrich_all.pack(side="left", padx=5)

        # Separador visual
        ttk.Separator(search_frame, orient="vertical").pack(side="left", fill="y", padx=20)

        # Sección 2: Cargar Ficha (Offline)
        tk.Label(search_frame, text="📂 Cargar Ficha Guardada:", font=("Segoe UI", 9), bg="#f8f9fa").pack(side="left")
        self.combo_fichas = ttk.Combobox(search_frame, width=25, state="readonly")
        self.combo_fichas.pack(side="left", padx=5)
        self.actualizar_lista_fichas() # Cargar lista inicial
        
        self.btn_cargar = ttk.Button(search_frame, text="ABRIR FICHA", command=self.cargar_ficha_offline)
        self.btn_cargar.pack(side="left", padx=5)

        # --- Contenedor Principal (Split View: Maestro-Detalle) ---
        main_container = tk.Frame(self.root, bg="#f8f9fa")
        main_container.pack(fill="both", expand=True, padx=20, pady=10)

        # Panel Izquierdo: Lista de Leads (Treeview)
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
        
        # Vincular evento de selección para actualizar la Card
        self.tree.bind("<<TreeviewSelect>>", self.mostrar_detalle)

        # Panel Derecho: Card de Detalle Visual
        self.right_panel = tk.Frame(main_container, width=350, bg="#f8f9fa", padx=20)
        self.right_panel.pack(side="right", fill="both")
        self.right_panel.pack_propagate(False)

        # Mensaje de ayuda inicial
        self.card_placeholder = tk.Label(self.right_panel, text="Selecciona un comercio\npara ver el detalle", 
                                         font=("Segoe UI", 10, "italic"), fg="#6c757d", bg="#f8f9fa", pady=100)
        self.card_placeholder.pack()

        # Marco de la Card (invisible hasta que se seleccione algo)
        self.detail_card = tk.Frame(self.right_panel, bg="white", highlightbackground="#dee2e6", highlightthickness=1)
        
        # --- Barra de Estado (Feedback al usuario) ---
        self.status_label = tk.Label(self.root, text="Listo para prospectar en Trelew", bd=1, relief="flat", anchor="w", bg="#e9ecef", padx=10)
        self.status_label.pack(side="bottom", fill="x")

    def log(self, mensaje):
        """Actualiza la barra de estado inferior."""
        self.status_label.config(text=f"⚙️ {mensaje}")
        self.root.update_idletasks()

    def actualizar_lista_fichas(self):
        """Lee la carpeta 'fichas_leads' y actualiza el combobox."""
        fichas = [f.replace(".json", "") for f in os.listdir("fichas_leads") if f.endswith(".json")]
        self.combo_fichas['values'] = fichas
        if fichas:
            self.combo_fichas.current(0)

    def cargar_ficha_offline(self):
        """Carga los datos desde un archivo JSON sin abrir el navegador."""
        seleccion = self.combo_fichas.get()
        if not seleccion:
            return
        
        filepath = os.path.join("fichas_leads", f"{seleccion}.json")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                datos_cargados = json.load(f)
            
            # Limpiar UI y memoria
            self.tree.delete(*self.tree.get_children())
            self.prospectos_datos = datos_cargados
            
            # Rellenar Treeview
            for nombre in self.prospectos_datos:
                self.tree.insert("", "end", values=(nombre, "GUARDADO 💾"))
            
            self.log(f"Ficha '{seleccion}' cargada exitosamente. ({len(datos_cargados)} registros)")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la ficha: {e}")

    def mostrar_detalle(self, event):
        """Genera y muestra la Card de detalle del emprendimiento seleccionado."""
        selected = self.tree.selection()
        if not selected:
            return

        # Limpiar contenido anterior de la card
        for widget in self.detail_card.winfo_children():
            widget.destroy()
        
        self.card_placeholder.pack_forget()
        self.detail_card.pack(fill="x", pady=20)

        # Obtener datos del diccionario de memoria
        item_id = selected[0]
        nombre = self.tree.item(item_id)['values'][0]
        datos = self.prospectos_datos.get(nombre, {})

        # Header de la Card
        card_header = tk.Frame(self.detail_card, bg="#1a73e8", pady=10)
        card_header.pack(fill="x")
        tk.Label(card_header, text="DETALLE DEL CLIENTE", font=("Segoe UI", 9, "bold"), bg="#1a73e8", fg="white").pack()

        # Cuerpo de la Card
        body = tk.Frame(self.detail_card, bg="white", padx=15, pady=15)
        body.pack(fill="x")

        tk.Label(body, text=nombre, font=("Segoe UI", 14, "bold"), bg="white", wraplength=280, justify="center").pack(pady=(0, 10))
        
        # Filas de información
        self.create_info_row(body, "📱 Teléfono:", datos.get('telefono', 'No disponible'))
        self.create_info_row(body, "🌐 Web:", "No posee (Oportunidad)")
        self.create_info_row(body, "📍 Ciudad:", "Trelew, Chubut")

        # Separador visual
        tk.Frame(body, height=1, bg="#dee2e6").pack(fill="x", pady=15)

        # --- BOTONES DE CONTACTO MULTICANAL ---
        
        # 1. Verificar disponibilidad de canales
        tel = datos.get('telefono', 'Sin teléfono')
        has_wa = tel and "Sin" not in str(tel) and "No" not in str(tel)
        
        fb = datos.get('facebook', 'No detectado')
        has_fb = fb and "No detectado" not in str(fb)
        
        ig = datos.get('instagram', 'No detectado')
        has_ig = ig and "No detectado" not in str(ig)
        
        email = datos.get('email', 'No detectado')
        has_email = email and "No detectado" not in str(email)

        # 2. Grilla de botones (2x2)
        btn_grid = tk.Frame(body, bg="white")
        btn_grid.pack(fill="x", pady=5)
        btn_grid.columnconfigure(0, weight=1)
        btn_grid.columnconfigure(1, weight=1)

        # WhatsApp (Verde/Rojo)
        c_wa = "#25D366" if has_wa else "#dc3545"
        tk.Button(btn_grid, text="WhatsApp", bg=c_wa, fg="white", font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2" if has_wa else "arrow", command=lambda: self.abrir_whatsapp(nombre, tel) if has_wa else None).grid(row=0, column=0, padx=2, pady=2, sticky="ew")

        # Facebook (Azul/Rojo)
        c_fb = "#3b5998" if has_fb else "#dc3545"
        tk.Button(btn_grid, text="Facebook", bg=c_fb, fg="white", font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2" if has_fb else "arrow", command=lambda: webbrowser.open(fb) if has_fb else None).grid(row=0, column=1, padx=2, pady=2, sticky="ew")

        # Instagram (Violeta/Rojo)
        c_ig = "#833AB4" if has_ig else "#dc3545"
        tk.Button(btn_grid, text="Instagram", bg=c_ig, fg="white", font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2" if has_ig else "arrow", command=lambda: webbrowser.open(ig) if has_ig else None).grid(row=1, column=0, padx=2, pady=2, sticky="ew")

        # Email (Amarillo/Rojo)
        c_em = "#ffc107" if has_email else "#dc3545"
        fg_em = "black" if has_email else "white"
        tk.Button(btn_grid, text="Email", bg=c_em, fg=fg_em, font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2" if has_email else "arrow", command=lambda: webbrowser.open(f"mailto:{email}") if has_email else None).grid(row=1, column=1, padx=2, pady=2, sticky="ew")

        # 3. Botón "Contactar por todos" (Gris/Rojo)
        has_any = has_wa or has_fb or has_ig or has_email
        c_all = "#343a40" if has_any else "#dc3545"
        tk.Button(body, text="CONTACTAR POR TODOS LOS MEDIOS", bg=c_all, fg="white", font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2" if has_any else "arrow", command=self.contactar_todos_placeholder).pack(fill="x", pady=(5, 5))

        # Botón de información detallada (Ficha Técnica)
        btn_info = tk.Button(body, text="📄 VER FICHA TÉCNICA (WEB DEMO)", bg="#17a2b8", fg="white", 
                           font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                           command=lambda: self.mostrar_info_detallada(nombre, datos))
        btn_info.pack(fill="x", pady=5)
        
        # Botón para búsqueda externa manual (Google Search)
        btn_enrich = tk.Button(body, text="🌍 BUSCAR DATOS EXTRA (GOOGLE)", bg="#6f42c1", fg="white", 
                           font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                           command=lambda: self.lanzar_busqueda_externa(nombre))
        btn_enrich.pack(fill="x", pady=5)

    def contactar_todos_placeholder(self):
        pass

    def mostrar_info_detallada(self, nombre, datos):
        """Muestra una ventana flotante con toda la información pública recolectada."""
        top = tk.Toplevel(self.root)
        top.title(f"Ficha Técnica: {nombre}")
        top.geometry("600x700")
        top.attributes('-topmost', True) # Mantiene la ventana siempre visible (Z superior)
        top.configure(bg="white")

        # --- Configuración de Scroll (Canvas + Scrollbar) ---
        container = tk.Frame(top, bg="white")
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg="white")
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        info_frame = tk.Frame(canvas, bg="white", padx=20)

        # Configurar el frame para que se expanda y actualice el scroll
        info_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        window_id = canvas.create_window((0, 0), window=info_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(window_id, width=e.width))

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Habilitar scroll con la rueda del ratón
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        tk.Label(info_frame, text="DATOS PÚBLICOS PARA WEB DEMO", font=("Segoe UI", 14, "bold"), bg="white", fg="#1a73e8", pady=15).pack()

        # Función auxiliar para filas de datos
        def add_row(label, value):
            f = tk.Frame(info_frame, bg="white", pady=8)
            f.pack(fill="x", side="top")
            tk.Label(f, text=label, font=("Segoe UI", 10, "bold"), bg="white", width=15, anchor="w", fg="#495057").pack(side="left")
            
            # Si es un link (Facebook/Instagram), hacerlo clickeable
            if str(value).startswith("http"):
                lbl_link = tk.Label(f, text=value, font=("Segoe UI", 10, "underline"), bg="white", fg="blue", cursor="hand2", wraplength=350, justify="left")
                lbl_link.pack(side="left", fill="x")
                lbl_link.bind("<Button-1>", lambda e: webbrowser.open(value))
            else:
                tk.Label(f, text=value, font=("Segoe UI", 10), bg="white", wraplength=350, justify="left").pack(side="left", fill="x")
            
            tk.Frame(info_frame, height=1, bg="#e9ecef").pack(fill="x") # Separador

        add_row("Nombre:", nombre)
        add_row("Rubro/Categoría:", datos.get("categoria", "No especificado"))
        add_row("Dirección:", datos.get("direccion", "No disponible"))
        add_row("Horarios:", datos.get("horario", "No disponible"))
        add_row("Valoración:", datos.get("rating", "Sin reseñas"))
        add_row("Teléfono:", datos.get("telefono", "Sin teléfono"))
        if datos.get("whatsapp", "No") == "Probable":
            add_row("WhatsApp:", "✅ Probable")
        if datos.get("email") and datos.get("email") != "No detectado":
            add_row("Email:", datos["email"])
        if datos.get("facebook"): add_row("Facebook:", datos["facebook"])
        if datos.get("instagram"): add_row("Instagram:", datos["instagram"])
        
        imgs = datos.get("imagenes", [])
        if imgs: add_row("Imágenes:", f"{len(imgs)} capturadas (URLs)")

        # Sección de Comentarios
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

        # Nota al pie
        tk.Label(info_frame, text="* Los datos se guardan automáticamente en la carpeta 'fichas_leads'", font=("Segoe UI", 8, "italic"), bg="white", pady=15, fg="#6c757d").pack()

    def create_info_row(self, parent, label, value):
        """Crea una fila de información etiquetada dentro de la Card."""
        row = tk.Frame(parent, bg="white")
        row.pack(fill="x", pady=2)
        tk.Label(row, text=label, font=("Segoe UI", 9, "bold"), bg="white", fg="#495057").pack(side="left")
        tk.Label(row, text=value, font=("Segoe UI", 9), bg="white", fg="#212529").pack(side="left", padx=5)

    def start_scraping_thread(self):
        """Inicia el proceso de búsqueda en un hilo separado para evitar bloqueos de UI."""
        rubro = self.entry_rubro.get()
        if not rubro:
            messagebox.showwarning("Atención", "Ingresa un rubro comercial para comenzar.")
            return
        
        self.btn_buscar.config(state="disabled")
        self.tree.delete(*self.tree.get_children())
        
        # --- LÓGICA DE FUSIÓN: Cargar datos previos si existen ---
        self.prospectos_datos = {}
        archivo_previo = f"fichas_leads/{rubro}.json"
        
        if os.path.exists(archivo_previo):
            try:
                with open(archivo_previo, 'r', encoding='utf-8') as f:
                    self.prospectos_datos = json.load(f)
                # Cargar en la lista visualmente (usando el nombre como ID para evitar duplicados)
                for nombre in self.prospectos_datos:
                    self.tree.insert("", "end", iid=nombre, values=(nombre, "HISTÓRICO 📁"))
                self.log(f"Se cargaron {len(self.prospectos_datos)} registros previos. Buscando actualizaciones...")
            except Exception:
                self.prospectos_datos = {}
        
        threading.Thread(target=self.ejecutar_scraping, args=(rubro,), daemon=True).start()

    def abrir_whatsapp(self, nombre, tel):
        """Procesa el contacto y abre el navegador con la API de WhatsApp."""
        if "Sin" in tel or not tel:
            messagebox.showwarning("Error", "Este comercio no dispone de un teléfono válido.")
            return

        # Limpieza de número para formato internacional
        numero_limpio = "".join(filter(str.isdigit, tel))
        if not numero_limpio.startswith("54"):
            numero_limpio = "549" + numero_limpio

        mensaje = f"Hola {nombre}, vi tu negocio en Maps. Noté que no tienen sitio web propio y me gustaría enviarte una propuesta para potenciar su presencia digital en Trelew. ¿Te interesaría conversar?"
        url = f"https://wa.me/{numero_limpio}?text={mensaje.replace(' ', '%20')}"
        webbrowser.open(url)

    def lanzar_enriquecimiento_masivo(self):
        if not self.prospectos_datos:
            messagebox.showwarning("Atención", "Primero debes buscar o cargar una lista de emprendimientos.")
            return
        
        rubro = self.entry_rubro.get()
        confirm = messagebox.askyesno("Confirmar", f"Esto buscará datos extra en Google para {len(self.prospectos_datos)} contactos.\nEl proceso puede tardar unos minutos.\n¿Deseas continuar?")
        if confirm:
            self.log("Iniciando enriquecimiento masivo...")
            threading.Thread(target=self.ejecutar_enriquecimiento_masivo, args=(rubro,), daemon=True).start()

    def ejecutar_enriquecimiento_masivo(self, rubro):
        self.btn_enrich_all.config(state="disabled")
        self.btn_buscar.config(state="disabled")
        
        options = Options()
        options.add_argument("--lang=es-419")
        options.add_argument("--disable-blink-features=AutomationControlled") 
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--start-maximized") 
        profile_dir = os.path.join(os.getcwd(), "selenium_profile")
        options.add_argument(f"--user-data-dir={profile_dir}")
        
        driver = None
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
            })
            
            total = len(self.prospectos_datos)
            count = 0
            
            # Iteramos sobre una copia de los items
            for nombre, datos in list(self.prospectos_datos.items()):
                count += 1
                
                # Solo buscamos si faltan datos importantes
                if datos.get("email") != "No detectado" and datos.get("instagram") != "No detectado":
                    continue

                self.log(f"Enriqueciendo {count}/{total}: {nombre}...")
                nuevos_datos = self.buscar_datos_externos(driver, nombre)
                
                if nuevos_datos:
                    actualizado = False
                    for k, v in nuevos_datos.items():
                        if v and datos.get(k) == 'No detectado':
                            datos[k] = v
                            actualizado = True
                    
                    if actualizado:
                        self.prospectos_datos[nombre] = datos
                        self.root.after(0, lambda n=nombre: self.tree.item(n, values=(n, "ENRIQUECIDO 🌟")) if self.tree.exists(n) else None)
                
                time.sleep(random.uniform(2, 4))

            # Guardado final
            if rubro:
                try:
                    nombre_archivo = f"fichas_leads/{rubro}.json"
                    with open(nombre_archivo, 'w', encoding='utf-8') as f:
                        json.dump(self.prospectos_datos, f, ensure_ascii=False, indent=4)
                except: pass

            self.log("Enriquecimiento masivo completado.")
            self.root.after(0, self.actualizar_lista_fichas)

        except Exception as e:
            self.log(f"Error en proceso masivo: {e}")
        finally:
            if driver:
                driver.quit()
            self.btn_enrich_all.config(state="normal")
            self.btn_buscar.config(state="normal")

    def lanzar_busqueda_externa(self, nombre):
        rubro = self.entry_rubro.get()
        self.log(f"Iniciando búsqueda profunda para {nombre}...")
        threading.Thread(target=self.ejecutar_busqueda_externa_thread, args=(nombre, rubro), daemon=True).start()

    def ejecutar_busqueda_externa_thread(self, nombre, rubro):
        options = Options()
        options.add_argument("--lang=es-419")
        options.add_argument("--disable-blink-features=AutomationControlled") 
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--start-maximized") 
        profile_dir = os.path.join(os.getcwd(), "selenium_profile")
        options.add_argument(f"--user-data-dir={profile_dir}")
        
        driver = None
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
            })
            
            nuevos_datos = self.buscar_datos_externos(driver, nombre)
            
            if nuevos_datos:
                datos = self.prospectos_datos.get(nombre, {})
                actualizado = False
                for k, v in nuevos_datos.items():
                    if v and datos.get(k) == 'No detectado':
                        datos[k] = v
                        actualizado = True
                
                if actualizado:
                    self.prospectos_datos[nombre] = datos
                    if rubro:
                        try:
                            nombre_archivo = f"fichas_leads/{rubro}.json"
                            with open(nombre_archivo, 'w', encoding='utf-8') as f:
                                json.dump(self.prospectos_datos, f, ensure_ascii=False, indent=4)
                        except: pass
                    
                    self.log(f"Datos actualizados para {nombre}")
                    self.root.after(0, lambda: self.mostrar_detalle(None) if self.tree.selection() and self.tree.item(self.tree.selection()[0])['values'][0] == nombre else None)
                else:
                    self.log(f"No se encontraron nuevos datos relevantes para {nombre}")
            else:
                self.log(f"Búsqueda externa sin resultados para {nombre}")

        except Exception as e:
            self.log(f"Error en búsqueda externa: {e}")
        finally:
            if driver:
                driver.quit()

    def buscar_datos_externos(self, driver, nombre):
        """
        Método de respaldo: Busca en Google Search si faltan datos clave.
        Abre una nueva pestaña, busca y extrae emails o redes sociales de los resultados.
        """
        self.log(f"🔍 Buscando datos extra en Google para: {nombre}...")
        nuevos_datos = {}
        try:
            original_window = driver.current_window_handle
            driver.switch_to.new_window('tab')
            
            # Búsqueda OSINT: Nombre + Ciudad + palabras clave
            query = f"{nombre} Trelew contacto email instagram facebook"
            driver.get(f"https://www.google.com/search?q={query.replace(' ', '+')}")
            time.sleep(random.uniform(2.5, 4)) # Espera humana
            
            # 1. Buscar Emails SOLO en los resultados (evitando header/scripts con datos de sesión)
            try:
                # Buscamos dentro del contenedor principal de resultados (id="search" o "rso")
                contenedor = driver.find_element(By.ID, "search")
                texto_analisis = contenedor.get_attribute("innerHTML")
            except:
                texto_analisis = driver.find_element(By.TAG_NAME, "body").text

            # Regex para emails
            emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", texto_analisis)
            # Filtrar basura técnica de Google
            emails_validos = [e for e in emails if not any(x in e for x in ['google.com', 'w3.org', 'rating', 'example', 'sentry', 'png', 'jpg', 'noreply'])]
            if emails_validos:
                nuevos_datos['email'] = emails_validos[0] # Tomamos el primero que suele ser el más relevante

            # 2. Buscar Redes Sociales (Búsqueda Global en la página de resultados)
            # Buscamos cualquier enlace que contenga facebook o instagram, no solo en los títulos
            social_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'facebook.com') or contains(@href, 'instagram.com')]")
            for link in social_links:
                url = link.get_attribute("href")
                if not url: continue
                # Filtrar enlaces de compartir o login que no son el perfil del negocio
                if "sharer" in url or "login" in url or "google.com" in url: continue
                
                if "instagram.com" in url and "instagram" not in nuevos_datos:
                    nuevos_datos['instagram'] = url
                elif "facebook.com" in url and "facebook" not in nuevos_datos:
                    nuevos_datos['facebook'] = url
            
            driver.close()
            driver.switch_to.window(original_window)
        except Exception as e:
            self.log(f"⚠️ Falló búsqueda externa: {e}")
            try:
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
            except: pass
        
        return nuevos_datos

    def ejecutar_scraping(self, rubro):
        """Lógica de scraping con Selenium y detección de sitios web."""
        self.log(f"Iniciando búsqueda para: {rubro}")
        options = Options()
        options.add_argument("--lang=es-419") # Forzar español latino
        
        # --- MEDIDAS ANTI-DETECCIÓN (STEALTH) ---
        # Estas opciones ocultan que el navegador está siendo controlado por software
        options.add_argument("--disable-blink-features=AutomationControlled") 
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # Forzamos WebGL y quitamos banderas de automatización
        # NOTA: Quitamos el User-Agent fijo para evitar conflictos con la versión real de Chrome instalada
        options.add_argument("--start-maximized") 
        # options.add_argument("--enable-webgl")
        # options.add_argument("--ignore-gpu-blocklist")
        options.add_argument("--window-size=1920,1080") # Forzar resolución alta
        
        # --- OPTIMIZACIÓN DE RECURSOS (SEGUNDO PLANO) ---
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        
        # --- PERFIL PERSISTENTE (Evita bloqueos y "Vista Limitada") ---
        # Guarda cookies y caché en una carpeta local para parecer un usuario real recurrente
        profile_dir = os.path.join(os.getcwd(), "selenium_profile")
        options.add_argument(f"--user-data-dir={profile_dir}")
        
        # options.add_argument("--headless") # Activar si se prefiere ocultar la ventana
        
        try:
            try:
                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            except Exception as e:
                # Capturar error si el perfil está bloqueado (Chrome ya abierto)
                if "user data directory is already in use" in str(e) or "Chrome failed to start" in str(e):
                    self.log("❌ Error: El perfil de Chrome está en uso.")
                    self.root.after(0, lambda: messagebox.showerror("Navegador Bloqueado", "No se pudo iniciar el robot.\n\nCierra todas las ventanas de Chrome (o el script de configuración) antes de buscar."))
                    self.btn_buscar.config(state="normal")
                    return
                raise e

            # --- TÉCNICA AVANZADA ANTI-DETECCIÓN (CDP) ---
            # Inyecta el script antes de que cargue cualquier página para ocultar que es un robot de forma persistente
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                """
            })
            
            wait = WebDriverWait(driver, 15)

            query = f"{rubro} en Trelew"
            driver.get(f"https://www.google.com/maps/search/{query.replace(' ', '+')}")
            
            # Esperar a que cargue el contenedor de resultados (feed)
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="feed"]')))
                # Pausa aleatoria tras la búsqueda (5 a 10 segundos)
                wait_search = random.uniform(5, 10)
                self.log(f"Esperando {wait_search:.1f}s para simular comportamiento humano...")
                time.sleep(wait_search)
            except:
                self.log("No se encontraron resultados o la carga fue muy lenta.")
                driver.quit()
                self.btn_buscar.config(state="normal")
                return

            # --- SCROLL AUTOMÁTICO PARA CARGAR MÁS RESULTADOS ---
            self.log("Haciendo scroll para cargar más resultados...")
            try:
                feed = driver.find_element(By.XPATH, '//div[@role="feed"]')
                for _ in range(4): # Realizar scroll 4 veces (carga aprox 40-50 items)
                    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", feed)
                    # Pausa aleatoria en scroll (acumula 20-30s total en 4 iteraciones)
                    time.sleep(random.uniform(5, 8))
            except Exception:
                pass # Si falla el scroll, intentamos con lo que haya cargado

            self.log("Identificando negocios sin sitio web...")

            # Selector robusto: Busca tarjetas dentro del feed de resultados
            # Usamos XPath para asegurar que el elemento contiene un enlace a un lugar (evita separadores)
            locales = driver.find_elements(By.XPATH, "//div[@role='feed']/div/div[.//a[contains(@href, '/maps/place/')]]")
            
            if not locales:
                self.log("⚠️ Selector primario vacío. Intentando selector alternativo...")
                locales = driver.find_elements(By.CSS_SELECTOR, "div[role='feed'] > div > div[jsaction]")

            self.log(f"Analizando {len(locales)} resultados encontrados...")
            
            for local in locales[:50]: # Aumentamos el límite de análisis
                try:
                    # Intentar obtener el nombre desde el enlace principal (más estable que clases aleatorias)
                    try:
                        nombre = local.find_element(By.CSS_SELECTOR, "a[href*='/maps/place/']").get_attribute("aria-label")
                    except:
                        nombre = local.text.split("\n")[0] # Fallback si falla el selector
                    
                    # Verificación lógica de presencia web
                    botones_web = [b for b in local.find_elements(By.TAG_NAME, "a") if "Sitio web" in str(b.get_attribute("aria-label"))]
                    
                    es_lead = False
                    estado_lead = "SIN WEB 🎯"
                    social_url = ""

                    if not botones_web:
                        es_lead = True # No tiene botón web
                    else:
                        # Si tiene botón, verificamos si es una red social (Facebook/Instagram)
                        url_destino = botones_web[0].get_attribute("href")
                        if "facebook.com" in url_destino or "instagram.com" in url_destino:
                            es_lead = True
                            estado_lead = "SOLO REDES 📱"
                            social_url = url_destino

                    if es_lead:
                        self.log(f"Oportunidad hallada: {nombre}")
                        
                        # --- FEEDBACK INMEDIATO: Listar antes de procesar ---
                        # Insertamos el item en la lista visualmente para que sepas que el robot lo encontró
                        self.root.after(0, lambda n=nombre: self.tree.insert("", "end", iid=n, values=(n, "⏳ PROCESANDO...")) if not self.tree.exists(n) else None)
                        # ----------------------------------------------------

                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", local) # Asegurar visibilidad
                        time.sleep(1)
                        try:
                            local.click() # Clic para cargar detalles en panel lateral de Maps
                        except Exception as e:
                            self.log(f"⚠️ Error al hacer clic en {nombre}: {e}")
                            # Si falla el clic, marcamos error en la lista para que no quede "Procesando" eternamente
                            self.root.after(0, lambda n=nombre: self.tree.item(n, values=(n, "❌ ERROR CLIC")) if self.tree.exists(n) else None)
                            continue
                        
                        # --- ESPERA INTELIGENTE PARA DETALLES ---
                        try:
                            # Esperar a que el panel de detalles cargue, buscando un elemento clave como la dirección.
                            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label*='Dirección:']")))
                        except:
                            # Si no encuentra la dirección, esperamos un tiempo fijo como fallback
                            self.log("Panel de detalle lento, esperando más tiempo...")
                            time.sleep(random.uniform(2, 4))
                        
                        # --- 1. SCROLL INICIAL EN DESCRIPCIÓN GENERAL ---
                        # Hacemos una primera pasada para cargar elementos lazy (horarios, "acerca de", etc.)
                        try:
                            self.log(f"Escaneando información general de {nombre}...")
                            driver.execute_script("""
                                var divs = document.querySelectorAll('div[role="main"]');
                                for (var i = 0; i < divs.length; i++) {
                                    if (divs[i].scrollHeight > divs[i].clientHeight) {
                                        divs[i].scrollTop = divs[i].scrollHeight;
                                    }
                                }
                            """)
                            time.sleep(random.uniform(2, 3))
                        except: pass
                        
                        # --- RECOLECCIÓN DE DATOS EXTENDIDA ---
                        datos_extra = {
                            "telefono": "Sin teléfono",
                            "direccion": "No disponible",
                            "categoria": "General",
                            "rating": "N/A",
                            "horario": "No especificado",
                            "comentarios": [],
                            "imagenes": [],
                            "whatsapp": "No",
                            "email": "No detectado",
                            "facebook": social_url if "facebook.com" in social_url else "No detectado",
                            "instagram": social_url if "instagram.com" in social_url else "No detectado"
                        }

                        try:
                            tel_element = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Teléfono:')]")
                            telefono_raw = tel_element.get_attribute("aria-label").replace("Teléfono: ", "")
                            datos_extra["telefono"] = telefono_raw

                            # Heurística para WhatsApp (números de Argentina)
                            numero_limpio = "".join(filter(str.isdigit, telefono_raw.replace("+", "")))
                            if len(numero_limpio) >= 10: # Celulares suelen tener 10 u 11 dígitos sin el +54
                                datos_extra["whatsapp"] = "Probable"
                        except: pass

                        try:
                            dir_element = driver.find_element(By.CSS_SELECTOR, "button[aria-label*='Dirección:']")
                            datos_extra["direccion"] = dir_element.get_attribute("aria-label").replace("Dirección: ", "")
                        except: pass

                        try:
                            # Categoría suele estar en botones con jsaction específico o texto simple
                            cat_element = driver.find_element(By.CSS_SELECTOR, "button[jsaction*='category']")
                            datos_extra["categoria"] = cat_element.text
                        except: pass

                        try:
                            datos_extra["rating"] = driver.find_element(By.CSS_SELECTOR, "span[role='img'][aria-label*='estrellas']").get_attribute("aria-label")
                        except: pass

                        try:
                            datos_extra["horario"] = driver.find_element(By.CSS_SELECTOR, "button[aria-label*='Horario:']").get_attribute("aria-label").replace("Horario: ", "")
                        except: pass

                        # --- EXTRACCIÓN DE COMENTARIOS (NUEVO) ---
                        try:
                            # 1. Intentar cambiar a la pestaña "Opiniones" para ver todas las reseñas
                            # Usamos JS para evitar errores si el elemento está tapado
                            try:
                                driver.execute_script("""
                                    var tabs = document.querySelectorAll('button[role="tab"], button[aria-label*="Opiniones"], button[aria-label*="Reseñas"]');
                                    for (var i = 0; i < tabs.length; i++) {
                                        var txt = tabs[i].textContent || tabs[i].getAttribute('aria-label');
                                        if (txt && (txt.includes('Opiniones') || txt.includes('Reseñas'))) {
                                            tabs[i].click();
                                            break;
                                        }
                                    }
                                """)
                                # Esperar a que carguen las reseñas
                                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-review-id]")))
                                time.sleep(random.uniform(1, 2)) # Pausa extra para renderizado
                            except: 
                                self.log(f"No se encontraron reseñas para {nombre} o la pestaña no cargó.")
                                pass
                            
                            # 2. SCROLL ROBUSTO Y MINIMIZACIÓN TEMPORAL
                            self.log(f"Iniciando análisis de reseñas para {nombre}...")
                            for i in range(3): # Realizar 3 ciclos de scroll/carga
                                # Hacemos scroll para pedir más contenido
                                driver.execute_script("""
                                    var divs = document.querySelectorAll('div');
                                    for (var j = 0; j < divs.length; j++) {
                                        var s = window.getComputedStyle(divs[j]);
                                        if ((s.overflowY === 'auto' || s.overflowY === 'scroll') && divs[j].scrollHeight > divs[j].clientHeight) {
                                            if (divs[j].clientHeight > 100) {
                                                divs[j].scrollTop = divs[j].scrollHeight;
                                                divs[j].dispatchEvent(new WheelEvent('wheel', { deltaY: 1000, bubbles: true }));
                                            }
                                        }
                                    }
                                """)
                                
                                # Espera simple para carga de reseñas sin minimizar
                                self.log(f"Cargando reseñas (ciclo {i+1}/3)...")
                                time.sleep(random.uniform(2, 4))
                                time.sleep(1) # Pequeña pausa para que se redibuje

                            # Buscar tarjetas de review (div con data-review-id es un selector fuerte)
                            reviews = driver.find_elements(By.CSS_SELECTOR, "div[data-review-id]")
                            
                            # Fallback: Si no hay reseñas (falló la pestaña), intentar scrollear el panel principal (Overview)
                            # A veces las reseñas están abajo en la portada y no en la pestaña dedicada.
                            if not reviews:
                                driver.execute_script("""
                                    var mains = document.querySelectorAll('div[role="main"]');
                                    if (mains.length > 0) {
                                        mains[mains.length - 1].scrollTop = mains[mains.length - 1].scrollHeight;
                                    }
                                """)
                                time.sleep(2)
                                reviews = driver.find_elements(By.CSS_SELECTOR, "div[data-review-id]")

                            for rev in reviews[:5]: # Limitado a 5 reseñas
                                try:
                                    comentario = {}
                                    # El autor suele estar en el aria-label del contenedor principal
                                    raw_author = rev.get_attribute("aria-label") or ""
                                    comentario['autor'] = raw_author.replace("Reseña de ", "").split("\n")[0]
                                    
                                    # Texto: Buscamos span con dir='ltr' que es típico del texto de usuario
                                    try:
                                        comentario['texto'] = rev.find_element(By.CSS_SELECTOR, "span[dir='ltr']").text
                                    except:
                                        # Intento secundario por clase si falla el genérico
                                        try:
                                            comentario['texto'] = rev.find_element(By.CLASS_NAME, "wiI7pd").text
                                        except:
                                            comentario['texto'] = "Sin texto"
                                    
                                    # Rating (estrellas)
                                    comentario['rating'] = rev.find_element(By.CSS_SELECTOR, "span[role='img']").get_attribute("aria-label")
                                    
                                    if comentario['texto'] and comentario['texto'] != "Sin texto":
                                        datos_extra["comentarios"].append(comentario)
                                except: continue

                        except: pass 

                        # --- VUELTA A INFORMACIÓN Y DATOS EXTRA (REDES/IMÁGENES) ---
                        try:
                            # 1. Volver a la pestaña "Información" para ver datos de contacto y fotos
                            driver.execute_script("""
                                var tabs = document.querySelectorAll('button[role="tab"], button[aria-label*="Información"], button[aria-label*="Overview"]');
                                for (var i = 0; i < tabs.length; i++) {
                                    var txt = tabs[i].textContent || tabs[i].getAttribute('aria-label');
                                    if (txt && (txt.includes('Información') || txt.includes('Overview'))) {
                                        tabs[i].click();
                                        break;
                                    }
                                }
                            """)
                            time.sleep(2)

                            # 2. SCROLL FINAL EN INFORMACIÓN (Para asegurar carga de redes/email)
                            driver.execute_script("""
                                var divs = document.querySelectorAll('div[role="main"]');
                                for (var i = 0; i < divs.length; i++) {
                                    if (divs[i].scrollHeight > divs[i].clientHeight) {
                                        divs[i].scrollTop = divs[i].scrollHeight;
                                    }
                                }
                            """)
                            time.sleep(2)
                            # 2. SCROLL PROFUNDO EN INFORMACIÓN (MEJORADO)
                            # El usuario solicitó priorizar la captura de datos aunque demore más.
                            self.log(f"Escaneando a fondo perfil de {nombre}...")
                            try:
                                main_div = driver.find_element(By.CSS_SELECTOR, "div[role='main']")
                                # Hacemos varios scrolls progresivos para asegurar que carguen secciones inferiores (Redes, "Del propietario")
                                for _ in range(3):
                                    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", main_div)
                                    time.sleep(1.5)
                            except: pass

                            # 3. Buscar Redes Sociales y Email en el panel de detalle (Búsqueda Profunda)
                            links = driver.find_elements(By.CSS_SELECTOR, "div[role='main'] a[href]")
                            for link in links:
                            # 3. Búsqueda de Redes Sociales y Email (Estrategia Robusta)
                            # Buscamos por selectores CSS específicos y XPath para mayor precisión
                            posibles_redes = driver.find_elements(By.XPATH, "//div[@role='main']//a[contains(@href, 'facebook.com') or contains(@href, 'instagram.com') or contains(@href, 'mailto:')]")
                            
                            for link in posibles_redes:
                                url = link.get_attribute("href")
                                if not url: continue
                                
                                if "facebook.com" in url and datos_extra["facebook"] == "No detectado":
                                    datos_extra["facebook"] = url
                                elif "instagram.com" in url and datos_extra["instagram"] == "No detectado":
                                    datos_extra["instagram"] = url
                                elif "mailto:" in url:
                                    datos_extra["email"] = url.replace("mailto:", "")

                            # 4. Recolectar Imágenes (URLs) para futura web
                            # 4. Respaldo de Teléfono (Búsqueda en texto si falló el botón)
                            if datos_extra["telefono"] == "Sin teléfono":
                                try:
                                    texto_panel = driver.find_element(By.CSS_SELECTOR, "div[role='main']").text
                                    # Regex para encontrar números telefónicos en el texto descriptivo
                                    phones = re.findall(r'(?:(?:\+|00)?54\s?9?)?(?:\d{2,4})[\s.-]?\d{6,8}', texto_panel)
                                    if phones:
                                        # Filtramos números válidos (longitud mínima)
                                        valid_phones = [p for p in phones if len(re.sub(r'\D', '', p)) >= 8]
                                        if valid_phones:
                                            datos_extra["telefono"] = valid_phones[0]
                                            # Recalcular WhatsApp
                                            num_clean = "".join(filter(str.isdigit, valid_phones[0]))
                                            if len(num_clean) >= 10:
                                                datos_extra["whatsapp"] = "Probable"
                                            self.log(f"Teléfono recuperado del texto: {datos_extra['telefono']}")
                                except: pass

                            # 5. Recolectar Imágenes (URLs) para futura web
                            imgs = driver.find_elements(By.CSS_SELECTOR, "div[role='main'] img")
                            for img in imgs:
                                src = img.get_attribute("src")
                                if src and "http" in src and "googleusercontent" in src and len(datos_extra["imagenes"]) < 3:
                                    datos_extra["imagenes"].append(src)
                        except Exception: pass

                        # --- LÓGICA DE FUSIÓN INTELIGENTE (MERGE) ---
                        # Recuperamos datos previos si existen para no perder información valiosa
                        datos_previos = self.prospectos_datos.get(nombre, {})
                        
                        # Lista de campos a verificar para no sobrescribir con vacíos
                        campos_verificar = ["telefono", "direccion", "categoria", "rating", "horario", "facebook", "instagram", "imagenes", "whatsapp", "email"]
                        valores_nulos = ["Sin teléfono", "No disponible", "No especificado", "N/A", "No detectado", "", None]

                        for campo in campos_verificar:
                            nuevo_valor = datos_extra.get(campo)
                            viejo_valor = datos_previos.get(campo)
                            
                            # Si el nuevo valor es "nulo" y el viejo servía, nos quedamos con el viejo
                            if nuevo_valor in valores_nulos and viejo_valor not in valores_nulos:
                                datos_extra[campo] = viejo_valor

                        # Fusión de imágenes: si no encontramos nuevas, mantenemos las viejas
                        if not datos_extra["imagenes"] and datos_previos.get("imagenes"):
                            datos_extra["imagenes"] = datos_previos["imagenes"]

                        # Fusión de comentarios: Si no encontramos nuevos, mantenemos los viejos
                        if not datos_extra["comentarios"] and datos_previos.get("comentarios"):
                            datos_extra["comentarios"] = datos_previos["comentarios"]
                        
                        # Guardar (ahora sí, datos combinados)
                        self.prospectos_datos[nombre] = datos_extra
                        
                        # --- GUARDADO INCREMENTAL (PERSISTENCIA) ---
                        # Guardamos en cada iteración para evitar pérdida de datos si se cierra el navegador
                        try:
                            nombre_archivo = f"fichas_leads/{rubro}.json"
                            with open(nombre_archivo, 'w', encoding='utf-8') as f:
                                json.dump(self.prospectos_datos, f, ensure_ascii=False, indent=4)
                        except Exception: pass
                        
                        # Actualizar UI de forma inteligente (sin duplicar filas)
                        def actualizar_ui(n):
                            if self.tree.exists(n):
                                self.tree.item(n, values=(n, "ACTUALIZADO ✨" if estado_lead == "SIN WEB 🎯" else estado_lead))
                            else:
                                self.tree.insert("", "end", iid=n, values=(n, estado_lead))
                        
                        self.root.after(0, lambda n=nombre: actualizar_ui(n))
                    
                    # Pausa entre cada ítem analizado
                    time.sleep(random.uniform(2, 4)) # Aumentado para mayor precisión
                    
                except Exception:
                    continue
            
            # --- GUARDADO AUTOMÁTICO AL FINALIZAR ---
            if self.prospectos_datos:
                nombre_archivo = f"fichas_leads/{rubro}.json"
                with open(nombre_archivo, 'w', encoding='utf-8') as f:
                    json.dump(self.prospectos_datos, f, ensure_ascii=False, indent=4)
                self.log(f"Datos guardados en {nombre_archivo}")
                self.root.after(0, self.actualizar_lista_fichas) # Actualizar lista desplegable
            else:
                self.log("⚠️ Finalizado sin nuevos datos guardados.")

            driver.quit()
            self.log("Proceso completado con éxito.")
            self.btn_buscar.config(state="normal")
            
        except Exception as e:
            self.log(f"Error: {e}")
            self.btn_buscar.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = TrelewLeadApp(root)
    root.mainloop()