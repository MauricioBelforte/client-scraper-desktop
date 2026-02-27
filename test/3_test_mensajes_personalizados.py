#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar la personalización de mensajes de WhatsApp
para diferentes rubros de negocios.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.mensajes import generar_mensaje_whatsapp, TEMPLATES_POR_ARCHIVO

# Rubros disponibles (nombres de archivos)
RUBROS_PRUEBA = list(TEMPLATES_POR_ARCHIVO.keys())[:10]  # Tomar los primeros 10

def main():
    print("=" * 80)
    print("PRUEBA DE PERSONALIZACIÓN DE MENSAJES DE WHATSAPP")
    print("=" * 80)
    
    for rubro in RUBROS_PRUEBA:
        print(f"\nRubro: {rubro}")
        print("-" * 80)
        
        # Generar mensaje (no decodificar para ver el contenido)
        try:
            mensaje_codificado = generar_mensaje_whatsapp("Negocio Test", rubro)
            
            # Decodificar para ver el contenido (esto es opcional)
            import urllib.parse
            mensaje_decodificado = urllib.parse.unquote(mensaje_codificado)
            
            # Mostrar solo la primera línea del intro personalizado
            lineas = mensaje_decodificado.split('\n')
            intro_line = None
            for linea in lineas:
                if "Estoy ofreciendo mis servicios" in linea:
                    intro_line = linea.strip()
                    break
            
            if intro_line:
                print(f"[OK] Intro: {intro_line[:70]}...")
            else:
                print(f"[OK] Mensaje generado correctamente")
                
        except Exception as e:
            print(f"[ERROR] {e}")
    
    print("\n" + "=" * 80)
    print("Prueba completada")
    print("=" * 80)

if __name__ == "__main__":
    main()
