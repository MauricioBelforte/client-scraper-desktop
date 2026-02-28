"""
TEST 1: Prueba del nuevo sistema de mensajes por archivo JSON
Verifica que generar_mensaje_whatsapp() usa el nombre del archivo correctamente
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.mensajes import generar_mensaje_whatsapp, TEMPLATES_POR_ARCHIVO
import urllib.parse

def test_cerveceria():
    """Prueba que cervecería recibe sus 5 modelos personalizados"""
    msg = generar_mensaje_whatsapp("BARDO - Cerveza Artesanal", "Cervecerías")
    decoded = urllib.parse.unquote(msg)
    
    # Verificar que contiene los 5 modelos de cervecería
    assert "cerveceria-el-galpon-patagonico.netlify.app" in decoded, "Falta modelo 1"
    assert "cerveceria-rio-chubut.netlify.app" in decoded, "Falta modelo 2"
    assert "patagonia-habitat-inmobiliaria.netlify.app" in decoded, "Falta modelo 3"
    assert "centro-psicologico-conexion-interior.netlify.app" in decoded, "Falta modelo 4"
    assert "tinta-austral.netlify.app" in decoded, "Falta modelo 5"
    
    # Verificar intro correcto
    assert "cervecerías y bares de la zona" in decoded, "Intro incorrecta"
    print("[OK] Cervecería: OK")

def test_abogados():
    """Prueba que abogados reciben su template correcto"""
    msg = generar_mensaje_whatsapp("Estudio P&M", "Abogados")
    decoded = urllib.parse.unquote(msg)
    
    # Verificar  que NO contiene los modelos de cervecería
    assert "cerveceria-el-galpon-patagonico" not in decoded, "Tiene modelos de cervecería"
    
    # Verificar intro correcto
    assert "estudios jurídicos" in decoded, "Intro incorrecta para abogados"
    print("[OK] Abogados: OK")

def test_restaurante():
    """Prueba que restaurante recibe su template correcto"""
    msg = generar_mensaje_whatsapp("El Buen Comer", "Restaurantes")
    decoded = urllib.parse.unquote(msg)
    
    # Verificar intro correcto
    assert "locales gastronomicos" in decoded, "Intro incorrecta para restaurante"
    print("[OK] Restaurante: OK")

def test_inmobiliaria():
    """Prueba que inmobiliaria recibe 4 modelos de inmobiliaria"""
    msg = generar_mensaje_whatsapp("Valle Azul Propiedades", "Inmobiliarias")
    decoded = urllib.parse.unquote(msg)
    
    # Verificar que contiene los 4 modelos de inmobiliaria
    assert "valle-azul-propiedades.netlify.app" in decoded, "Falta modelo inmobiliario"
    assert "patagonia-urbana-inmobiliaria.netlify.app" in decoded, "Falta modelo inmobiliario 2"
    assert "Modelo 4:" in decoded, "No tiene 4 modelos"
    print("[OK] Inmobiliaria: OK")

def test_template_default():
    """Prueba que archivo desconocido usa template por defecto"""
    msg = generar_mensaje_whatsapp("Negocio Desconocido", "ArchivoQueNoExiste")
    decoded = urllib.parse.unquote(msg)
    
    # Verificar intro por defecto
    assert "distintos negocios y profesionales locales" in decoded, "No usa template default"
    print("[OK] Template Default: OK")

def test_todos_archivos_configurados():
    """Prueba que todos los archivos conocidos están configurados"""
    archivos_json = [
        "Abogados", "Barbería", "Bares", "Cafeterías", "Carnicerías",
        "Centros de Estética", "Cervecerías", "Gimnasios", "Inmobiliarias",
        "Kinesiólogos", "Kioscos", "Mueblerías", "Nutricionistas", "Odontólogos",
        "Panaderías", "Peluquerías", "Pet Shops", "Pizzerías", "Psicólogos",
        "Restaurantes", "Servicios de Catering", "Talleres Mecánicos", "Tatuajes",
        "Verdulerías", "Veterinarias"
    ]
    
    for archivo in archivos_json:
        assert archivo in TEMPLATES_POR_ARCHIVO, f"Archivo '{archivo}' no está configurado"
    
    print(f"[OK] Todos los {len(archivos_json)} archivos están configurados")

def test_mensaje_estructura():
    """Prueba que el mensaje tiene la estructura correcta"""
    msg = generar_mensaje_whatsapp("Test Negocio", "Cervecerías")
    decoded = urllib.parse.unquote(msg)
    
    # Verificar estructura
    assert "Hola, Test Negocio" in decoded, "Falta saludo"
    assert "Mi nombre es Mauricio Belforte" in decoded, "Falta presentación"
    assert "Soy de Trelew" in decoded, "Falta ubicación"
    assert "Estoy ofreciendo mis servicios" in decoded, "Falta intro"
    assert "Si gustan pueden pasar a ver estos ejemplos" in decoded, "Falta call to action"
    assert "https://mauriciobelforte.github.io/mi-portfolio/" in decoded, "Falta portfolio"
    assert "Si les sirve, no duden en contactarme" in decoded, "Falta cierre"
    
    print("[OK] Estructura del mensaje: OK")

if __name__ == "__main__":
    print("="*70)
    print("TEST 1: PRUEBAS DEL NUEVO SISTEMA DE MENSAJES POR ARCHIVO JSON")
    print("="*70)
    print()
    
    try:
        test_cerveceria()
        test_abogados()
        test_restaurante()
        test_inmobiliaria()
        test_template_default()
        test_todos_archivos_configurados()
        test_mensaje_estructura()
        
        print()
        print("="*70)
        print("[OK] TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("="*70)
    except AssertionError as e:
        print(f"\n[NO] TEST FALLIDO: {e}")
        sys.exit(1)
