"""
Test de Integración - Prueba del sistema con archivos JSON reales

Este test carga archivos JSON reales de fichas_leads/ y verifica que:
1. Se cargan correctamente
2. Se genera mensaje personalizado para cada rubro
3. Los modelos específicos de cada rubro están presentes
"""

import json
import os
import sys
from pathlib import Path

# Agregar raíz del proyecto al path
sys.path.insert(0, '.')

from src.mensajes import generar_mensaje_whatsapp, TEMPLATES_POR_ARCHIVO

def test_integracion_json_reales():
    """Prueba con JSONs reales de fichas_leads/"""
    
    ruta_fichas = Path("fichas_leads")
    archivos_json = sorted(ruta_fichas.glob("*.json"))
    
    print(f"\n{'='*70}")
    print(f"TEST DE INTEGRACIÓN - Archivos JSON Reales")
    print(f"{'='*70}")
    print(f"Encontrados: {len(archivos_json)} archivos JSON\n")
    
    resultados = []
    mensajes_correctos = 0
    
    for archivo_path in archivos_json:
        nombre_archivo = archivo_path.stem  # Sin extensión
        
        # Cargar JSON
        try:
            with open(archivo_path, 'r', encoding='utf-8') as f:
                datos = json.load(f)
        except Exception as e:
            print(f"[NO] {nombre_archivo}: Error al cargar JSON - {e}")
            continue
        
        # La estructura es {nombre_negocio: {datos}, ...}
        if not datos:
            print(f"[WN] {nombre_archivo}: JSON vacío")
            continue
        
        # Obtener primer negocio del archivo
        nombre_negocio = next(iter(datos.keys()), None)
        if not nombre_negocio:
            print(f"[WN] {nombre_archivo}: No contiene negocios")
            continue
        
        # Generar mensaje con nombre de archivo (nuevo sistema)
        try:
            mensaje = generar_mensaje_whatsapp(nombre_negocio, nombre_archivo)
            
            # Validar mensaje
            if mensaje and len(mensaje) > 50:
                # Verificar si tiene entrada específica en templates
                tiene_template = nombre_archivo in TEMPLATES_POR_ARCHIVO
                
                # Decodificar mensaje para inspección
                import urllib.parse
                mensaje_decodificado = urllib.parse.unquote(mensaje)
                
                # Validar estructura
                tiene_nombre = nombre_negocio in mensaje_decodificado
                tiene_url = "netlify.app" in mensaje_decodificado
                tiene_intro = len(mensaje_decodificado) > 100
                
                estado = "[OK]" if (tiene_url and tiene_intro) else "[!!]"
                template_str = "ESPECIFICO" if tiene_template else "DEFAULT"
                
                print(f"{estado} {nombre_archivo:30} | Template: {template_str:9} | "
                      f"Negocio: {nombre_negocio[:25]:25} | URLs: {tiene_url}")
                
                if tiene_url and tiene_intro:
                    mensajes_correctos += 1
                    resultados.append({
                        'archivo': nombre_archivo,
                        'template': template_str,
                        'negocio': nombre_negocio,
                        'mensaje_length': len(mensaje_decodificado)
                    })
            else:
                print(f"[NO] {nombre_archivo:30} | Mensaje vacío o inválido")
                
        except Exception as e:
            print(f"[NO] {nombre_archivo:30} | Error: {e}")
    
    print(f"\n{'='*70}")
    print(f"RESULTADOS: {mensajes_correctos}/{len(archivos_json)} archivos procesados correctamente")
    print(f"{'='*70}\n")
    
    # Validaciones adicionales
    assert mensajes_correctos > 0, "Ningún archivo JSON fue procesado correctamente"
    assert mensajes_correctos >= len(archivos_json) * 0.8, "Menos del 80% de archivos son válidos"
    
    print("[OK] TEST DE INTEGRACIÓN COMPLETADO EXITOSAMENTE")
    return resultados

