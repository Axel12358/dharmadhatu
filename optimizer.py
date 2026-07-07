import json
from datetime import datetime
import random

class Optimizer:
    def __init__(self):
        self.objetivo_eventos = 200
        self.objetivo_organizadores = 40
        self.objetivo_emails = 30
        self.contador_iteraciones = 0
        
        # Fuentes que NUNCA se quitan
        self.fuentes_base = ["Goabase", "Grupos Fijos"]
    
    def verificar_eventos(self, metricas):
        return metricas['total_eventos'] < self.objetivo_eventos
    
    def verificar_organizadores(self, metricas):
        return metricas['organizadores'] < self.objetivo_organizadores
    
    def verificar_emails(self, metricas):
        return metricas['emails'] < self.objetivo_emails
    
    def verificar_fuentes(self, metricas):
        return metricas['fuentes'] < 4
    
    def identificar_deficits(self, metricas):
        """Identifica deficits y recomienda agregar, no quitar"""
        
        deficits = []
        recomendaciones = []
        prioridad = "Ninguna"
        
        # 1. Eventos
        if self.verificar_eventos(metricas):
            faltan = self.objetivo_eventos - metricas['total_eventos']
            deficits.append(f"Faltan {faltan} eventos para llegar a {self.objetivo_eventos}")
            recomendaciones.append("AGREGAR más búsquedas en Facebook")
            recomendaciones.append("AGREGAR nueva fuente de scraping (Ej: Resident Advisor)")
            prioridad = "Aumentar eventos"
        
        # 2. Organizadores
        if self.verificar_organizadores(metricas):
            faltan = self.objetivo_organizadores - metricas['organizadores']
            deficits.append(f"Faltan {faltan} organizadores para llegar a {self.objetivo_organizadores}")
            recomendaciones.append("AGREGAR extracción de organizadores con Ollama")
            if prioridad == "Ninguna":
                prioridad = "Extraer organizadores"
        
        # 3. Emails
        if self.verificar_emails(metricas):
            faltan = self.objetivo_emails - metricas['emails']
            deficits.append(f"Faltan {faltan} emails para llegar a {self.objetivo_emails}")
            recomendaciones.append("AGREGAR extracción de emails con Ollama")
            if prioridad == "Ninguna":
                prioridad = "Extraer emails"
        
        # 4. Fuentes
        if self.verificar_fuentes(metricas):
            deficits.append(f"Pocas fuentes de datos (actuales: {metricas['fuentes']}, mínimo: 4)")
            recomendaciones.append("AGREGAR nueva fuente de scraping")
            recomendaciones.append("AGREGAR más países a la búsqueda")
            if prioridad == "Ninguna":
                prioridad = "Agregar fuentes"
        
        # Si no hay deficits, mantener y mejorar
        if not deficits:
            deficits = ["Ninguno, los resultados son buenos"]
            recomendaciones = ["Mantener configuración actual y agregar pequeñas mejoras"]
            prioridad = "Mantener"
        
        self.contador_iteraciones += 1
        
        resultado = {
            'deficits': deficits,
            'recomendaciones': recomendaciones,
            'prioridad': prioridad,
            'iteracion': self.contador_iteraciones,
            'timestamp': datetime.now().isoformat()
        }
        
        return resultado
    
    def generar_config(self, deficits):
        """Genera nueva configuración AGREGANDO, NUNCA QUITANDO"""
        
        # Configuración base (NUNCA se quita lo que ya funciona)
        config = {
            "max_eventos": 100,
            "busquedas_facebook": 50,
            "timeout": 20,
            "priorizar_paises": [],
            "priorizar_fuentes": [],
            "extraer_contactos": False,
            # NUEVOS parámetros que se AGREGAN
            "agregar_fuentes": [],
            "profundidad_busqueda": 3,
            "paises_extra": []
        }
        
        prioridad = deficits.get('prioridad', 'Ninguna')
        
        # --- ESTRATEGIA 1: AGREGAR más eventos ---
        if prioridad == "Aumentar eventos" or "eventos" in str(deficits):
            # Aumentar sin bajar
            config["max_eventos"] = max(config["max_eventos"] + random.randint(30, 80), 150)
            config["busquedas_facebook"] = max(config["busquedas_facebook"] + random.randint(10, 40), 80)
            config["profundidad_busqueda"] = max(config["profundidad_busqueda"] + 1, 4)
        
        # --- ESTRATEGIA 2: AGREGAR organizadores ---
        if prioridad == "Extraer organizadores" or "organizadores" in str(deficits):
            config["extraer_contactos"] = True
            # Agregar más búsquedas para encontrar organizadores
            config["busquedas_facebook"] += random.randint(10, 30)
        
        # --- ESTRATEGIA 3: AGREGAR emails ---
        if prioridad == "Extraer emails" or "emails" in str(deficits):
            config["extraer_contactos"] = True
            config["busquedas_facebook"] += random.randint(5, 20)
        
        # --- ESTRATEGIA 4: AGREGAR fuentes ---
        if prioridad == "Agregar fuentes" or "fuentes" in str(deficits):
            # AGREGAR países (no quitar los que ya están)
            paises_posibles = ["España", "Portugal", "Alemania", "Francia", "Italia", "Holanda", "Bélgica", "Suiza", "Austria"]
            paises_actuales = config.get("priorizar_paises", [])
            paises_nuevos = random.sample(paises_posibles, min(random.randint(2, 4), len(paises_posibles)))
            config["priorizar_paises"] = list(set(paises_actuales + paises_nuevos))  # UNIÓN, no reemplazo
            
            # AGREGAR nuevas fuentes de scraping
            nuevas_fuentes = ["Resident Advisor", "Songkick", "Eventbrite"]
            config["agregar_fuentes"] = random.sample(nuevas_fuentes, min(random.randint(1, 2), len(nuevas_fuentes)))
        
        # --- ESTRATEGIA 5: Mantener pero AGREGAR mejoras ---
        if prioridad == "Mantener":
            # Agregar países nuevos sin quitar los existentes
            paises_extra = ["Suiza", "Austria", "Croacia", "Hungría"]
            config["paises_extra"] = random.sample(paises_extra, random.randint(1, 2))
            
            # Pequeños ajustes (siempre hacia arriba)
            config["timeout"] = max(config["timeout"] + random.randint(-2, 5), 15)
        
        # NUNCA bajar los valores por debajo de los que ya funcionan
        config["max_eventos"] = max(config["max_eventos"], 100)
        config["busquedas_facebook"] = max(config["busquedas_facebook"], 50)
        config["timeout"] = max(config["timeout"], 15)
        
        return config
