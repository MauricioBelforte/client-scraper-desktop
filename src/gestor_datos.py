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
        """Carga el contenido de un archivo JSON dado su nombre (sin extensión)."""
        ruta_archivo = os.path.join(self.carpeta_datos, f"{nombre_archivo}.json")
        if not os.path.exists(ruta_archivo):
            return {}
        
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            return json.load(f)

    # Aquí agregaremos guardar_datos en el siguiente paso