def test_modelos_especificos_por_rubro():
    """Verifica que modelos específicos están en los mensajes"""
    
    rubros_validar = {
        "Cervecerías": [
            "cerveceria-el-galpon-patagonico",
            "cerveceria-rio-chubut"
        ],
        "Psicólogos": [
            "espacio-psicologico-conexion",
            "centro-psicologico-conexion-interior"
        ],
        "Tatuajes": [
            "tinta-austral",
            "tinta-patagonica-tattoo-studio"
        ],
        "Inmobiliarias": [
            "valle-azul-propiedades",
            "patagonia-urbana-inmobiliaria"
        ]
    }
    
    print(f"\n{'='*70}")
    print(f"TEST - Validación de Modelos Específicos por Rubro")
    print(f"{'='*70}\n")
    
    for rubro, modelos_esperados in rubros_validar.items():
        mensaje = generar_mensaje_whatsapp("Test", rubro)
        import urllib.parse
        mensaje_decoded = urllib.parse.unquote(mensaje)
        
        modelos_encontrados = sum(1 for modelo in modelos_esperados 
                                   if modelo in mensaje_decoded)
        
        total_modelos = len(modelos_esperados)
        porcentaje = (modelos_encontrados / total_modelos) * 100
        
        estado = "[OK]" if modelos_encontrados == total_modelos else "[WN]"
        print(f"{estado} {rubro:20} | {modelos_encontrados}/{total_modelos} modelos encontrados "
              f"({porcentaje:.0f}%)")
        
        assert modelos_encontrados > 0, f"{rubro} no tiene modelos en mensaje"
    
    print(f"\n[OK] VALIDACIÓN DE MODELOS COMPLETADA")
    return True

def test_consistencia_mensajes():
    """Verifica que todos los mensajes tienen la estructura correcta"""
    
    print(f"\n{'='*70}")
    print(f"TEST - Consistencia de Estructura de Mensajes")
    print(f"{'='*70}\n")
    
    rubros_muestra = list(TEMPLATES_POR_ARCHIVO.keys())[:5]
    
    for rubro in rubros_muestra:
        mensaje = generar_mensaje_whatsapp("Negocio Test", rubro)
        import urllib.parse
        mensaje_decoded = urllib.parse.unquote(mensaje)
        
        # Validar componentes
        tiene_saludo = "Hola," in mensaje_decoded
        tiene_nombre = "Mauricio Belforte" in mensaje_decoded
        tiene_intro = TEMPLATES_POR_ARCHIVO[rubro]["intro"] in mensaje_decoded
        tiene_modelos = "Modelo 1:" in mensaje_decoded
        tiene_portfolio = "mauriciobelforte.github.io/mi-portfolio/" in mensaje_decoded
        
        todos_componentes = [tiene_saludo, tiene_nombre, tiene_intro, tiene_modelos, tiene_portfolio]
        
        if all(todos_componentes):
            print(f"[OK] {rubro:25} | Estructura completa")
        else:
            print(f"[WN] {rubro:25} | Faltan: ", end="")
            if not tiene_saludo: print("saludo ", end="")
            if not tiene_nombre: print("nombre ", end="")
            if not tiene_intro: print("intro ", end="")
            if not tiene_modelos: print("modelos ", end="")
            if not tiene_portfolio: print("portfolio ", end="")
            print()
        
        assert all(todos_componentes), f"{rubro} no tiene estructura completa"
    
    print(f"\n[OK] CONSISTENCIA VERIFICADA")
    return True

def test_archivo_no_configurado():
    """Verifica que archivos no configurados usan TEMPLATE_DEFAULT"""
    
    print(f"\n{'='*70}")
    print(f"TEST - Fallback para Archivos No Configurados")
    print(f"{'='*70}\n")
    
    # Prueba con archivo inexistente
    mensaje = generar_mensaje_whatsapp("Test", "ArchivoInexistente")
    import urllib.parse
    mensaje_decoded = urllib.parse.unquote(mensaje)
    
    # Debe tener los modelos del DEFAULT
    default_urls = ["espacio-psicologico-conexion", "centro-psicologico-conexion-interior"]
    urls_encontradas = sum(1 for url in default_urls if url in mensaje_decoded)
    
    print(f"Archivo 'ArchivoInexistente' -> usa TEMPLATE_DEFAULT")
    print(f"URLs encontradas: {urls_encontradas}/{len(default_urls)}")
    
    if urls_encontradas > 0:
        print(f"[OK] Fallback funciona correctamente")
    else:
        print(f"[WN] No se encontraron URLs del default")
    
    assert urls_encontradas > 0, "Fallback no funciona"
    return True

if __name__ == "__main__":
    print("\n" + "="*70)
    print("SUITE DE TESTS DE INTEGRACIÓN")
    print("="*70)
    
    try:
        # Test 1
        test_integracion_json_reales()
        
        # Test 2
        test_modelos_especificos_por_rubro()
        
        # Test 3
        test_consistencia_mensajes()
        
        # Test 4
        test_archivo_no_configurado()
        
        print("\n" + "="*70)
        print("[OK] TODOS LOS TESTS DE INTEGRACIÓN PASARON EXITOSAMENTE")
        print("="*70 + "\n")
        
    except AssertionError as e:
        print(f"\n[NO] TEST FALLIDO: {e}\n")
        exit(1)
    except Exception as e:
        print(f"\n[NO] ERROR DURANTE TESTING: {e}\n")
        exit(1)
