import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import random
import time
import os
import webbrowser
import re
import urllib.parse
import unicodedata
from selenium import webdriver
import shutil
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
from src.estrategia_fotos_reviews import extraer_fotos_de_resena
from src.scroll_strategies import estrategia_scroll_js_focalizado, estrategia_scroll_teclado
from src.utils import calcular_calidad_lead
from controlador_ia import generar_contenido_ia, limpiar_datos_ia, generar_datos_demo
from generador_web import generar_web_profesional
from src.enriquecedor import buscar_datos_externos, ejecutar_enriquecimiento_global
from src.ui_search import BuscadorVisual

def abrir_whatsapp(nombre, telefono):
    """Abre WhatsApp Web con un mensaje personalizado."""
    tel_limpio = "".join(filter(str.isdigit, str(telefono)))
    
    # --- CORRECCIÓN DE FORMATO ARGENTINA ---
    # 1. Si empieza con 0 (ej: 0280...), quitamos el 0 inicial
    if tel_limpio.startswith("0"):
        tel_limpio = tel_limpio[1:]
    
    # 2. Si no tiene el prefijo de país 54, lo agregamos con el 9 de móvil (549)
    if not tel_limpio.startswith("54"):
        tel_limpio = "549" + tel_limpio
        
    # 3. Si tiene el 549 pero le sigue un 0 (ej: 5490280...), quitamos ese 0
    if tel_limpio.startswith("5490"):
        tel_limpio = "549" + tel_limpio[4:]

    mensaje = f"""Hola, {nombre}. Mi nombre es Mauricio Belforte, me dedico al desarrollo de páginas web. 
Soy de Trelew.

Estoy ofreciendo mis servicios a distintos negocios y profesionales locales.

Si gustan pueden pasar a ver estos 2 modelos de plantillas que estoy trabajando. Se pueden adaptar y modificar rapidamente.
Modelo 1: https://abogadotrelew.netlify.app/
Modelo 2: https://cafeteriatrelew.netlify.app/

Sino tambien podemos trabajar en una página con un diseño mas elaborado y funcionalidades más especificas pero a un costo mayor.

Pueden ver más de mis trabajos en mi portfolio: https://mauriciobelforte.github.io/mi-portfolio/.

Si les sirve, no duden en contactarme. Saludos!"""
    
    url = f"https://wa.me/{tel_limpio}?text={urllib.parse.quote(mensaje)}"
    webbrowser.open(url)

