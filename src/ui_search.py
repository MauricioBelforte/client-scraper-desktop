import tkinter as tk
from tkinter import ttk

class BuscadorVisual:
    def __init__(self, parent, tree):
        self.tree = tree
        self.entry_var = tk.StringVar()
        self.all_items = [] # Cache de (iid, values) para restaurar
        self.is_filtered = False
        
        self._setup_ui(parent)

    def _setup_ui(self, parent):
        # Frame contenedor
        frame = tk.Frame(parent, bg="white", pady=5)
        frame.pack(fill="x", padx=0, pady=(0, 5))
        
        # Icono / Etiqueta
        tk.Label(frame, text="🔍 Filtrar:", bg="white", font=("Segoe UI", 9, "bold"), fg="#6c757d").pack(side="left", padx=(5, 5))
        
        # Campo de entrada
        entry = ttk.Entry(frame, textvariable=self.entry_var)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # Evento al soltar tecla
        entry.bind("<KeyRelease>", self.on_filter)

    def actualizar_cache(self):
        """
        Captura el estado actual del Treeview (todos los items visibles).
        Debe llamarse después de cargar datos masivos o finalizar un scraping.
        """
        # Si hay texto escrito, lo limpiamos para asegurar que capturamos todo
        if self.entry_var.get():
            self.entry_var.set("")
            self.is_filtered = False
            # Restaurar visibilidad de todo antes de capturar
            # (Aunque si get_children devuelve todo lo visible, está bien)
        
        self.all_items = []
        for iid in self.tree.get_children():
            # Guardamos el ID y los valores (para buscar en el nombre)
            self.all_items.append((iid, self.tree.item(iid, "values")))

    def on_filter(self, event):
        query = self.entry_var.get().lower()
        
        # Si el cache está vacío (primera vez), lo llenamos
        if not self.all_items:
            self.actualizar_cache()
            
        # Si borraron todo el texto, restaurar todo
        if not query:
            self.restaurar_todo()
            self.is_filtered = False
            return

        self.is_filtered = True
        
        # 1. Ocultar todos los items actuales (detach)
        # get_children() devuelve los que están visibles ahora
        self.tree.detach(*self.tree.get_children())
        
        # 2. Re-insertar (move) solo los que coinciden
        for iid, values in self.all_items:
            # values[0] es el nombre del negocio
            nombre = str(values[0]).lower()
            if query in nombre:
                # 'move' reubica el item si ya existe (o lo re-atacha si estaba detached)
                self.tree.move(iid, "", "end")

    def restaurar_todo(self):
        """Vuelve a mostrar todos los items del cache."""
        self.tree.detach(*self.tree.get_children())
        for iid, values in self.all_items:
            self.tree.move(iid, "", "end")