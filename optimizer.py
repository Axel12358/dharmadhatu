import json
from datetime import datetime

class Optimizer:
    def __init__(self):
        self.objetivo_eventos = 200
        self.objetivo_organizadores = 40
        self.objetivo_emails = 30
        self.contador_iteraciones = 0
        
        # ============================================================
        # BLOQUEADO: SOLO EL LOGIN DE FACEBOOK (ya funciona)
        # ============================================================
        self.parametros_bloqueados = {
            "fb_state.json": "NO TOCAR"
        }
    
    def verificar_eventos(self, metricas):
        return metricas['total_eventos'] < self.objetivo_eventos
    
    def verificar_organizadores(self, metricas):
        return metricas['organizadores'] < self.objetivo_organizadores
    
    def verificar_emails(self, metricas):
        return metricas['emails'] < self.objetivo_emails
    
    def verificar_fuentes(self, metricas):
        return metricas['fuentes'] < 4
    
    def identificar_deficits(self, metricas):
        deficits = []
        recomendaciones = []
        prioridad = "Ninguna"
        
        if self.verificar_eventos(metricas):
            faltan = self.objetivo_eventos - metricas['total_eventos']
            deficits.append(f"Faltan {faltan} eventos")
            recomendaciones.append("AUMENTAR busquedas_facebook")
            recomendaciones.append("AUMENTAR max_eventos")
            prioridad = "Aumentar eventos"
        
        if self.verificar_organizadores(metricas):
            faltan = self.objetivo_organizadores - metricas['organizadores']
            deficits.append(f"Faltan {faltan} organizadores")
            recomendaciones.append("ACTIVAR extraer_contactos")
            if prioridad == "Ninguna":
                prioridad = "Extraer organizadores"
        
        if self.verificar_emails(metricas):
            faltan = self.objetivo_emails - metricas['emails']
            deficits.append(f"Faltan {faltan} emails")
            recomendaciones.append("ACTIVAR extraer_contactos")
            if prioridad == "Ninguna":
                prioridad = "Extraer emails"
        
        if self.verificar_fuentes(metricas):
            deficits.append(f"Pocas fuentes ({metricas['fuentes']}/4)")
            recomendaciones.append("AGREGAR más países")
            if prioridad == "Ninguna":
                prioridad = "Agregar fuentes"
        
        if not deficits:
            deficits = ["Ninguno"]
            recomendaciones = ["Mantener"]
            prioridad = "Mantener"
        
        self.contador_iteraciones += 1
        
        return {
            'deficits': deficits,
            'recomendaciones': recomendaciones,
            'prioridad': prioridad,
            'iteracion': self.contador_iteraciones,
            'timestamp': datetime.now().isoformat()
        }
    
    def generar_config(self, deficits):
        config = {}
        prioridad = deficits.get('prioridad', 'Ninguna')
        
        if prioridad == "Aumentar eventos" or "eventos" in str(deficits):
            config["busquedas_facebook"] = 100
            config["max_eventos"] = 150
            config["timeout"] = 30
        
        if prioridad == "Extraer organizadores" or prioridad == "Extraer emails":
            config["extraer_contactos"] = True
        
        if prioridad == "Agregar fuentes" or "fuentes" in str(deficits):
            config["priorizar_paises"] = ["España", "Portugal", "Alemania", "Francia", "Italia", "Holanda", "Bélgica", "Suiza"]
        
        if prioridad == "Mantener":
            config["busquedas_facebook"] = 70
            config["timeout"] = 25
        
        return config

