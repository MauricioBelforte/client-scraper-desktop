# test_ia.py
import json
from controlador_ia import generar_contenido_ia

# 1. Definir un JSON de prueba (simulando datos del scraper)
# Caso de prueba: Una peluquería con reseñas positivas sobre cortes y color.
datos_prueba_peluqueria = {
    "nombre": "Estilo Divino",
    "categoria": "Peluquería",
    "direccion": "Avenida Siempreviva 742, Trelew, Chubut",
    "rating": "4.9 de 5 estrellas",
    "comentarios": [
        {"autor": "Ana S.", "texto": "¡Me encantó el corte! Muy modernos y profesionales.", "rating": "5 estrellas"},
        {"autor": "Laura G.", "texto": "El color quedó increíble, justo lo que quería. Volveré sin dudas.", "rating": "5 estrellas"},
        {"autor": "Carla M.", "texto": "Excelente atención y el lugar es muy lindo.", "rating": "4 estrellas"}
    ]
}

print("--- Iniciando Prueba Unitaria del Módulo de IA ---")
print(f"Negocio de prueba: {datos_prueba_peluqueria['nombre']} ({datos_prueba_peluqueria['categoria']})")

# 2. Ejecutar SOLO el módulo de IA
contenido_generado = generar_contenido_ia(datos_prueba_peluqueria['nombre'], datos_prueba_peluqueria)

# 3. Imprimir y evaluar el resultado
if contenido_generado:
    print("\n--- Contenido Generado por la IA ---")
    print(json.dumps(contenido_generado, indent=2, ensure_ascii=False))
    print("\n--- Evaluación ---")
    print("1. ¿Los textos son coherentes para una 'Peluquería'?")
    print("2. ¿Los 'beneficios' reflejan las fortalezas de las reseñas (cortes, color, atención)?")

    # Gracias a la lógica de ahorro de tokens, para una categoría conocida
    # como "Peluquería", la IA no debería sugerir colores.
    if "sugerencia_colores" in contenido_generado:
        print("3. [AVISO] La IA sugirió colores, pero no debería haberlo hecho para una categoría predefinida.")
    else:
        print("3. [OK] La IA no sugirió colores, respetando las paletas predefinidas (ahorro de tokens).")
else:
    print("\n--- FALLO LA PRUEBA ---")
    print("La IA no devolvió contenido. Revisa los logs de 'controlador_ia.py'.")