class TrelewLeadApp:
    """
    Aplicación principal para la prospección de clientes en Trelew.
    Gestiona la interfaz de usuario y la lógica de scraping de Google Maps.
    """
    def __init__(self, root):
        self.root = root
        self.root.title(constantes.TITULO_APP)
        self.root.geometry("1100x700")
        self.root.state('zoomed')
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
        self.archivo_activo = None # Archivo JSON sobre el que se está trabajando
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

        self.btn_rapido = ttk.Button(search_frame, text=constantes.BTN_MODO_RAPIDO, command=lambda: self.start_scraping_thread("js"))
        self.btn_rapido.pack(side="left", padx=5)

        self.btn_humano = ttk.Button(search_frame, text=constantes.BTN_MODO_HUMANO, command=lambda: self.start_scraping_thread("teclado"))
        self.btn_humano.pack(side="left", padx=5)

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

        # Botón Demo Web V1
        self.btn_demo_v1 = ttk.Button(search_frame, text="🎨 DEMO WEB V1", command=lambda: self.lanzar_demo_web("v1"))
        self.btn_demo_v1.pack(side="left", padx=5)

        # Botón Demo Web V2
        self.btn_demo_v2 = ttk.Button(search_frame, text="🎨 DEMO WEB V2", command=lambda: self.lanzar_demo_web("v2"))
        self.btn_demo_v2.pack(side="left", padx=5)

        # --- Contenedor Principal (Split View: Maestro-Detalle) ---
        main_container = tk.Frame(self.root, bg=constantes.COLOR_FONDO)
        main_container.pack(fill="both", expand=True, padx=20, pady=10)

        # Panel Izquierdo: Lista de Leads (Treeview)
        left_panel = tk.Frame(main_container, bg=constantes.COLOR_BLANCO, relief="flat")
        left_panel.pack(side="left", fill="both", expand=True)

        tk.Label(left_panel, text=constantes.ETIQUETA_RESULTADOS, font=constantes.FUENTE_NEGRITA, bg=constantes.COLOR_BLANCO, pady=5).pack()

        columns = ("nombre", "estado", "propuesta", "web")
        self.tree = ttk.Treeview(left_panel, columns=columns, show="headings")
        self.tree.heading("nombre", text=constantes.COLUMNA_NOMBRE)
        self.tree.heading("estado", text=constantes.COLUMNA_ESTADO)
        self.tree.heading("propuesta", text="Propuesta")
        self.tree.heading("web", text="Web")
        self.tree.column("nombre", width=250)
        self.tree.column("estado", width=100)
        self.tree.column("propuesta", width=100, anchor="center")
        self.tree.column("web", width=80, anchor="center")
        
        # --- BUSCADOR / FILTRO (NUEVO) ---
        # Instanciamos el buscador pasándole el panel y el treeview.
        # Se empaqueta automáticamente dentro de left_panel.
        self.buscador = BuscadorVisual(left_panel, self.tree)

        # Botón para AGREGAR MANUALMENTE (Debajo del buscador)
        self.btn_agregar = tk.Button(left_panel, text="➕ Agregar Emprendimiento", bg="#6c757d", fg="white",
                                     font=constantes.FUENTE_PEQUENA_NEGRITA, relief="flat", cursor="hand2", state="disabled",
                                     command=self.abrir_alta_manual)
        self.btn_agregar.pack(fill="x", padx=5, pady=(0, 5))
        
        # Empaquetamos el treeview DESPUÉS del buscador para que quede abajo
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

        # --- BOTÓN GLOBAL (Siempre visible abajo) ---
        self.btn_global_enrich = tk.Button(self.right_panel, text="🌍 ENRIQUECEDOR MASIVO (TODO)", 
                                           bg=constantes.COLOR_PELIGRO, fg="white",
                                           font=constantes.FUENTE_NEGRITA, relief="flat", cursor="hand2",
                                           command=self.lanzar_enriquecimiento_global)
        self.btn_global_enrich.pack(side="bottom", fill="x", pady=(10, 20))

        # --- SCROLLABLE AREA (Canvas + Scrollbar) ---
        canvas_frame = tk.Frame(self.right_panel, bg=constantes.COLOR_FONDO)
        canvas_frame.pack(side="top", fill="both", expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg=constantes.COLOR_FONDO, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = tk.Frame(self.canvas, bg=constantes.COLOR_FONDO)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
        canvas_frame.bind('<Enter>', lambda e: self.canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas_frame.bind('<Leave>', lambda e: self.canvas.unbind_all("<MouseWheel>"))

        # Mensaje de ayuda inicial
        self.card_placeholder = tk.Label(self.scrollable_frame, text=constantes.TEXTO_PLACEHOLDER_CARD, 
                                         font=constantes.FUENTE_ITALICA, fg=constantes.COLOR_TEXTO_TENUE, bg=constantes.COLOR_FONDO, pady=100)
        self.card_placeholder.pack()

        # Marco de la Card (invisible hasta que se seleccione algo)
        self.detail_card = tk.Frame(self.scrollable_frame, bg=constantes.COLOR_BLANCO, highlightbackground=constantes.COLOR_BORDE, highlightthickness=1)
        
        # --- Barra de Estado (Feedback al usuario) ---
        self.status_label = tk.Label(self.root, text=constantes.ESTADO_LISTO, bd=1, relief="flat", anchor="w", bg=constantes.COLOR_FONDO_ESTADO, padx=10)
        self.status_label.pack(side="bottom", fill="x")

    def log(self, mensaje):
        """Actualiza la barra de estado inferior."""
        self.status_label.config(text=f"⚙️ {mensaje}")
        self.root.update_idletasks()

    def _get_propuesta_status_text(self, datos):
        """Helper para obtener el texto visual del estado de la propuesta."""
        return "✅ Enviada" if datos.get("propuesta_enviada") else "❌ Pendiente"

    def _get_web_status_text(self, datos):
        """Helper para obtener el texto visual si tiene web."""
        return "🌐 Sí" if datos.get("website") else "-"

    def normalizar_texto(self, texto):
        """Normaliza texto para comparación: minúsculas, sin acentos, sin caracteres especiales."""
        if not texto: return ""
        try:
            # Descomponer caracteres (ej: á -> a + ´)
            texto = unicodedata.normalize('NFD', str(texto))
            # Filtrar solo caracteres ASCII (elimina los acentos separados)
            texto = texto.encode('ascii', 'ignore').decode("utf-8").lower()
            # Eliminar todo lo que no sea letra, número o espacio
            texto = re.sub(r'[^a-z0-9\s]', '', texto)
            # Colapsar espacios múltiples
            return " ".join(texto.split())
        except:
            return str(texto).lower().strip()

    def limpiar_nombre(self, nombre):
        """Elimina sufijos de estado de navegación del nombre del negocio."""
        if not nombre: return ""
        
        # --- NUEVO: Limpieza de prefijos de anuncios ---
        # Detecta "Patrocinado", "Anuncio", "Sponsored" al inicio que causan ERROR SYNC
        patron_ad = r"(?i)^(Patrocinado|Anuncio|Sponsored|Ad)\s*[-·•.]?\s*"
        nombre = re.sub(patron_ad, "", nombre)

        # Regex robusto: detecta guiones, puntos medios (·) y variaciones de "Vínculo visitado"
        patron = r"(?i)(\s*[-·]?\s*(Vínculo visitado|Visited link|Enlace visitado))"
        nombre_limpio = re.sub(patron, "", nombre)
        
        # --- CORRECCIÓN ERROR SYNC ---
        # Google ahora agrega la categoría y rating en el aria-label separados por "·"
        if "·" in nombre_limpio:
            nombre_limpio = nombre_limpio.split("·")[0]
        # Google ahora agrega la categoría y rating en el aria-label separados por "·" o "•"
        for sep in ["·", "•"]:
            if sep in nombre_limpio:
                nombre_limpio = nombre_limpio.split(sep)[0]
            
        return nombre_limpio.strip()

    def fusionar_datos(self, datos_prioritarios, datos_secundarios):
        """
        Combina dos diccionarios. Mantiene los datos de 'datos_prioritarios' 
        salvo que estén vacíos y 'datos_secundarios' tenga información.
        """
        resultado = datos_prioritarios.copy()
        valores_nulos = ["Sin teléfono", "No disponible", "No especificado", "N/A", "No detectado", "", None, "General"]
        
        for k, v in datos_secundarios.items():
            val_prio = resultado.get(k)
            
            # Si el prioritario no tiene dato válido y el secundario sí, lo tomamos
            if val_prio in valores_nulos and v not in valores_nulos:
                resultado[k] = v
            
            # Fusión inteligente de listas (imágenes, enlaces)
            elif isinstance(v, list) and isinstance(val_prio, list):
                if k in ["imagenes", "enlaces_extra"]:
                    # Unir y quitar duplicados
                    resultado[k] = list(set(val_prio + v))
                elif k == "horarios_detallados":
                    if not val_prio and v: resultado[k] = v
                elif not val_prio and v:
                    resultado[k] = v
        return resultado

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
            self.archivo_activo = seleccion # Recordar qué archivo estamos editando
            
            # Rellenar Treeview ORDENADO POR PRIORIDAD
            # Convertimos a lista de tuplas y ordenamos usando la función de utilidad
            items_ordenados = sorted(self.prospectos_datos.items(), key=lambda x: calcular_calidad_lead(x[1]), reverse=True)
            
            for nombre, datos in items_ordenados:
                prop_status = self._get_propuesta_status_text(datos)
                web_status = self._get_web_status_text(datos)
                # IMPORTANTE: Asignar iid=nombre para poder actualizar la fila después
                self.tree.insert("", "end", iid=nombre, values=(nombre, "GUARDADO 💾", prop_status, web_status))
            
            # Actualizar el cache del buscador con los nuevos datos cargados
            self.buscador.actualizar_cache()
            
            self.log(f"Ficha '{seleccion}' cargada exitosamente. ({len(datos_cargados)} registros)")
            self.btn_agregar.config(state="normal") # Habilitar botón de agregar
            
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
        
        # Botón de Enriquecer (Arriba del todo para indicar que busca los datos de abajo)
        btn_enrich = tk.Button(body, text="🌍 BUSCAR DATOS (Enriquecer)", bg=constantes.COLOR_BTN_BUSCAR, fg=constantes.COLOR_BLANCO, 
                           font=constantes.FUENTE_PEQUENA_NEGRITA, relief="flat", cursor="hand2",
                           command=lambda: self.lanzar_busqueda_externa(nombre))
        btn_enrich.pack(fill="x", pady=(0, 10))
        
        # Filas de información
        self.create_info_row(body, "Categoría:", datos.get('categoria', 'General'))
        self.create_info_row(body, constantes.ETIQUETA_TELEFONO, datos.get('telefono', 'No disponible'))
        self.create_info_row(body, constantes.ETIQUETA_WEB, datos.get('website', constantes.VALOR_SIN_WEB))
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
        tk.Button(body, text=constantes.BTN_CONTACTAR_TODOS, bg=c_all, fg=constantes.COLOR_BLANCO, font=constantes.FUENTE_PEQUENA_NEGRITA, relief="flat", cursor="hand2" if has_any else "arrow", command=lambda n=nombre, d=datos: self.contactar_todos(n, d) if has_any else None).pack(fill="x", pady=(5, 5))

        # Botón de información detallada (Ficha Técnica)
        btn_info = tk.Button(body, text=constantes.BTN_VER_FICHA, bg=constantes.COLOR_BTN_INFO, fg=constantes.COLOR_BLANCO, 
                           font=constantes.FUENTE_NEGRITA, relief="flat", cursor="hand2",
                           command=lambda: self.mostrar_info_detallada(nombre, datos))
        btn_info.pack(fill="x", pady=5)

        # --- SECCIÓN WEB MANUAL ---
        web_frame = tk.Frame(body, bg=constantes.COLOR_BLANCO)
        web_frame.pack(fill="x", pady=5)
        
        tiene_web = datos.get("website")
        if tiene_web:
            btn_web_text = "✏️ Editar Web Existente"
            btn_web_bg = constantes.COLOR_BTN_INFO 
        else:
            btn_web_text = "🌐 Ingresar una WEB"
            btn_web_bg = constantes.COLOR_BTN_INFO 
            
        tk.Button(web_frame, text=btn_web_text, bg=btn_web_bg, fg="white",
                  font=constantes.FUENTE_NEGRITA, relief="flat", cursor="hand2",
                  command=lambda: self.gestionar_web_manual(nombre)).pack(fill="x")

        # Botón para ver en Google manual (ahora solo y full width)
        btn_manual_google = tk.Button(body, text="👁️ VER EN GOOGLE", bg="#5f3dc4", fg=constantes.COLOR_BLANCO, 
                           font=constantes.FUENTE_PEQUENA_NEGRITA, relief="flat", cursor="hand2",
                           command=lambda: self.abrir_busqueda_manual(nombre, datos.get('categoria') or ''))
        btn_manual_google.pack(fill="x", pady=5)
        
        # Botones Generar Web (IA) V1 y V2
        btn_web_frame = tk.Frame(body, bg=constantes.COLOR_BLANCO)
        btn_web_frame.pack(fill="x", pady=(10, 5))
        btn_web_frame.columnconfigure(0, weight=1)
        btn_web_frame.columnconfigure(1, weight=1)

        # --- BOTÓN MAQUETA 1 ---
        # Llama a lanzar_generacion_web pasando "v1" como argumento
        btn_web_v1 = tk.Button(btn_web_frame, text="✨ WEB V1 (IA)", bg="#efc355", fg="#111111", 
                           font=constantes.FUENTE_NEGRITA, relief="flat", cursor="hand2",
                           command=lambda: self.lanzar_generacion_web(nombre, datos, "v1"))
        btn_web_v1.grid(row=0, column=0, padx=2, sticky="ew")

        # --- BOTÓN MAQUETA 2 ---
        # Llama a lanzar_generacion_web pasando "v2" como argumento
        btn_web_v2 = tk.Button(btn_web_frame, text="✨ WEB V2 (IA)", bg="#efc355", fg="#111111", 
                           font=constantes.FUENTE_NEGRITA, relief="flat", cursor="hand2",
                           command=lambda: self.lanzar_generacion_web(nombre, datos, "v2"))
        btn_web_v2.grid(row=0, column=1, padx=2, sticky="ew")

        # --- SECCIÓN ESTADO DE PROPUESTA ---
        propuesta_frame = tk.Frame(body, bg=constantes.COLOR_BLANCO)
        propuesta_frame.pack(fill="x", pady=(15, 5))
        
        estado_propuesta = datos.get("propuesta_enviada", False)
        if estado_propuesta:
            btn_prop_text = "↩️ Desmarcar Propuesta"
            btn_prop_bg = "#ff8787" # Rojo claro para cancelar
        else:
            btn_prop_text = "✅ Marcar Propuesta ENVIADA"
            btn_prop_bg = "#69db7c" # Verde claro para confirmar
            
        tk.Button(propuesta_frame, text=btn_prop_text, bg=btn_prop_bg, fg="white",
                  font=constantes.FUENTE_NEGRITA, relief="flat", cursor="hand2",
                  command=lambda: self.toggle_propuesta(nombre)).pack(fill="x")


    def contactar_todos(self, nombre, datos):
        """Abre todos los canales de contacto disponibles para un negocio en pestañas separadas."""
        tel = datos.get('telefono')
        if tel and "Sin" not in str(tel) and "No" not in str(tel):
            abrir_whatsapp(nombre, tel)
            time.sleep(0.5) # Pausa para que el sistema operativo procese la apertura

        fb = datos.get('facebook')
        if fb and "No detectado" not in fb:
            webbrowser.open(fb)
            time.sleep(0.5)

        ig = datos.get('instagram')
        if ig and "No detectado" not in ig:
            webbrowser.open(ig)
            time.sleep(0.5)

        email = datos.get('email')
        if email and "No detectado" not in email:
            webbrowser.open(f"mailto:{email}")

    def toggle_propuesta(self, nombre):
        """Cambia el estado de 'propuesta_enviada' y actualiza la UI y el archivo."""
        if nombre in self.prospectos_datos:
            datos = self.prospectos_datos[nombre]
            # Invertir estado
            datos["propuesta_enviada"] = not datos.get("propuesta_enviada", False)
            self.prospectos_datos[nombre] = datos
            
            # Guardar cambios en el archivo correspondiente
            # Usamos el archivo activo si existe, sino intentamos deducirlo
            if self.archivo_activo:
                 self.gestor_datos.guardar_datos(self.archivo_activo, self.prospectos_datos)
            else:
                 rubro = self.entry_rubro.get()
                 if rubro:
                     self.gestor_datos.guardar_datos(f"{rubro}.json", self.prospectos_datos)

            # Actualizar fila en Treeview sin perder el estado de scraping
            if self.tree.exists(nombre):
                vals = self.tree.item(nombre)['values']
                estado_scraping = vals[1] # Mantener "NUEVO", "GUARDADO", etc.
                prop_status = self._get_propuesta_status_text(datos)
                web_status = self._get_web_status_text(datos)
                self.tree.item(nombre, values=(nombre, estado_scraping, prop_status, web_status))
            
            # Refrescar panel lateral para actualizar el botón
            self.mostrar_detalle(None)

    def gestionar_web_manual(self, nombre):
        """Permite al usuario ingresar manualmente una URL para el negocio."""
        if nombre in self.prospectos_datos:
            datos = self.prospectos_datos[nombre]
            current_web = datos.get("website", "")
            
            new_web = simpledialog.askstring("Gestión Web", f"Ingresa la URL del sitio web para:\n{nombre}", initialvalue=current_web, parent=self.root)
            
            if new_web is not None: # Si no canceló
                if new_web.strip():
                    datos["website"] = new_web.strip()
                else:
                    # Si lo dejó vacío, eliminamos la clave (asumimos que borró la web)
                    if "website" in datos:
                        del datos["website"]
                
                self.prospectos_datos[nombre] = datos
                
                # Guardar
                if self.archivo_activo:
                     self.gestor_datos.guardar_datos(self.archivo_activo, self.prospectos_datos)
                else:
                     rubro = self.entry_rubro.get()
                     if rubro:
                         self.gestor_datos.guardar_datos(f"{rubro}.json", self.prospectos_datos)

                # Actualizar UI
                if self.tree.exists(nombre):
                    vals = self.tree.item(nombre)['values']
                    estado = vals[1]
                    propuesta = vals[2]
                    web_status = self._get_web_status_text(datos)
                    self.tree.item(nombre, values=(nombre, estado, propuesta, web_status))
                
                self.mostrar_detalle(None)

    def abrir_busqueda_manual(self, nombre, categoria):
        """Abre una búsqueda de Google en el navegador predeterminado para inspección manual."""
        query = f"{nombre} {categoria} Trelew"
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        webbrowser.open(url)

    def abrir_edicion_ficha(self, parent, nombre, datos):
        """Abre una ventana de edición para los datos del lead."""
        edit_win = tk.Toplevel(self.root)
        edit_win.title(f"Editar: {nombre}")
        edit_win.geometry("500x600")
        edit_win.configure(bg=constantes.COLOR_BLANCO)
        edit_win.transient(parent) # Hacerla modal respecto a la ficha
        edit_win.grab_set()

        tk.Label(edit_win, text="Editar Información", font=constantes.FUENTE_SUBTITULO, bg=constantes.COLOR_BLANCO, fg=constantes.COLOR_PRIMARIO, pady=15).pack()

        form_frame = tk.Frame(edit_win, bg=constantes.COLOR_BLANCO, padx=20)
        form_frame.pack(fill="both", expand=True)

        entries = {}

        def crear_campo(label, key, valor_inicial):
            f = tk.Frame(form_frame, bg=constantes.COLOR_BLANCO, pady=5)
            f.pack(fill="x")
            tk.Label(f, text=label, font=constantes.FUENTE_NEGRITA, bg=constantes.COLOR_BLANCO, anchor="w", fg=constantes.COLOR_TEXTO_OSCURO).pack(fill="x")
            e = tk.Entry(f, font=constantes.FUENTE_NORMAL, bg="#f8f9fa", relief="flat", highlightthickness=1, highlightbackground=constantes.COLOR_BORDE)
            # Limpiamos valores por defecto para facilitar la edición
            val = str(valor_inicial) if valor_inicial and valor_inicial not in ["No detectado", "Sin teléfono", "No disponible"] else ""
            e.insert(0, val)
            e.pack(fill="x", ipady=5)
            entries[key] = e

        # Campos editables
        crear_campo("Nombre del Negocio:", "nombre", nombre)
        crear_campo("Rubro / Categoría:", "categoria", datos.get("categoria", ""))
        crear_campo("Teléfono:", "telefono", datos.get("telefono", ""))
        crear_campo("Email:", "email", datos.get("email", ""))
        crear_campo("Sitio Web:", "website", datos.get("website", ""))
        crear_campo("Facebook:", "facebook", datos.get("facebook", ""))
        crear_campo("Instagram:", "instagram", datos.get("instagram", ""))

        def guardar():
            nuevo_nombre = entries["nombre"].get().strip()
            if not nuevo_nombre:
                messagebox.showwarning("Error", "El nombre es obligatorio.", parent=edit_win)
                return

            # Actualizar datos en el diccionario
            datos["categoria"] = entries["categoria"].get().strip()
            datos["telefono"] = entries["telefono"].get().strip() or "Sin teléfono"
            
            email = entries["email"].get().strip()
            datos["email"] = email if email else "No detectado"
            
            web = entries["website"].get().strip()
            if web: datos["website"] = web
            elif "website" in datos: del datos["website"] # Si borra la web, la quitamos
            
            fb = entries["facebook"].get().strip()
            datos["facebook"] = fb if fb else "No detectado"
            
            ig = entries["instagram"].get().strip()
            datos["instagram"] = ig if ig else "No detectado"

            # Manejo de cambio de nombre (clave del diccionario)
            nombre_final = nombre
            if nuevo_nombre != nombre:
                self.prospectos_datos[nuevo_nombre] = datos
                if nombre in self.prospectos_datos:
                    del self.prospectos_datos[nombre]
                nombre_final = nuevo_nombre

            # Guardar en archivo
            if self.archivo_activo:
                 self.gestor_datos.guardar_datos(self.archivo_activo, self.prospectos_datos)
            else:
                 rubro = self.entry_rubro.get()
                 if rubro:
                     self.gestor_datos.guardar_datos(f"{rubro}.json", self.prospectos_datos)

            # Actualizar UI Principal (Treeview)
            if self.tree.exists(nombre):
                vals = self.tree.item(nombre)['values']
                estado = vals[1]
                propuesta = self._get_propuesta_status_text(datos)
                web_status = self._get_web_status_text(datos)
                
                if nuevo_nombre != nombre:
                    self.tree.delete(nombre)
                    self.tree.insert("", "end", iid=nuevo_nombre, values=(nuevo_nombre, estado, propuesta, web_status))
                    self.tree.selection_set(nuevo_nombre)
                else:
                    self.tree.item(nombre, values=(nombre, estado, propuesta, web_status))

            # Actualizar Card Lateral
            self.mostrar_detalle(None)

            # Cerrar ventana de edición y refrescar la ficha técnica
            edit_win.destroy()
            parent.destroy() # Cerramos la ficha vieja
            self.mostrar_info_detallada(nombre_final, datos) # Abrimos la nueva actualizada

    def abrir_alta_manual(self):
        """Abre un formulario completo para dar de alta un nuevo emprendimiento manualmente."""
        alta_win = tk.Toplevel(self.root)
        alta_win.title("Nuevo Emprendimiento")
        alta_win.geometry("550x750")
        alta_win.configure(bg=constantes.COLOR_BLANCO)
        alta_win.transient(self.root)
        alta_win.grab_set()

        # Header
        tk.Label(alta_win, text="Agregar Nuevo Lead", font=constantes.FUENTE_TITULO, bg=constantes.COLOR_BLANCO, fg=constantes.COLOR_PRIMARIO, pady=15).pack()
        tk.Label(alta_win, text="Completa los datos que tengas. Los vacíos se guardarán como 'No detectado'.", font=constantes.FUENTE_PEQUENA, bg=constantes.COLOR_BLANCO, fg=constantes.COLOR_TEXTO_TENUE).pack(pady=(0, 10))

        # Contenedor con Scroll para el formulario
        canvas = tk.Canvas(alta_win, bg=constantes.COLOR_BLANCO, highlightthickness=0)
        scrollbar = ttk.Scrollbar(alta_win, orient="vertical", command=canvas.yview)
        form_frame = tk.Frame(canvas, bg=constantes.COLOR_BLANCO, padx=20, pady=10)

        form_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=form_frame, anchor="nw", width=500)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        entries = {}

        def crear_campo(label, key, placeholder=""):
            f = tk.Frame(form_frame, bg=constantes.COLOR_BLANCO, pady=5)
            f.pack(fill="x")
            tk.Label(f, text=label, font=constantes.FUENTE_NEGRITA, bg=constantes.COLOR_BLANCO, anchor="w", fg=constantes.COLOR_TEXTO_OSCURO).pack(fill="x")
            e = tk.Entry(f, font=constantes.FUENTE_NORMAL, bg="#f8f9fa", relief="flat", highlightthickness=1, highlightbackground=constantes.COLOR_BORDE)
            if placeholder:
                e.insert(0, placeholder) # Valor por defecto sugerido
            e.pack(fill="x", ipady=5)
            entries[key] = e

        # --- CAMPOS DEL FORMULARIO ---
        crear_campo("Nombre del Negocio (*):", "nombre")
        
        # Categoría por defecto: Usar el archivo activo (JSON cargado) en lugar del buscador
        cat_default = self.archivo_activo.replace(".json", "") if self.archivo_activo else self.entry_rubro.get()
        
        crear_campo("Rubro / Categoría:", "categoria", cat_default)
        crear_campo("Dirección:", "direccion")
        crear_campo("Teléfono (con cód. área):", "telefono")
        crear_campo("Horarios (Texto libre):", "horario")
        crear_campo("Sitio Web:", "website")
        crear_campo("Email:", "email")
        crear_campo("Facebook (URL):", "facebook")
        crear_campo("Instagram (URL):", "instagram")
        crear_campo("Rating (1.0 - 5.0):", "rating", "5.0")

        def guardar_nuevo():
            nombre = entries["nombre"].get().strip()
            if not nombre:
                messagebox.showwarning("Faltan datos", "El nombre del negocio es obligatorio.", parent=alta_win)
                return
            
            if nombre in self.prospectos_datos:
                messagebox.showerror("Duplicado", f"El negocio '{nombre}' ya existe en la lista.", parent=alta_win)
                return

            # Construir diccionario de datos
            nuevo_lead = {
                "categoria": entries["categoria"].get().strip() or "General",
                "direccion": entries["direccion"].get().strip() or "No disponible",
                "telefono": entries["telefono"].get().strip() or "Sin teléfono",
                "horario": entries["horario"].get().strip() or "No especificado",
                "website": entries["website"].get().strip() or None, # None para que no salga "No tiene" si está vacío
                "email": entries["email"].get().strip() or "No detectado",
                "facebook": entries["facebook"].get().strip() or "No detectado",
                "instagram": entries["instagram"].get().strip() or "No detectado",
                "rating": f"{entries['rating'].get().strip()} estrellas" if entries["rating"].get().strip() else "N/A",
                "comentarios": [], # Lista vacía inicial
                "imagenes": [],
                "horarios_detallados": [],
                "propuesta_enviada": False
            }

            # Guardar en memoria y disco
            self.prospectos_datos[nombre] = nuevo_lead
            archivo_destino = self.archivo_activo if self.archivo_activo else f"{self.entry_rubro.get()}.json"
            self.gestor_datos.guardar_datos(archivo_destino, self.prospectos_datos)

            # Actualizar UI
            web_status = self._get_web_status_text(nuevo_lead)
            self.tree.insert("", 0, iid=nombre, values=(nombre, "MANUAL ✍️", "❌ Pendiente", web_status)) # Insertar al principio
            self.tree.selection_set(nombre) # Seleccionar el nuevo
            self.mostrar_detalle(None) # Mostrar ficha
            self.buscador.actualizar_cache() # Actualizar buscador
            
            alta_win.destroy()
            messagebox.showinfo("Éxito", f"Se agregó '{nombre}' a la lista.")

        btn_guardar = tk.Button(form_frame, text="💾 AGREGAR A LA LISTA", bg=constantes.COLOR_BTN_INFO, fg="white",
                                font=constantes.FUENTE_NEGRITA, relief="flat", cursor="hand2", command=guardar_nuevo)
        btn_guardar.pack(pady=20, fill="x")

        btn_guardar = tk.Button(edit_win, text="💾 GUARDAR CAMBIOS", bg=constantes.COLOR_BTN_INFO, fg="white",
                                font=constantes.FUENTE_NEGRITA, relief="flat", cursor="hand2", command=guardar)
        btn_guardar.pack(pady=20, fill="x", padx=20)

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

        # Header con botón de edición
        header_frame = tk.Frame(info_frame, bg=constantes.COLOR_BLANCO)
        header_frame.pack(fill="x", pady=15)
        
        tk.Label(header_frame, text=constantes.ENCABEZADO_FICHA, font=constantes.FUENTE_SUBTITULO, bg=constantes.COLOR_BLANCO, fg=constantes.COLOR_PRIMARIO).pack(side="left")
        
        tk.Button(header_frame, text="✏️ Editar", bg=constantes.COLOR_BTN_INFO, fg="white", 
                  font=constantes.FUENTE_PEQUENA_NEGRITA, relief="flat", cursor="hand2",
                  command=lambda: self.abrir_edicion_ficha(top, nombre, datos)).pack(side="right")

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
        
        # --- NUEVO: Mostrar Horarios Detallados ---
        horarios_det = datos.get("horarios_detallados", [])
        if horarios_det:
            tk.Label(info_frame, text="Cronograma Semanal:", font=constantes.FUENTE_NEGRITA, bg=constantes.COLOR_BLANCO, width=15, anchor="w", fg=constantes.COLOR_TEXTO_ETIQUETA).pack(fill="x", pady=(5, 0))
            for h in horarios_det:
                tk.Label(info_frame, text=f"• {h}", font=constantes.FUENTE_PEQUENA, bg=constantes.COLOR_BLANCO, anchor="w", padx=20).pack(fill="x")
        
        add_row("Valoración:", datos.get("rating", "Sin reseñas"))
        add_row("Teléfono:", datos.get("telefono", "Sin teléfono"))
        if datos.get("whatsapp", "No") == "Probable":
            add_row("WhatsApp:", "✅ Probable")
        if datos.get("email") and datos.get("email") != "No detectado":
            add_row("Email:", datos["email"])
        if datos.get("facebook"): add_row("Facebook:", datos["facebook"])
        if datos.get("instagram"): add_row("Instagram:", datos["instagram"])
        add_row("Sitio Web:", datos.get("website", "No tiene"))
        
        # Mostrar enlaces extra encontrados en la web
        enlaces = datos.get("enlaces_extra", [])
        if enlaces:
            for i, link in enumerate(enlaces, 1):
                add_row(f"Web Extra {i}:", link)

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

    def lanzar_generacion_web(self, nombre, datos, version="v1"):
        """Inicia el proceso de generación web en un hilo aparte."""
        if messagebox.askyesno(f"Generar Web {version.upper()}", f"¿Deseas generar automáticamente el sitio web ({version.upper()}) para:\n{nombre}?"):
            threading.Thread(target=self.ejecutar_generacion_web_thread, args=(nombre, datos, version), daemon=True).start()

    def ejecutar_generacion_web_thread(self, nombre, datos, version="v1"):
        self.log(f"🚀 Iniciando motor de IA ({version.upper()}) para {nombre}...")
        try:
            # --- Filtrado de testimonios duplicados ---
            # Aseguramos que no haya textos repetidos antes de seleccionar los mejores para la web
            if datos.get("comentarios"):
                comentarios_unicos = []
                textos_vistos = set()
                for c in datos["comentarios"]:
                    texto = c.get("texto", "").strip()
                    if texto and texto not in textos_vistos:

                        textos_vistos.add(texto)
                        comentarios_unicos.append(c)
                datos["comentarios"] = comentarios_unicos
            
            # 1. Limpieza de datos
            self.log("🧹 Fase 1: Normalizando datos con IA...")
            datos_limpios = limpiar_datos_ia(datos)
            

            # 2. Generación de contenido
            self.log("🧠 Fase 2: Redactando textos persuasivos...")
            textos_ai = generar_contenido_ia(nombre, datos_limpios)
            
            # 3. Construcción de la web
            self.log(f"🎨 Fase 3: Maquetando sitio web ({version.upper()})...")
            resultado = generar_web_profesional(nombre, datos_limpios, textos_ai, version=version)
            

            self.log("✅ ¡Sitio web creado con éxito!")
            self.root.after(0, lambda: messagebox.showinfo("Proceso Finalizado", f"Web generada correctamente.\n\n{resultado}"))
            
        except Exception as e:
            error_msg = str(e)
            self.log(f"❌ Error en generación: {error_msg}")
            self.root.after(0, lambda: messagebox.showerror("Error Crítico", f"No se pudo generar la web:\n{error_msg}"))

    def lanzar_demo_web(self, version="v1"):
        # Prioridad: 1. Archivo seleccionado (combo_fichas) | 2. Texto del buscador (entry_rubro)
        categoria_demo = self.combo_fichas.get()
        origen = "Ficha Guardada"

        if not categoria_demo:
            categoria_demo = self.entry_rubro.get()
            origen = "Buscador"

        if not categoria_demo:
            messagebox.showwarning("Atención", "No se detectó ninguna categoría.\nSelecciona una ficha guardada o escribe un rubro.")
            return
        
        if messagebox.askyesno(f"Generar Demo {version.upper()}", f"¿Crear una web de demostración ({version.upper()}) para '{categoria_demo}'?\n(Origen: {origen})"):
            threading.Thread(target=self.ejecutar_demo_web, args=(categoria_demo, version), daemon=True).start()

    def ejecutar_demo_web(self, rubro, version="v1"):
        self.log(f"🎲 Inventando negocio para demo ({version.upper()}) de {rubro}...")
        try:
            datos_fake = generar_datos_demo(rubro)
            if not datos_fake:
                raise Exception("La IA no pudo generar los datos ficticios.")
            
            nombre = datos_fake.get('nombre', f"Demo {rubro}")
            self.log(f"✨ Negocio: {nombre}. Generando contenidos...")
            
            textos_ai = generar_contenido_ia(nombre, datos_fake)
            
            self.log(f"🎨 Maquetando demo ({version.upper()})...")
            # Guardamos en carpeta 'demos' para que se pueda subir a GitHub
            resultado = generar_web_profesional(nombre, datos_fake, textos_ai, carpeta_salida="demos", version=version)
            
            self.log("✅ Demo creada.")
            self.root.after(0, lambda: messagebox.showinfo("Demo Finalizada", f"Web generada para {nombre}:\n\n{resultado}"))
            
        except Exception as e:
            self.log(f"❌ Error demo: {e}")

    def start_scraping_thread(self, estrategia="teclado"):
        """Inicia el proceso de búsqueda en un hilo separado para evitar bloqueos de UI."""
        rubro = self.entry_rubro.get()
        if not rubro:
            messagebox.showwarning("Atención", constantes.MSJ_ADVERTENCIA_RUBRO)
            return
        
        self.archivo_activo = f"{rubro}.json" # Establecer archivo activo para guardados futuros
        self.btn_rapido.config(state="disabled")
        self.btn_humano.config(state="disabled")
        self.tree.delete(*self.tree.get_children())
        
        # --- LÓGICA DE FUSIÓN: Cargar datos previos si existen ---
        self.prospectos_datos = {}
        
        # Usamos GestorDatos para cargar (Refactor Fase 3)
        self.prospectos_datos = self.gestor_datos.cargar_datos(f"{rubro}.json")
        
        if self.prospectos_datos:
            # Ordenar históricos por prioridad también
            items_ordenados = sorted(self.prospectos_datos.items(), key=lambda x: calcular_calidad_lead(x[1]), reverse=True)
            
            for nombre, datos in items_ordenados:
                prop_status = self._get_propuesta_status_text(datos)
                web_status = self._get_web_status_text(datos)
                self.tree.insert("", "end", iid=nombre, values=(nombre, "HISTÓRICO 📁", prop_status, web_status))
            
            # Actualizar cache del buscador con históricos
            self.buscador.actualizar_cache()
            self.btn_agregar.config(state="normal") # Habilitar botón agregar
            self.log(f"Se cargaron {len(self.prospectos_datos)} registros previos. Buscando actualizaciones...")
        
        threading.Thread(target=self.ejecutar_scraping, args=(rubro, estrategia), daemon=True).start()

    def lanzar_enriquecimiento_masivo(self):
        """Enriquecimiento local (solo la lista actual)."""
        if not self.prospectos_datos:
            messagebox.showwarning("Atención", constantes.MSJ_ADVERTENCIA_SIN_LISTA)
            return
        
        rubro = self.entry_rubro.get()
        confirm = messagebox.askyesno("Confirmar", constantes.MSJ_CONFIRMAR_ENRIQUECIMIENTO.format(len(self.prospectos_datos)))
        if confirm:
            self.log("Iniciando enriquecimiento masivo...")
            threading.Thread(target=self.ejecutar_enriquecimiento_masivo, args=(rubro,), daemon=True).start()

    def lanzar_enriquecimiento_global(self):
        """
        Inicia el proceso de enriquecimiento para TODAS las fichas JSON existentes.
        Usa un sistema de estado para reanudar desde donde dejó.
        """
        mensaje = (
            "⚠️ ADVERTENCIA DE PROCESO LARGO ⚠️\n\n"
            "Esto buscará datos en Google para TODOS los archivos de leads guardados.\n"
            "• Se omitirán los que ya tienen propuesta enviada.\n"
            "• Se guardará el progreso automáticamente.\n"
            "• Puedes detener el proceso cerrando la app (se reanudará la próxima vez).\n\n"
            "¿Estás seguro de iniciar?"
        )
        if not messagebox.askyesno("Confirmar Enriquecimiento Global", mensaje, icon='warning'):
            return

        threading.Thread(target=ejecutar_enriquecimiento_global, args=(self.gestor_datos, self.log), daemon=True).start()

    def ejecutar_enriquecimiento_masivo(self, rubro):
        self.btn_enrich_all.config(state="disabled")
        self.btn_rapido.config(state="disabled")
        self.btn_humano.config(state="disabled")
        
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
            # --- FASE 0: LIMPIEZA Y FUSIÓN DE DUPLICADOS ---
            self.log("♻️ Optimizando base de datos (fusionando duplicados)...")
            claves_a_eliminar = []
            nuevos_items = {}
            
            # Iteramos sobre una copia para detectar nombres sucios
            for nombre_sucio, datos in list(self.prospectos_datos.items()):
                nombre_limpio = self.limpiar_nombre(nombre_sucio)
                
                # Si el nombre estaba sucio (ej: tenía "- Vínculo visitado")
                if nombre_sucio != nombre_limpio:
                    claves_a_eliminar.append(nombre_sucio)
                    
                    # Recuperamos datos existentes del nombre limpio (si hay)
                    datos_existentes = self.prospectos_datos.get(nombre_limpio, nuevos_items.get(nombre_limpio, {}))
                    
                    # Fusionamos: Priorizamos lo que ya existía limpio, rellenamos con lo sucio
                    if datos_existentes:
                        datos_fusionados = self.fusionar_datos(datos_existentes, datos)
                    else:
                        datos_fusionados = datos
                    
                    nuevos_items[nombre_limpio] = datos_fusionados
            
            # Aplicar cambios a la base de datos principal
            for k in claves_a_eliminar:
                del self.prospectos_datos[k]
            self.prospectos_datos.update(nuevos_items)
            
            # Refrescar UI
            self.root.after(0, lambda: self.tree.delete(*self.tree.get_children()))
            for nombre in self.prospectos_datos:
                datos = self.prospectos_datos[nombre]
                prop_status = self._get_propuesta_status_text(datos)
                web_status = self._get_web_status_text(datos)
                self.root.after(0, lambda n=nombre, p=prop_status, w=web_status: self.tree.insert("", "end", iid=n, values=(n, "OPTIMIZADO ⚡", p, w)))

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
                categoria = datos.get("categoria", "")
                nuevos_datos = buscar_datos_externos(driver, nombre, categoria, self.log)
                
                if nuevos_datos:
                    actualizado = False
                    for k, v in nuevos_datos.items():
                        if v and datos.get(k) == 'No detectado':
                            datos[k] = v
                            actualizado = True
                    
                    if actualizado:
                        self.prospectos_datos[nombre] = datos
                        prop_status = self._get_propuesta_status_text(datos)
                        web_status = self._get_web_status_text(datos)
                        self.root.after(0, lambda n=nombre, p=prop_status, w=web_status: self.tree.item(n, values=(n, "ENRIQUECIDO 🌟", p, w)) if self.tree.exists(n) else None)
                
                time.sleep(random.uniform(2, 4))

            # Guardado final
            if rubro:
                self.gestor_datos.guardar_datos(f"{rubro}.json", self.prospectos_datos)

            # Actualizar cache del buscador al finalizar enriquecimiento
            self.root.after(0, self.buscador.actualizar_cache)
            
            self.log("Enriquecimiento masivo completado.")
            self.root.after(0, self.actualizar_lista_fichas)

        except Exception as e:
            self.log(f"Error en proceso masivo: {e}")
        finally:
            if driver:
                driver.quit()
            self.btn_enrich_all.config(state="normal")
            self.btn_rapido.config(state="normal")
            self.btn_humano.config(state="normal")

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
            
            datos = self.prospectos_datos.get(nombre, {})
            categoria = datos.get("categoria", "")
            nuevos_datos = buscar_datos_externos(driver, nombre, categoria, self.log)
            
            if nuevos_datos:
                actualizado = False
                for k, v in nuevos_datos.items():
                    # En búsqueda manual individual, sobrescribimos (pisamos) los datos
                    # porque el usuario indica implícitamente que los actuales no le sirven.
                    if v:
                        datos[k] = v
                        actualizado = True
                
                if actualizado:
                    self.prospectos_datos[nombre] = datos
                    if rubro:
                        self.gestor_datos.guardar_datos(f"{rubro}.json", self.prospectos_datos)
                    
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

    def ejecutar_scraping(self, rubro, estrategia="teclado"):
        """Lógica de scraping con Selenium y detección de sitios web."""
        self.log(f"Iniciando búsqueda ({estrategia}) para: {rubro}")
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
                    self.btn_rapido.config(state="normal")
                    self.btn_humano.config(state="normal")
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
                self.btn_rapido.config(state="normal")
                self.btn_humano.config(state="normal")
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
                    link_principal = None
                    try:
                        link_principal = local.find_element(By.CSS_SELECTOR, "a[href*='/maps/place/']")
                        nombre_raw = link_principal.get_attribute("aria-label")
                    except:
                        nombre_raw = local.text.split("\n")[0] # Fallback si falla el selector
                    
                    nombre = self.limpiar_nombre(nombre_raw)
                    
                    # Verificación lógica de presencia web
                    botones_web = [b for b in local.find_elements(By.TAG_NAME, "a") if "Sitio web" in str(b.get_attribute("aria-label"))]
                    
                    es_lead = True # Aceptamos todos para revisión manual
                    estado_lead = "SIN WEB 🎯"
                    social_url = ""
                    website_url = ""

                    if not botones_web:
                        pass
                    else:
                        # Si tiene botón, verificamos si es una red social (Facebook/Instagram)
                        url_destino = botones_web[0].get_attribute("href")
                        website_url = url_destino
                        if "facebook.com" in url_destino or "instagram.com" in url_destino:
                            estado_lead = "SOLO REDES 📱"
                            social_url = url_destino
                        else:
                            estado_lead = "CON WEB 🌐"

                    if es_lead:
                        self.log(f"Oportunidad hallada: {nombre}")
                        
                        # --- FEEDBACK INMEDIATO: Listar antes de procesar ---
                        # Insertamos el item en la lista visualmente (con propuesta pendiente por defecto)
                        self.root.after(0, lambda n=nombre: self.tree.insert("", "end", iid=n, values=(n, "⏳ PROCESANDO...", "❌ Pendiente", "-")) if not self.tree.exists(n) else None)
                        # ----------------------------------------------------

                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", local) # Asegurar visibilidad
                        time.sleep(1)
                        
                        # --- CLIC ROBUSTO (Mejorado) ---
                        # Intentamos clic en el enlace específico si existe, sino en la tarjeta
                        click_hecho = False
                        for _ in range(2): # 2 intentos de clic inicial
                            try:
                                if link_principal:
                                    driver.execute_script("arguments[0].click();", link_principal)
                                else:
                                    local.click()
                                click_hecho = True
                                break
                            except:
                                time.sleep(1)
                        
                        if not click_hecho:
                            self.log(f"⚠️ No se pudo hacer clic en {nombre}")
                            self.root.after(0, lambda n=nombre: self.tree.item(n, values=(n, "❌ ERROR CLIC", "❌ Pendiente", "-")) if self.tree.exists(n) else None)
                            continue

                        # --- VALIDACIÓN DE CARGA (Anti-Datos Pegados) ---
                        # Verificamos que el título del panel coincida con el negocio clicado
                        validacion_exitosa = False
                        titulo_panel = ""
                        try:
                            for intento in range(3): # 3 intentos de validación con espera
                                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='main'] h1")))
                                titulo_panel = driver.find_element(By.CSS_SELECTOR, "div[role='main'] h1").text.strip()
                                
                                # Comparación ROBUSTA (Normalizada)
                                n_lista = self.normalizar_texto(nombre)
                                n_panel = self.normalizar_texto(titulo_panel)

                                # 1. Contención directa
                                if n_lista in n_panel or n_panel in n_lista:
                                    validacion_exitosa = True
                                    break
                                
                                # 2. Coincidencia parcial de palabras (ej: "Bar X" vs "X Bar")
                                if set(n_lista.split()) & set(n_panel.split()):
                                    validacion_exitosa = True
                                    break
                                
                                # Si falla, esperamos y reintentamos clic en el segundo intento
                                time.sleep(1.5)
                                if intento == 1:
                                    self.log(f"⚠️ Reintentando clic para sincronizar {nombre}...")
                                    if link_principal:
                                        try:
                                            driver.execute_script("arguments[0].click();", link_principal)
                                        except:
                                            driver.execute_script("arguments[0].click();", local)
                                    else:
                                        driver.execute_script("arguments[0].click();", local)
                                    time.sleep(2)

                            if not validacion_exitosa:
                                # CAMBIO CRÍTICO: Si falla la validación, NO detenemos el proceso.
                                # Solo advertimos y seguimos. A veces Google cambia los títulos ligeramente.
                                self.log(f"⚠️ Advertencia Sync: Panel '{titulo_panel}' vs Lista '{nombre}'. Extrayendo igual...")
                                self.root.after(0, lambda n=nombre: self.tree.item(n, values=(n, "⚠️ SYNC?", "⏳...", "-")) if self.tree.exists(n) else None)
                                # continue  <-- ELIMINADO PARA QUE NO SE TRABE

                        except Exception:
                            pass # Si falla la validación (ej. no hay H1), seguimos con riesgo pero sin bloquear

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
                            "horarios_detallados": [],
                            "comentarios": [],
                            "imagenes": [],
                            "whatsapp": "No",
                            "email": "No detectado",
                            "facebook": social_url if "facebook.com" in social_url else "No detectado",
                            "instagram": social_url if "instagram.com" in social_url else "No detectado",
                            "enlaces_extra": []
                        }
                        
                        if website_url:
                            datos_extra["website"] = website_url

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

                        btn_horario_general = None
                        # Lista de selectores posibles para el botón de horarios (CSS y XPath)
                        selectores_horario = [
                            (By.CSS_SELECTOR, "[aria-label*='Mostrar el horario']"),
                            (By.CSS_SELECTOR, "button[aria-label*='Horario']"),
                            (By.CSS_SELECTOR, "button[aria-label*='Abierto']"),
                            (By.CSS_SELECTOR, "button[aria-label*='Cerrado']"),
                            (By.CSS_SELECTOR, "button[aria-label*='Abre']"),
                            (By.CSS_SELECTOR, "button[aria-label*='Cierra']"),
                            (By.CSS_SELECTOR, "div[role='button'][aria-label*='Horario']"),
                            (By.CSS_SELECTOR, "div[role='button'][aria-label*='Abierto']"),
                            (By.CSS_SELECTOR, "div[role='button'][aria-label*='Cerrado']"),
                            # XPath como último recurso buscando por texto visible
                            (By.XPATH, "//button[contains(@aria-label, 'lunes') or contains(@aria-label, 'martes')]") 
                        ]

                        for by_method, selector in selectores_horario:
                            try:
                                elementos = driver.find_elements(by_method, selector)
                                for el in elementos:
                                    if el.is_displayed():
                                        btn_horario_general = el
                                        break
                                if btn_horario_general: break
                            except:
                                continue

                        try:
                            if btn_horario_general:
                                raw_label = btn_horario_general.get_attribute("aria-label") or btn_horario_general.text
                                datos_extra["horario"] = raw_label.replace("Horario: ", "")
                                
                                # --- NUEVO: Extracción de Horarios Detallados (Semana Completa) ---
                                try:
                                    driver.execute_script("arguments[0].click();", btn_horario_general)
                                    time.sleep(1.5) # Esperar animación
                                    
                                    # Selector específico basado en el HTML proporcionado
                                    filas_horario = driver.find_elements(By.CSS_SELECTOR, "table.eK4R0e tr")
                                    
                                    for fila in filas_horario:
                                        try:
                                            # Extraer día (primer td)
                                            dia_element = fila.find_element(By.CSS_SELECTOR, "td.ylH6lf div")
                                            dia = dia_element.text.strip()
                                            
                                            # Extraer horario (segundo td, preferiblemente del aria-label o del li)
                                            horario_element = fila.find_element(By.CSS_SELECTOR, "td.mxowUb")
                                            horario = horario_element.get_attribute("aria-label") or horario_element.text
                                            
                                            if dia and horario:
                                                texto_final = f"{dia}: {horario}"
                                                datos_extra["horarios_detallados"].append(texto_final)
                                        except:
                                            continue
                                except: pass 
                        except: 
                            pass

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
                                if estrategia == "js":
                                    estrategia_scroll_js_focalizado(driver, panel_resenas, self.log)
                                else:
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
                                    
                                    # --- NUEVO: Captura de imágenes subidas por el usuario ---
                                    comentario['imagenes'] = []
                                    try:
                                        # Usamos el módulo modularizado para probar múltiples estrategias
                                        comentario['imagenes'] = extraer_fotos_de_resena(rev, self.log)

                                    except: pass

                                    if comentario['texto'] and comentario['texto'] != "Sin texto":
                                        datos_extra["comentarios"].append(comentario)
                                except: continue

                        except: pass 

                        # --- PUNTO DE PAUSA SOLICITADO ---
                        # Frenamos aquí para verificar visualmente antes de volver a la info general
                        # self.solicitar_confirmacion_usuario(f"Terminé de leer reseñas de: {nombre}.\n\nVoy a intentar volver a la descripción general.\nVerifica el navegador.")

                        # --- VUELTA A INFORMACIÓN Y DATOS EXTRA (REDES/IMÁGENES) ---
                        try:
                            self.log("Volviendo a pestaña Descripción general...")
                            # 1. Volver a la pestaña "Información" para buscar datos que no estaban en la vista principal.
                            # Este patrón (Info -> Reseñas -> Info) asegura que todos los datos dinámicos se carguen.
                            tab_switched = False
                            # Estrategia A: Búsqueda por XPath específicos (más robusto)
                            xpaths_tab = [
                                "//button[contains(@aria-label, 'Descripción general')]",
                                "//div[contains(text(), 'Descripción general')]",
                                "//span[contains(text(), 'Descripción general')]",
                                "//button[contains(@aria-label, 'Información')]",
                                "//div[contains(text(), 'Información')]",
                                "//span[contains(text(), 'Información')]",
                                "//button[contains(@aria-label, 'Overview')]"
                            ]
                            
                            for xpath in xpaths_tab:
                                try:
                                    elements = driver.find_elements(By.XPATH, xpath)
                                    for el in elements:
                                        if el.is_displayed():
                                            # Intentar click directo o en el padre botón
                                            driver.execute_script("arguments[0].click();", el)
                                            tab_switched = True
                                            break
                                    if tab_switched: break
                                except: pass
                            
                            # Estrategia B: Fallback JS original
                            if not tab_switched:
                                driver.execute_script("""
                                    var tabs = document.querySelectorAll('button[role="tab"], button[aria-label*="Información"], button[aria-label*="Overview"], button[aria-label*="Descripción general"]');
                                    for (var i = 0; i < tabs.length; i++) {
                                        var txt = tabs[i].textContent || tabs[i].getAttribute('aria-label');
                                        if (txt && (txt.includes('Información') || txt.includes('Overview') || txt.includes('Descripción general'))) {
                                            tabs[i].click();
                                            break;
                                        }
                                    }
                                """)
                            
                            time.sleep(2.5) # Espera vital para que cargue el contenido de la pestaña

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
                                    # Usamos la estrategia de teclado para que el scroll sea visible y active lazy load
                                    # FIX: Hacemos clic en el TÍTULO (H1) en lugar de un punto arbitrario para evitar abrir fotos
                                    try:
                                        h1_safe = main_div.find_element(By.TAG_NAME, "h1")
                                        ActionChains(driver).move_to_element(h1_safe).click().perform()
                                        time.sleep(0.5)
                                        for _ in range(6): # Aumentamos iteraciones para llegar al final (Web Results)
                                            ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
                                            time.sleep(1.0)
                                        
                                        # Scroll final forzado con JS para asegurar que llegamos al fondo absoluto
                                        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", main_div)
                                        time.sleep(1.0)
                                    except:
                                        # Fallback a JS si no se puede hacer clic en el título
                                        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", main_div)
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
                            # --- NUEVA ESTRATEGIA MODULARIZADA (Galería) ---
                            # SE COMENTA TEMPORALMENTE POR INESTABILIDAD EN EL CIERRE DE GALERÍA
                            # try:
                            #     fotos_galeria = extraer_fotos_galeria(driver, self.log)
                            #     if fotos_galeria:
                            #         # Agregamos las fotos de mejor calidad encontradas
                            #         for f in fotos_galeria:
                            #             if f not in datos_extra["imagenes"]:
                            #                 datos_extra["imagenes"].append(f)
                            # except Exception as e:
                            #     self.log(f"Error invocando módulo fotos: {e}")
                            
                            # 6. Recolectar "Resultados web" (Enlaces extra al final del panel)
                            # Capturamos hasta 3 enlaces externos que no sean de Google ni redes ya detectadas.
                            try:
                                root_element = main_div if main_div else driver.find_element(By.CSS_SELECTOR, "div[role='main']")
                                links_raw = root_element.find_elements(By.TAG_NAME, "a")
                                for link in links_raw:
                                    try:
                                        url = link.get_attribute("href")
                                        if not url or "javascript" in url or "mailto" in url or "tel" in url: continue
                                        
                                        # Filtros de ruido (Google Maps internals)
                                        if "google.com" in url or "goo.gl" in url: continue
                                        
                                        # Filtros de redes ya capturadas
                                        if "facebook.com" in url or "instagram.com" in url: continue
                                        
                                        # Evitar duplicados y limitar a 3
                                        if url not in datos_extra["enlaces_extra"] and len(datos_extra["enlaces_extra"]) < 3:
                                            datos_extra["enlaces_extra"].append(url)
                                    except: continue
                            except: pass

                            # --- PUNTO DE PAUSA SOLICITADO 2 ---
                            # self.solicitar_confirmacion_usuario(f"Finalicé la revisión extra de: {nombre}.\n\nVoy a pasar al siguiente emprendimiento.")

                        except Exception: pass

                        # --- LÓGICA DE FUSIÓN INTELIGENTE (MERGE) ---
                        # Si ya teníamos datos de este negocio de una búsqueda anterior, no sobrescribimos
                        # información valiosa (ej. un email encontrado manualmente) con un resultado vacío ("No detectado").
                        datos_previos = self.prospectos_datos.get(nombre, {})
                        
                        # Usamos la nueva función de fusión
                        # Prioridad: datos_extra (lo nuevo que acabamos de scrapear)
                        # Respaldo: datos_previos (lo que ya teníamos)
                        # Si datos_extra trae "No detectado" y datos_previos tenía email, se queda el email.
                        datos_fusionados = self.fusionar_datos(datos_extra, datos_previos)

                        # Guardar (ahora sí, datos combinados)
                        self.prospectos_datos[nombre] = datos_fusionados
                        
                        # --- GUARDADO INCREMENTAL (PERSISTENCIA) ---
                        # Guardamos en cada iteración para evitar pérdida de datos si se cierra el navegador
                        self.gestor_datos.guardar_datos(f"{rubro}.json", self.prospectos_datos)
                        
                        # Actualizar UI de forma inteligente (sin duplicar filas)
                        def actualizar_ui(n):
                            prop_status = self._get_propuesta_status_text(datos_fusionados)
                            web_status = self._get_web_status_text(datos_fusionados)
                            if self.tree.exists(n):
                                self.tree.item(n, values=(n, "ACTUALIZADO ✨" if estado_lead == "SIN WEB 🎯" else estado_lead, prop_status, web_status))
                            else:
                                self.tree.insert("", "end", iid=n, values=(n, estado_lead, prop_status, web_status))
                        
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
                self.gestor_datos.guardar_datos(f"{rubro}.json", self.prospectos_datos)
                self.log(f"Datos guardados en {rubro}.json")
                self.root.after(0, self.actualizar_lista_fichas) # Actualizar lista desplegable
            else:
                self.log("⚠️ Finalizado sin nuevos datos guardados.")
            
            # Actualizar cache del buscador al finalizar scraping
            self.root.after(0, self.buscador.actualizar_cache)

            driver.quit()
            self.log("Proceso completado con éxito.")
            self.btn_rapido.config(state="normal")
            self.btn_humano.config(state="normal")
            
        except Exception as e:
            self.log(f"Error: {e}")
            self.btn_rapido.config(state="normal")
            self.btn_humano.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = TrelewLeadApp(root)
    root.mainloop()