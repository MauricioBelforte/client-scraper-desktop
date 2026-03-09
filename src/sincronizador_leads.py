import os
import json
from src.gestor_datos import GestorDatos

class SincronizadorLeads:
    """
    Clase para sincronizar leads entre diferentes fichas de rubros.
    Permite buscar leads duplicados y actualizar información en todas las fichas.
    """

    def __init__(self, carpeta_datos="fichas_leads"):
        self.gestor = GestorDatos(carpeta_datos)
        self.carpeta_datos = carpeta_datos

    def buscar_lead_por_nombre(self, nombre_lead):
        """
        Busca un lead por nombre en todos los archivos JSON de fichas.
        Retorna un diccionario con los archivos donde se encuentra y los datos.
        """
        resultados = {}
        archivos = self.gestor.obtener_archivos()

        for archivo in archivos:
            datos = self.gestor.cargar_datos(archivo)
            if nombre_lead in datos:
                resultados[archivo] = datos[nombre_lead]

        return resultados

    def actualizar_lead_en_todas_fichas(self, nombre_lead, nuevos_datos):
        """
        Actualiza los datos de un lead en todas las fichas donde aparezca.
        Actualiza campos de contacto y propuestas, preservando campos únicos por rubro.
        """
        archivos_afectados = []
        archivos = self.gestor.obtener_archivos()

        # Campos que NO se deben sobrescribir (únicos por rubro)
        campos_excluidos = [
            'categoria', 'rating', 'horario', 'horarios_detallados', 
            'comentarios', 'imagenes', 'enlaces_extra'
        ]

        for archivo in archivos:
            datos = self.gestor.cargar_datos(archivo)
            if nombre_lead in datos:
                lead_actual = datos[nombre_lead]
                
                # Actualizar campos de contacto y propuestas
                for campo, valor in nuevos_datos.items():
                    if campo not in campos_excluidos and valor is not None:
                        # Solo actualizar si el campo está vacío o es menos específico
                        valor_actual = lead_actual.get(campo, '')
                        if not valor_actual or str(valor_actual).lower() in ['no detectado', 'sin teléfono', 'no disponible', '']:
                            lead_actual[campo] = valor

                # Guardar cambios
                self.gestor.guardar_datos(archivo, datos)
                archivos_afectados.append(archivo)

        return archivos_afectados

    def obtener_datos_completos_lead(self, nombre_lead):
        """
        Obtiene los datos más completos de un lead de todas las fichas.
        Prioriza el lead con más canales de contacto marcados como enviados.
        """
        resultados = self.buscar_lead_por_nombre(nombre_lead)
        if not resultados:
            return None

        # Función para calcular el score de completitud
        def calcular_score_completitud(datos):
            score = 0
            # Canales de propuesta enviados (prioridad principal)
            canales = ['propuesta_wa', 'propuesta_ig', 'propuesta_fb', 'propuesta_mail']
            for canal in canales:
                if datos.get(canal):
                    score += 10  # Alta prioridad por canal contactado
            
            # Datos de contacto disponibles
            campos_contacto = ['telefono', 'email', 'whatsapp', 'instagram', 'facebook', 'website']
            for campo in campos_contacto:
                valor = datos.get(campo, '')
                if valor and str(valor).lower() not in ['no detectado', 'sin teléfono', 'no disponible', '']:
                    score += 1
            
            # Propuesta general enviada
            if datos.get('propuesta_enviada'):
                score += 5
            
            return score

        # Encontrar el lead con el score más alto
        mejor_score = -1
        datos_mas_completos = None
        archivo_mas_completo = None

        for archivo, datos in resultados.items():
            score = calcular_score_completitud(datos)
            if score > mejor_score:
                mejor_score = score
                datos_mas_completos = datos.copy()
                archivo_mas_completo = archivo

        return datos_mas_completos

    def limpiar_duplicados_globales(self):
        """
        Función para limpiar duplicados a nivel global (futuro desarrollo).
        Por ahora, solo reporta duplicados.
        """
        # Implementación futura: crear un archivo maestro con leads únicos
        pass