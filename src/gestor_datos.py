import json
import os

class GestorDatos:
    def __init__(self, carpeta_datos):
        self.carpeta_datos = carpeta_datos
        if not os.path.exists(self.carpeta_datos):
            os.makedirs(self.carpeta_datos)

    def obtener_archivos(self):
        """Devuelve una lista con los nombres de los archivos JSON disponibles (sin extensión)."""
        if not os.path.exists(self.carpeta_datos):
            return []
        return [f.replace(".json", "") for f in os.listdir(self.carpeta_datos) if f.endswith(".json")]

    def cargar_datos(self, nombre_archivo):
        """Carga el contenido de un archivo JSON dado su nombre (con o sin extensión)."""
        if not nombre_archivo.endswith(".json"):
            nombre_archivo += ".json"
            
        ruta_archivo = os.path.join(self.carpeta_datos, nombre_archivo)
        if not os.path.exists(ruta_archivo):
            return {}
        
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def guardar_datos(self, nombre_archivo, datos):
        """Guarda un diccionario en un archivo JSON (con o sin extensión)."""
        if not nombre_archivo:
            return False
            
        if not nombre_archivo.endswith(".json"):
            nombre_archivo += ".json"
            
        ruta_archivo = os.path.join(self.carpeta_datos, nombre_archivo)
        try:
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(datos, f, ensure_ascii=False, indent=4)
            return True
        except Exception:
            return False