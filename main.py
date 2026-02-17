import os
import json
import time
from controlador_ia import generar_contenido_ia, limpiar_datos_ia
from generador_web import generar_web_profesional

CARPETA_LEADS = "fichas_leads"

def cargar_leads():
    """Carga los archivos JSON disponibles en la carpeta de leads."""
    if not os.path.exists(CARPETA_LEADS):
        print(f"⚠️ La carpeta '{CARPETA_LEADS}' no existe. Asegúrate de haber ejecutado el scraper primero.")
        return []
    
    archivos = [f for f in os.listdir(CARPETA_LEADS) if f.endswith('.json')]
    return archivos

def main():
    print("\n>> ORQUESTADOR DE SITIOS WEB AUTOMATICOS <<")
    print("========================================")
    
    archivos = cargar_leads()
    
    if not archivos:
        print(">> No se encontraron fichas de leads para procesar.")
        print(">> Consejo: Ejecuta primero el scraper para recolectar datos.")
        # Opción de prueba manual si no hay archivos
        print("\n--- MODO PRUEBA ---")
        datos_seleccionados = {
            "nombre": "Veterinaria Patitas Felices",
            "categoria": "Veterinaria",
            "direccion": "Av. Siempre Viva 123",
            "telefono": "+54 9 11 1234 5678",
            "rating": "4.8",
            "comentarios": [
                {"autor": "Ana Gomez", "texto": "Excelente atención, salvaron a mi perro.", "rating": "5 estrellas"},
                {"autor": "Carlos Perez", "texto": "Muy amables y profesionales.", "rating": "5 estrellas"}
            ]
        }
        nombre_archivo = "prueba_manual.json"
    else:
        print(f">> Se encontraron {len(archivos)} candidatos:")
        for i, archivo in enumerate(archivos):
            print(f"[{i + 1}] {archivo}")
            
        try:
            seleccion = int(input("\n>> Selecciona el número del negocio para generar su web: ")) - 1
            if 0 <= seleccion < len(archivos):
                nombre_archivo = archivos[seleccion]
                ruta_completa = os.path.join(CARPETA_LEADS, nombre_archivo)
                with open(ruta_completa, 'r', encoding='utf-8') as f:
                    datos_seleccionados = json.load(f)
            else:
                print(">> Selección inválida.")
                return
        except ValueError:
            print(">> Debes ingresar un número.")
            return

    print(f"\n>> Procesando: {datos_seleccionados.get('nombre', 'Negocio')}")
    
    # 1. Limpieza de Datos
    print("\n>> Paso 1: Limpiando y normalizando datos con IA...")
    datos_limpios = limpiar_datos_ia(datos_seleccionados)
    nombre_negocio = datos_limpios.get('nombre', datos_seleccionados.get('nombre', 'Negocio Sin Nombre'))
    
    # 2. Generación de Contenido
    print("\n>> Paso 2: Creando contenido creativo (Copywriting)...")
    textos_creativos = generar_contenido_ia(nombre_negocio, datos_limpios)
    
    # 3. Generación de Web
    print("\n>> Paso 3: Maquetando y generando código HTML...")
    resultado = generar_web_profesional(nombre_negocio, datos_limpios, textos_creativos)
    
    print(f"\n>> {resultado}")
    print(">> Proceso finalizado con éxito.")

if __name__ == "__main__":
    main()