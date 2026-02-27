import os
import sys
import json

# Agregar el directorio padre al path para poder importar src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from src.estrategia_fotos_reviews import analizar_contenido_eden_ai

# Cargar variables de entorno (asegúrate de tener EDENAI_API_KEY en tu .env)
load_dotenv()

# Datos de prueba del negocio
datos_negocio = {
    "CERVEZA BIRRAT": {
        "telefono": "Sin teléfono",
        "direccion": "Sarmiento 281, U9100 Trelew, Chubut ",
        "categoria": "Cervecería artesanal",
        "rating": "4.6 estrellas 231 opiniones",
        "comentarios": [
            {
                "autor": "Imanol Rojas",
                "texto": "Excelente la birra y la buena onda",
                "rating": "5 estrellas",
                "imagenes": [
                    "https://lh3.googleusercontent.com/geougc-cs/ABOP9psDxYd4974OipTwUDcwuqcai265AeMGteL4EZpUdWbuPAaBIzTgTRWPMzCol_sA2hQl-qwSLD3o-vDBO78xtPwpJHizOGfDk_B0srMceyVtztb0eR5pBX35yu1KHKO9vcFNBkfHre_HkZWv=s0"
                ]
            },
            {
                "autor": "Mauricio Robalo Bianco",
                "texto": "Muy buena birra, es más un centro de re llenado",
                "rating": "4 estrellas",
                "imagenes": [
                    "https://lh3.googleusercontent.com/geougc-cs/ABOP9psxIEoIxrtZeDl9LMH8c4hfdasShOsicyskz8ktCeKqLExN9llgsd5Tb_0_vbTnrxhumcn_22aZPejuPguziDvpnjcN2KKpUJRIK8q0k22A85D60THbnXDCV35VqPjTPFRuTYnS=s0",
                    "https://lh3.googleusercontent.com/geougc-cs/ABOP9pt2clne_Bl9AecUgCGj7tL_XS7-9w8nzk8TV2raeupAeXksT3Ha7L5J1Oe_DxBTn2AWgTKxCYiozoNlTzHZ6QDLUd339gArIU8LyU4YqW6S2hxnb6pFz1V3yHtPHZKmv7DHUaU=s0",
                ]
            },
            {
                "autor": "Leandro Turchin",
                "texto": "Tienen la cerveza 🍻 super rica y el mejor arte!!…",
                "rating": "5 estrellas",
                "imagenes": [
                    "https://lh3.googleusercontent.com/geougc-cs/ABOP9ptuf68svqS37XoQILwDPf0FMVDBKWjxT5qhnPSLVA3U2-u2zfQ5vMPWdRERUytgjNM2TeK2_3Td6vKou_dOLe5OUSEPPG-rgjD_s8Ekr7UXWYm2p1yozarYf9Sb7z7v7-d7PsBlhg=s0",
                ]
            }
        ]
    }
}

def test_vision_analysis():
    """
    Ejecuta un test de la función de análisis de imágenes sobre los datos de prueba.
    """
    nombre_negocio = "CERVEZA BIRRAT"
    datos = datos_negocio[nombre_negocio]
    
    # Contexto para el análisis: nombre, categoría y palabras clave relevantes
    # Eden AI funciona mejor con etiquetas en minúsculas y simples
    contexto_analisis = [
        "beer", "glass", "bottle", "cup", "cerveza", "vaso", "botella", "copa"
    ]
    
    print(f"--- INICIANDO TEST DE VISIÓN (Eden AI) PARA: {nombre_negocio} ---")
    
    if not os.getenv("EDENAI_API_KEY"):
        print("\n[ERROR] No se encontró la variable de entorno EDENAI_API_KEY en tu archivo .env")
        print("Asegúrate de que el archivo .env existe en la raíz del proyecto y contiene: EDENAI_API_KEY=tu_clave_aqui")
        return

    total_imagenes = sum(len(c.get("imagenes", [])) for c in datos.get("comentarios", []))
    print(f"Se analizarán {total_imagenes} imágenes de los comentarios.\n")

    for comentario in datos.get("comentarios", []):
        autor = comentario.get("autor") or "Anónimo"
        print(f"\n--- Comentario de: {autor} ---")
        
        for url_foto in comentario.get("imagenes", []):
            print(f"  > Analizando URL: {url_foto[:80]}...")
            analisis = analizar_contenido_eden_ai(url_foto, context_labels=contexto_analisis)
            
            if analisis:
                if analisis.get("es_persona"):
                    print(f"    [OK] RESULTADO: PERSONA DETECTADA (Género: {analisis.get('genero', 'N/A')}, Confianza: {analisis.get('confianza', 0):.2f})")
                elif analisis.get("es_relacionado"):
                    print(f"    [OBJETO] RESULTADO: OBJETO RELACIONADO (Etiqueta: '{analisis.get('etiqueta')}', Confianza: {analisis.get('confianza', 0):.2f})")
                else:
                    print(f"    [INFO] RESULTADO: NO RELEVANTE (Etiqueta: '{analisis.get('etiqueta')}', Confianza: {analisis.get('confianza', 0):.2f})")
            else:
                print("    [ERROR] La API de Eden AI no devolvió un análisis válido.")

    print("\n--- TEST DE VISIÓN (Eden AI) FINALIZADO ---")

if __name__ == "__main__":
    test_vision_analysis()