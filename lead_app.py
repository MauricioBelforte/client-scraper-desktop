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
import src.constants as constantes
from src.gestor_datos import GestorDatos
from src.utilidades import abrir_whatsapp
from src.scroll_strategies import estrategia_scroll_js_focalizado, estrategia_scroll_teclado

class TrelewLeadApp:
    """
    Aplicación principal para la prospección de clientes en Trelew.
    Gestiona la interfaz de usuario y la lógica de scraping de Google Maps.
    """
    def __init__(self, root):
        self.root = root
        self.root.title(constantes.TITULO_APP)
        self.root.geometry("1100x700")
        self.root.configure(bg=constantes.COLOR_FONDO)

        # Inicializar Gestor de Datos
        self.gestor_datos = GestorDatos(constantes.CARPETA_DATOS)

        # Configuración de Estilos para una apariencia moderna
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Treeview", rowheight=30, font=constantes.FUENTE_NORMAL)
        self.style.configure("Treeview.Heading", font=constantes.FUENTE_NEGRITA)
        self.style.configure("Action.TButton", font=constantes.FUENTE_NEGRITA, padding=10)
        
        self.prospectos_datos = {} # Memoria temporal de datos recolectados
        self.setup_ui()

    def setup_ui(self):
        # --- Header Principal ---
        header = tk.Frame(self.root, bg=constantes.COLOR_PRIMARIO, height=70)
        header.pack(fill="x")
        
        tk.Label(header, text=constantes.TEXTO_ENCABEZADO, font=constantes.FUENTE_TITULO, 
                 bg=constantes.COLOR_PRIMARIO, fg=constantes.COLOR_BLANCO).pack(pady=15)

        # --- Panel de Control: Búsqueda ---
        search_frame = tk.LabelFrame(self.root, text=constantes.TITULO_FRAME_BUSQUEDA, font=constantes.FUENTE_NEGRITA, bg=constantes.COLOR_FONDO, pady=10, padx=10)
        search_frame.pack(fill="x", padx=20)

        # Sección 1: Nueva Búsqueda (Online)
        tk.Label(search_frame, text=constantes.ETIQUETA_NUEVA_BUSQUEDA, font=constantes.FUENTE_PEQUENA, bg=constantes.COLOR_FONDO).pack(side="left")
        
        self.entry_rubro = ttk.Combobox(search_frame, values=constantes.RUBROS_SUGERIDOS, width=28)
        self.entry_rubro.pack(side="left", padx=5)
        self.entry_rubro.set("Gimnasios")

        self.btn_buscar = ttk.Button(search_frame, text=constantes.BTN_BUSCAR, command=self.start_scraping_thread)
        self.btn_buscar.pack(side="left", padx=10)

        # Botón para enriquecimiento masivo
        self.btn_enrich_all = ttk.Button(search_frame, text=constantes.BTN_ENRIQUECER, command=self.lanzar_enriquecimiento_masivo)
        self.btn_enrich_all.pack(side="left", padx=5)

        # Separador visual
        ttk.Separator(search_frame, orient="vertical").pack(side="left", fill="y", padx=20)

        # Sección 2: Cargar Ficha (Offline)
        tk.Label(search_frame, text=constantes.ETIQUETA_CARGAR_ARCHIVO, font=constantes.FUENTE_PEQUENA, bg=constantes.COLOR_FONDO).pack(side="left")
        self.combo_fichas = ttk.Combobox(search_frame, width=25, state="readonly")
        self.combo_fichas.pack(side="left", padx=5)
        self.actualizar_lista_fichas() # Cargar lista inicial
        
        self.btn_cargar = ttk.Button(search_frame, text=constantes.BTN_CARGAR, command=self.cargar_ficha_offline)
        self.btn_cargar.pack(side="left", padx=5)

        # --- Contenedor Principal (Split View: Maestro-Detalle) ---
        main_container = tk.Frame(self.root, bg=constantes.COLOR_FONDO)
        main_container.pack(fill="both", expand=True, padx=20, pady=10)

        # Panel Izquierdo: Lista de Leads (Treeview)
        left_panel = tk.Frame(main_container, bg=constantes.COLOR_BLANCO, relief="flat")
        left_panel.pack(side="left", fill="both", expand=True)

        tk.Label(left_panel, text=constantes.ETIQUETA_RESULTADOS, font=constantes.FUENTE_NEGRITA, bg=constantes.COLOR_BLANCO, pady=5).pack()

        columns = ("nombre", "estado")
        self.tree = ttk.Treeview(left_panel, columns=columns, show="headings")
        self.tree.heading("nombre", text=constantes.COLUMNA_NOMBRE)
        self.tree.heading("estado", text=constantes.COLUMNA_ESTADO)
        self.tree.column("nombre", width=250)
        self.tree.column("estado", width=100)
        
        scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Vincular evento de selección para actualizar la Card
        self.tree.bind("<<TreeviewSelect>>", self.mostrar_detalle)

        # Panel Derecho: Card de Detalle Visual
        self.right_panel = tk.Frame(main_container, width=350, bg=constantes.COLOR_FONDO, padx=20)
        self.right_panel.pack(side="right", fill="both")
        self.right_panel.pack_propagate(False)

        # Mensaje de ayuda inicial
        self.card_placeholder = tk.Label(self.right_panel, text=constantes.TEXTO_PLACEHOLDER_CARD, 
                                         font=constantes.FUENTE_ITALICA, fg=constantes.COLOR_TEXTO_TENUE, bg=constantes.COLOR_FONDO, pady=100)
        self.card_placeholder.pack()

        # Marco de la Card (invisible hasta que se seleccione algo)
        self.detail_card = tk.Frame(self.right_panel, bg=constantes.COLOR_BLANCO, highlightbackground=constantes.COLOR_BORDE, highlightthickness=1)
        
        # --- Barra de Estado (Feedback al usuario) ---
        self.status_label = tk.Label(self.root, text=constantes.ESTADO_LISTO, bd=1, relief="flat", anchor="w", bg=constantes.COLOR_FONDO_ESTADO, padx=10)
        self.status_label.pack(side="bottom", fill="x")

    def log(self, mensaje):
        """Actualiza la barra de estado inferior."""
        self.status_label.config(text=f"⚙️ {mensaje}")
        self.root.update_idletasks()

    def solicitar_confirmacion_usuario(self, mensaje):
        """Muestra un cartel y detiene el hilo hasta que el usuario acepte."""
        event = threading.Event()
        def show():
            messagebox.showinfo("Pausa Manual", mensaje)
            event.set()
        self.root.after(0, show)
        event.wait()

    def actualizar_lista_fichas(self):
        """Lee la carpeta 'fichas_leads' y actualiza el combobox."""
        fichas = self.gestor_datos.obtener_archivos()
        self.combo_fichas['values'] = fichas
        if fichas:
            self.combo_fichas.current(0)

    def cargar_ficha_offline(self):
        """Carga los datos desde un archivo JSON sin abrir el navegador."""
        seleccion = self.combo_fichas.get()
        if not seleccion:
            return
        
        try:
            datos_cargados = self.gestor_datos.cargar_datos(seleccion)
            
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
        card_header = tk.Frame(self.detail_card, bg=constantes.COLOR_PRIMARIO, pady=10)
        card_header.pack(fill="x")
        tk.Label(card_header, text=constantes.ENCABEZADO_CARD, font=constantes.FUENTE_PEQUENA_NEGRITA, bg=constantes.COLOR_PRIMARIO, fg=constantes.COLOR_BLANCO).pack()

        # Cuerpo de la Card
        body = tk.Frame(self.detail_card, bg=constantes.COLOR_BLANCO, padx=15, pady=15)
        body.pack(fill="x")

        tk.Label(body, text=nombre, font=constantes.FUENTE_SUBTITULO, bg=constantes.COLOR_BLANCO, wraplength=280, justify="center").pack(pady=(0, 10))
        
        # Filas de información
        self.create_info_row(body, constantes.ETIQUETA_TELEFONO, datos.get('telefono', 'No disponible'))
        self.create_info_row(body, constantes.ETIQUETA_WEB, constantes.VALOR_SIN_WEB)
        self.create_info_row(body, constantes.ETIQUETA_CIUDAD, constantes.VALOR_CIUDAD)

        # Separador visual
        tk.Frame(body, height=1, bg=constantes.COLOR_BORDE).pack(fill="x", pady=15)

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
        btn_grid = tk.Frame(body, bg=constantes.COLOR_BLANCO)
        btn_grid.pack(fill="x", pady=5)
        btn_grid.columnconfigure(0, weight=1)
        btn_grid.columnconfigure(1, weight=1)

        # WhatsApp (Verde/Rojo)
        c_wa = constantes.COLOR_WHATSAPP if has_wa else constantes.COLOR_PELIGRO
        tk.Button(btn_grid, text="WhatsApp", bg=c_wa, fg=constantes.COLOR_BLANCO, font=constantes.FUENTE_PEQUENA_NEGRITA, relief="flat", cursor="hand2" if has_wa else "arrow", command=lambda: abrir_whatsapp(nombre, tel) if has_wa else None).grid(row=0, column=0, padx=2, pady=2, sticky="ew")

        # Facebook (Azul/Rojo)
        c_fb = constantes.COLOR_FACEBOOK if has_fb else constantes.COLOR_PELIGRO
        tk.Button(btn_grid, text="Facebook", bg=c_fb, fg=constantes.COLOR_BLANCO, font=constantes.FUENTE_PEQUENA_NEGRITA, relief="flat", cursor="hand2" if has_fb else "arrow", command=lambda: webbrowser.open(fb) if has_fb else None).grid(row=0, column=1, padx=2, pady=2, sticky="ew")

        # Instagram (Violeta/Rojo)
        c_ig = constantes.COLOR_INSTAGRAM if has_ig else constantes.COLOR_PELIGRO
        tk.Button(btn_grid, text="Instagram", bg=c_ig, fg=constantes.COLOR_BLANCO, font=constantes.FUENTE_PEQUENA_NEGRITA, relief="flat", cursor="hand2" if has_ig else "arrow", command=lambda: webbrowser.open(ig) if has_ig else None).grid(row=1, column=0, padx=2, pady=2, sticky="ew")

        # Email (Amarillo/Rojo)
        c_em = constantes.COLOR_EMAIL if has_email else constantes.COLOR_PELIGRO
        fg_em = "black" if has_email else constantes.COLOR_BLANCO
        tk.Button(btn_grid, text="Email", bg=c_em, fg=fg_em, font=constantes.FUENTE_PEQUENA_NEGRITA, relief="flat", cursor="hand2" if has_email else "arrow", command=lambda: webbrowser.open(f"mailto:{email}") if has_email else None).grid(row=1, column=1, padx=2, pady=2, sticky="ew")

        # 3. Botón "Contactar por todos" (Gris/Rojo)
        has_any = has_wa or has_fb or has_ig or has_email
        c_all = constantes.COLOR_BTN_OSCURO if has_any else constantes.COLOR_PELIGRO
        tk.Button(body, text=constantes.BTN_CONTACTAR_TODOS, bg=c_all, fg=constantes.COLOR_BLANCO, font=constantes.FUENTE_PEQUENA_NEGRITA, relief="flat", cursor="hand2" if has_any else "arrow", command=self.contactar_todos_placeholder).pack(fill="x", pady=(5, 5))

        # Botón de información detallada (Ficha Técnica)
        btn_info = tk.Button(body, text=constantes.BTN_VER_FICHA, bg=constantes.COLOR_BTN_INFO, fg=constantes.COLOR_BLANCO, 
                           font=constantes.FUENTE_NEGRITA, relief="flat", cursor="hand2",
                           command=lambda: self.mostrar_info_detallada(nombre, datos))
        btn_info.pack(fill="x", pady=5)
        
        btn_enrich = tk.Button(body, text=constantes.BTN_BUSCAR_GOOGLE, bg=constantes.COLOR_BTN_BUSCAR, fg=constantes.COLOR_BLANCO, 
                           font=constantes.FUENTE_PEQUENA_NEGRITA, relief="flat", cursor="hand2",
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
        top.configure(bg=constantes.COLOR_BLANCO)

        # --- Configuración de Scroll (Canvas + Scrollbar) ---
        container = tk.Frame(top, bg=constantes.COLOR_BLANCO)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg=constantes.COLOR_BLANCO)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        info_frame = tk.Frame(canvas, bg=constantes.COLOR_BLANCO, padx=20)

        # Configurar el frame para que se expanda y actualice el scroll
        info_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        window_id = canvas.create_window((0, 0), window=info_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(window_id, width=e.width))

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Habilitar scroll con la rueda del ratón
        def _on_mousewheel(event):
            try:
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                pass
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Limpiar evento al cerrar la ventana para evitar errores
        def on_close():
            canvas.unbind_all("<MouseWheel>")
            top.destroy()
        top.protocol("WM_DELETE_WINDOW", on_close)

        tk.Label(info_frame, text=constantes.ENCABEZADO_FICHA, font=constantes.FUENTE_SUBTITULO, bg=constantes.COLOR_BLANCO, fg=constantes.COLOR_PRIMARIO, pady=15).pack()

        # Función auxiliar para filas de datos
        def add_row(label, value):
            f = tk.Frame(info_frame, bg=constantes.COLOR_BLANCO, pady=8)
            f.pack(fill="x", side="top")
            tk.Label(f, text=label, font=constantes.FUENTE_NEGRITA, bg=constantes.COLOR_BLANCO, width=15, anchor="w", fg=constantes.COLOR_TEXTO_ETIQUETA).pack(side="left")
            
            # Si es un link (Facebook/Instagram), hacerlo clickeable
            if str(value).startswith("http"):
                lbl_link = tk.Label(f, text=value, font=constantes.FUENTE_LINK, bg=constantes.COLOR_BLANCO, fg=constantes.COLOR_ENLACE, cursor="hand2", wraplength=350, justify="left")
                lbl_link.pack(side="left", fill="x")
                lbl_link.bind("<Button-1>", lambda e: webbrowser.open(value))
            else:
                tk.Label(f, text=value, font=constantes.FUENTE_NORMAL, bg=constantes.COLOR_BLANCO, wraplength=350, justify="left").pack(side="left", fill="x")
            
            tk.Frame(info_frame, height=1, bg=constantes.COLOR_FONDO_ESTADO).pack(fill="x") # Separador

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
        tk.Label(info_frame, text=constantes.SECCION_COMENTARIOS, font=constantes.FUENTE_NEGRITA, bg=constantes.COLOR_BLANCO, pady=10).pack(anchor="w")
        comentarios_frame = tk.Frame(info_frame, bg=constantes.COLOR_FONDO_COMENTARIO, padx=10, pady=10)
        comentarios_frame.pack(fill="x")
        
        comentarios = datos.get("comentarios", [])
        if comentarios:
            for i, com in enumerate(comentarios, 1):
                tk.Label(comentarios_frame, text=f"👤 {com['autor']} ({com['rating']})", font=constantes.FUENTE_PEQUENA_NEGRITA, bg=constantes.COLOR_FONDO_COMENTARIO, anchor="w").pack(fill="x")
                tk.Label(comentarios_frame, text=f"💬 {com['texto'][:100]}...", font=constantes.FUENTE_PEQUENA, bg=constantes.COLOR_FONDO_COMENTARIO, anchor="w", fg=constantes.COLOR_TEXTO_COMENTARIO).pack(fill="x", pady=(0, 5))
        else:
            tk.Label(comentarios_frame, text=constantes.MSJ_SIN_COMENTARIOS, bg=constantes.COLOR_FONDO_COMENTARIO).pack()

        # Nota al pie
        tk.Label(info_frame, text=constantes.NOTA_PIE, font=constantes.FUENTE_DIMINUTA, bg=constantes.COLOR_BLANCO, pady=15, fg=constantes.COLOR_TEXTO_TENUE).pack()

    def create_info_row(self, parent, label, value):
        """Crea una fila de información etiquetada dentro de la Card."""
        row = tk.Frame(parent, bg=constantes.COLOR_BLANCO)
        row.pack(fill="x", pady=2)
        tk.Label(row, text=label, font=constantes.FUENTE_PEQUENA_NEGRITA, bg=constantes.COLOR_BLANCO, fg=constantes.COLOR_TEXTO_ETIQUETA).pack(side="left")
        tk.Label(row, text=value, font=constantes.FUENTE_PEQUENA, bg=constantes.COLOR_BLANCO, fg=constantes.COLOR_TEXTO_OSCURO).pack(side="left", padx=5)

    def start_scraping_thread(self):
        """Inicia el proceso de búsqueda en un hilo separado para evitar bloqueos de UI."""
        rubro = self.entry_rubro.get()
        if not rubro:
            messagebox.showwarning("Atención", constantes.MSJ_ADVERTENCIA_RUBRO)
            return
        
        self.btn_buscar.config(state="disabled")
        self.tree.delete(*self.tree.get_children())
        
        # --- LÓGICA DE FUSIÓN: Cargar datos previos si existen ---
        self.prospectos_datos = {}
        archivo_previo = os.path.join(constantes.CARPETA_DATOS, f"{rubro}.json")
        
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

    def lanzar_enriquecimiento_masivo(self):
        if not self.prospectos_datos:
            messagebox.showwarning("Atención", constantes.MSJ_ADVERTENCIA_SIN_LISTA)
            return
        
        rubro = self.entry_rubro.get()
        confirm = messagebox.askyesno("Confirmar", constantes.MSJ_CONFIRMAR_ENRIQUECIMIENTO.format(len(self.prospectos_datos)))
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
        profile_dir = os.path.join(os.getcwd(), constantes.CARPETA_PERFIL)
        options.add_argument(f"--user-data-dir={profile_dir}")
        
        driver = None
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
            })
            
            total = len(self.prospectos_datos)
            count = 0
            
            # Iteramos sobre una copia de los items para poder modificar el diccionario original sin errores
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
                    nombre_archivo = os.path.join(constantes.CARPETA_DATOS, f"{rubro}.json")
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
        profile_dir = os.path.join(os.getcwd(), constantes.CARPETA_PERFIL)
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
                            nombre_archivo = os.path.join(constantes.CARPETA_DATOS, f"{rubro}.json")
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
            
            # Búsqueda OSINT: Combinamos nombre, ciudad y palabras clave para maximizar la probabilidad de encontrar datos de contacto.
            query = f"{nombre} Trelew contacto email instagram facebook"
            driver.get(f"https://www.google.com/search?q={query.replace(' ', '+')}")
            time.sleep(random.uniform(2.5, 4)) # Espera humana
            
            # 1. Buscar Emails SOLO en los resultados (evitando header/scripts con datos de sesión)
            try:
                # Buscamos dentro del contenedor principal de resultados (id="search" o "rso") para evitar capturar emails de la UI de Google.
                contenedor = driver.find_element(By.ID, "search")
                texto_analisis = contenedor.get_attribute("innerHTML")
            except:
                texto_analisis = driver.find_element(By.TAG_NAME, "body").text

            # Regex para emails
            emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", texto_analisis)
            # Filtrar basura técnica: Excluimos dominios comunes de Google o ejemplos para obtener emails reales.
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
        # Estas opciones intentan ocultar que el navegador está siendo controlado por software de automatización.
        options.add_argument("--disable-blink-features=AutomationControlled") 
        options.add_experimental_option("excludeSwitches", ["enable-automation"]) # Oculta la barra "Chrome está siendo controlado..."
        options.add_experimental_option("useAutomationExtension", False) # Desactiva extensiones de automatización
        
        # Forzamos WebGL y quitamos banderas de automatización
        # NOTA: Quitamos el User-Agent fijo para evitar conflictos con la versión real de Chrome instalada
        options.add_argument("--start-maximized") 
        # options.add_argument("--enable-webgl")
        # options.add_argument("--ignore-gpu-blocklist")
        options.add_argument("--window-size=1920,1080") # Forzar resolución alta para que carguen más elementos
        
        # --- OPTIMIZACIÓN DE RECURSOS (SEGUNDO PLANO) ---
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        
        # --- PERFIL PERSISTENTE (La medida anti-bloqueo más importante) ---
        # Guarda cookies, caché y sesiones en una carpeta local. Esto hace que el bot parezca un usuario real que vuelve a visitar el sitio.
        profile_dir = os.path.join(os.getcwd(), constantes.CARPETA_PERFIL)
        options.add_argument(f"--user-data-dir={profile_dir}")
        
        # options.add_argument("--headless") # Activar si se prefiere ocultar la ventana
        
        try:
            try:
                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            except Exception as e:
                # Capturar error si el perfil está bloqueado (Chrome ya abierto)
                if "user data directory is already in use" in str(e) or "Chrome failed to start" in str(e):
                    self.log("❌ Error: El perfil de Chrome está en uso.")
                    self.root.after(0, lambda: messagebox.showerror("Navegador Bloqueado", constantes.MSJ_NAVEGADOR_BLOQUEADO))
                    self.btn_buscar.config(state="normal")
                    return
                raise e

            # --- TÉCNICA AVANZADA ANTI-DETECCIÓN (CDP) ---
            # Inyecta un script de JavaScript en cada página ANTES de que se cargue.
            # Este script elimina la propiedad `navigator.webdriver`, que los sitios web usan para detectar bots.
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
            # En la lista inicial de resultados, hacemos scroll hacia abajo varias veces
            # para forzar a Google Maps a cargar más negocios en el DOM antes de empezar a analizarlos.
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

            # Selector robusto: Busca las "tarjetas" de cada negocio dentro del feed de resultados.
            # Usamos un XPath que busca cualquier div que contenga un enlace a un lugar de Google Maps,
            # lo que lo hace más resistente a cambios de clases CSS.
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
                            # 1. Navegación a la pestaña "Opiniones"
                            # Usamos un script de JS para hacer clic, ya que es más fiable que el .click() de Selenium
                            # si el elemento está parcialmente oculto o hay otros elementos superpuestos.
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
                            
                            # 2. SCROLL ROBUSTO EN RESEÑAS
                            # Realizamos varios ciclos de scroll para cargar la mayor cantidad de reseñas posible.
                            # El script busca cualquier div con barra de scroll y lo baja hasta el final.
                            self.log(f"Analizando reseñas de {nombre}...")
                            
                            # --- PASO 1: IDENTIFICAR EL PANEL CORRECTO ---
                            # Buscamos el panel visible que tenga el título del negocio
                            panel_resenas = None
                            try:
                                candidates = driver.find_elements(By.CSS_SELECTOR, "div[role='main']")
                                for c in candidates:
                                    if c.is_displayed():
                                        try:
                                            h1_text = c.find_element(By.TAG_NAME, "h1").text
                                            if nombre.lower() in h1_text.lower() or h1_text.lower() in nombre.lower():
                                                panel_resenas = c
                                                break
                                        except: pass
                                # Fallback: Si no coincide nombre, usamos el último visible
                                if not panel_resenas:
                                    visibles = [x for x in candidates if x.is_displayed()]
                                    if visibles: panel_resenas = visibles[-1]
                            except: pass

                            # --- PASO 2: EJECUTAR ESTRATEGIAS MODULARES ---
                            if panel_resenas:
                                # Podemos llamar a una, a la otra, o a ambas en secuencia
                                # estrategia_scroll_js_focalizado(driver, panel_resenas, self.log)
                                 estrategia_scroll_teclado(driver, panel_resenas, self.log)

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

                        # --- PUNTO DE PAUSA SOLICITADO ---
                        # Frenamos aquí para verificar visualmente antes de volver a la info general
                        self.solicitar_confirmacion_usuario(f"Terminé de leer reseñas de: {nombre}.\n\nVoy a intentar volver a la descripción general.\nVerifica el navegador.")

                        # --- VUELTA A INFORMACIÓN Y DATOS EXTRA (REDES/IMÁGENES) ---
                        try:
                            # 1. Volver a la pestaña "Información" para buscar datos que no estaban en la vista principal.
                            # Este patrón (Info -> Reseñas -> Info) asegura que todos los datos dinámicos se carguen.
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

                            # 2. SCROLL PROFUNDO EN INFORMACIÓN (MEJORADO)
                            # El usuario solicitó priorizar la captura de datos aunque demore más.
                            self.log(f"Escaneando a fondo perfil de {nombre}...")
                            main_div = None
                            try:
                                # Buscamos todos los paneles y usamos el que es visible para evitar interactuar con paneles ocultos/viejos
                                candidates = driver.find_elements(By.CSS_SELECTOR, "div[role='main']")
                                
                                # Buscamos el panel que corresponde al negocio actual por nombre
                                for c in candidates:
                                    if c.is_displayed():
                                        try:
                                            h1_text = c.find_element(By.TAG_NAME, "h1").text
                                            # Comparación laxa para evitar problemas con mayúsculas/espacios
                                            if nombre.lower() in h1_text.lower() or h1_text.lower() in nombre.lower():
                                                main_div = c
                                                break
                                        except: pass
                                
                                # Fallback: Si no coincide nombre, usamos el último visible
                                if not main_div:
                                    visibles = [x for x in candidates if x.is_displayed()]
                                    if visibles:
                                        main_div = visibles[-1]

                                if main_div:
                                    # Hacemos varios scrolls progresivos para asegurar que carguen secciones inferiores (Redes, "Del propietario")
                                    for _ in range(3):
                                        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", main_div)
                                        time.sleep(1.5)
                            except: pass

                            # 3. Búsqueda de Redes Sociales y Email (Estrategia de Respaldo)
                            # Buscamos enlaces que apunten a dominios específicos (facebook, instagram) o que contengan "mailto:".
                            # El XPath se limita al panel principal (`div[role='main']`) para no capturar enlaces del resto de la página.
                            posibles_redes = []
                            if main_div:
                                posibles_redes = main_div.find_elements(By.XPATH, ".//a[contains(@href, 'facebook.com') or contains(@href, 'instagram.com') or contains(@href, 'mailto:')]")
                            else:
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
                        # Si ya teníamos datos de este negocio de una búsqueda anterior, no sobrescribimos
                        # información valiosa (ej. un email encontrado manualmente) con un resultado vacío ("No detectado").
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
                            nombre_archivo = os.path.join(constantes.CARPETA_DATOS, f"{rubro}.json")
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
                    
                    # Limpieza preventiva: Cerrar posibles modales (Share, Fotos) con ESC
                    try:
                        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                    except: pass

                    # Pausa entre cada ítem analizado
                    time.sleep(random.uniform(2, 4)) # Aumentado para mayor precisión
                    
                except Exception:
                    continue
            
            # --- GUARDADO AUTOMÁTICO AL FINALIZAR ---
            if self.prospectos_datos:
                nombre_archivo = os.path.join(constantes.CARPETA_DATOS, f"{rubro}.json")
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