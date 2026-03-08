#!/usr/bin/env python3
"""
Script para limpiar y sincronizar leads duplicados entre fichas.
Ejecutar una sola vez para actualizar datos existentes.
"""

import os
import json
from src.sincronizador_leads import SincronizadorLeads

def sincronizar_todos_los_leads():
    """Sincroniza todos los leads que aparecen en múltiples fichas usando el más completo como fuente."""
    sincronizador = SincronizadorLeads("fichas_leads")

    # Obtener todos los archivos
    archivos = sincronizador.gestor.obtener_archivos()

    print(f"Procesando {len(archivos)} fichas...")

    # Recopilar todos los leads únicos
    leads_procesados = set()
    actualizaciones = 0

    for archivo in archivos:
        print(f"Procesando {archivo}...")
        datos = sincronizador.gestor.cargar_datos(archivo)

        for nombre_lead, datos_lead in datos.items():
            if nombre_lead in leads_procesados:
                continue

            leads_procesados.add(nombre_lead)

            # Verificar si aparece en múltiples fichas
            resultados = sincronizador.buscar_lead_por_nombre(nombre_lead)
            if len(resultados) > 1:
                # Obtener el lead más completo
                datos_completos = sincronizador.obtener_datos_completos_lead(nombre_lead)
                
                if datos_completos:
                    # Actualizar todas las fichas con los datos del más completo
                    archivos_actualizados = sincronizador.actualizar_lead_en_todas_fichas(
                        nombre_lead, datos_completos
                    )
                    
                    if archivos_actualizados:
                        actualizaciones += len(archivos_actualizados)
                        print(f"  ✅ Sincronizado '{nombre_lead}' desde el lead más completo a {len(archivos_actualizados)} fichas")

    print(f"\nProceso completado. Se realizaron {actualizaciones} actualizaciones.")

if __name__ == "__main__":
    sincronizar_todos_los_leads()