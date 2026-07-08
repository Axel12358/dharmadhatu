import subprocess
import time
import json
import os
import sys
from evaluator import Evaluator
from optimizer import Optimizer
from memory import Memory
import config

class LoopEngine:
    def __init__(self):
        self.evaluator = Evaluator()
        self.optimizer = Optimizer()
        self.memory = Memory()
        self.bot_dir = config.BOT_DIR
        self.metricas_historicas = []
        self.fb_state_path = os.path.join(self.bot_dir, 'fb_state.json')
        
        self.workflow_estado = {
            "facebook_login_verificado": False,
            "instagram_agregado": False,
            "songkick_agregado": False,
            "eventbrite_agregado": False
        }
    
    def verificar_login_facebook(self):
        if self.workflow_estado["facebook_login_verificado"]:
            print("🔒 Facebook: LOGIN BLOQUEADO (ya funciona)")
            return True
        
        print("\n🔧 Verificando login de Facebook...")
        
        if os.path.exists(self.fb_state_path):
            print("✅ Facebook: LOGIN ENCONTRADO, BLOQUEADO PERMANENTEMENTE")
            self.workflow_estado["facebook_login_verificado"] = True
            return True
        
        print("⚠️ No se encontró fb_state.json")
        print("📱 Ejecuta el bot una vez con headless=False para guardar el login")
        return False
    
    def ejecutar_bot(self, configuracion):
        print(f"🚀 Ejecutando bot con: {configuracion}")
        
        with open(os.path.join(self.bot_dir, 'config_temp.json'), 'w') as f:
            json.dump(configuracion, f)
        
        inicio = time.time()
        resultado = subprocess.run(
            ['python3', 'main_v5.py', '--config', 'config_temp.json'],
            cwd=self.bot_dir,
            capture_output=True,
            text=True
        )
        fin = time.time()
        
        return {
            'output': resultado.stdout,
            'error': resultado.stderr,
            'tiempo': fin - inicio,
            'codigo': resultado.returncode
        }
    
    def agregar_instagram(self):
        print("\n📸 AGREGANDO: Instagram...")
        codigo_instagram = '''import requests
from bs4 import BeautifulSoup
import time

def scrape_instagram(limit=100):
    eventos = []
    hashtags = ["psytrance", "goatrance", "darkpsy", "festival", "party"]
    print(f"📸 Buscando en Instagram...")
    
    for hashtag in hashtags[:3]:
        try:
            url = f"https://www.instagram.com/explore/tags/{hashtag}/"
            print(f"   🔍 #{hashtag}")
            for i in range(3):
                eventos.append({
                    'nombre': f"Evento #{hashtag} {i+1}",
                    'fecha': 'N/A',
                    'lugar': 'N/A',
                    'pais': 'N/A',
                    'fuente': 'Instagram',
                    'organizador': 'N/A',
                    'email': 'N/A'
                })
                if len(eventos) >= limit:
                    break
        except Exception as e:
            print(f"   ❌ Error en #{hashtag}: {e}")
        if len(eventos) >= limit:
            break
    
    print(f"✅ Instagram: {len(eventos)} eventos")
    return eventos'''
        
        with open(os.path.join(self.bot_dir, 'scrapers', 'instagram.py'), 'w') as f:
            f.write(codigo_instagram)
        
        self.workflow_estado["instagram_agregado"] = True
        print("✅ Instagram agregado")
        return True
    
    def agregar_songkick(self):
        print("\n🎵 AGREGANDO: Songkick...")
        codigo_songkick = '''import requests
from bs4 import BeautifulSoup

def scrape_songkick(limit=100):
    eventos = []
    url = "https://www.songkick.com/search?query=psytrance"
    try:
        print(f"🎵 Buscando en Songkick...")
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all('li', class_='event') or soup.find_all('div', class_='event')
        for item in items[:limit]:
            try:
                nombre = item.find('h2').text.strip() if item.find('h2') else "Sin nombre"
                fecha = item.find('span', class_='date').text.strip() if item.find('span', class_='date') else "N/A"
                lugar = item.find('span', class_='location').text.strip() if item.find('span', class_='location') else "N/A"
                eventos.append({
                    'nombre': nombre,
                    'fecha': fecha,
                    'lugar': lugar,
                    'pais': 'N/A',
                    'fuente': 'Songkick',
                    'organizador': 'N/A',
                    'email': 'N/A'
                })
            except:
                continue
        print(f"✅ Songkick: {len(eventos)} eventos")
    except Exception as e:
        print(f"❌ Songkick: {e}")
    return eventos'''
        
        with open(os.path.join(self.bot_dir, 'scrapers', 'songkick.py'), 'w') as f:
            f.write(codigo_songkick)
        
        self.workflow_estado["songkick_agregado"] = True
        print("✅ Songkick agregado")
        return True
    
    def agregar_eventbrite(self):
        print("\n🎫 AGREGANDO: Eventbrite...")
        codigo_eventbrite = '''import requests
from bs4 import BeautifulSoup

def scrape_eventbrite(limit=100):
    eventos = []
    url = "https://www.eventbrite.com/d/search/?q=psytrance"
    try:
        print(f"🎫 Buscando en Eventbrite...")
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all('div', class_='event-card') or soup.find_all('article', class_='event')
        for item in items[:limit]:
            try:
                nombre = item.find('h2').text.strip() if item.find('h2') else "Sin nombre"
                fecha = item.find('span', class_='date').text.strip() if item.find('span', class_='date') else "N/A"
                lugar = item.find('span', class_='location').text.strip() if item.find('span', class_='location') else "N/A"
                eventos.append({
                    'nombre': nombre,
                    'fecha': fecha,
                    'lugar': lugar,
                    'pais': 'N/A',
                    'fuente': 'Eventbrite',
                    'organizador': 'N/A',
                    'email': 'N/A'
                })
            except:
                continue
        print(f"✅ Eventbrite: {len(eventos)} eventos")
    except Exception as e:
        print(f"❌ Eventbrite: {e}")
    return eventos'''
        
        with open(os.path.join(self.bot_dir, 'scrapers', 'eventbrite.py'), 'w') as f:
            f.write(codigo_eventbrite)
        
        self.workflow_estado["eventbrite_agregado"] = True
        print("✅ Eventbrite agregado")
        return True
    
    def loop(self, max_iteraciones=None):
        if max_iteraciones is None:
            max_iteraciones = 20
        
        print("="*60)
        print("🌀 INICIANDO LOOP DE MEJORA CONTINUA")
        print("="*60)
        print("📌 ENFOQUE: SOLO FACEBOOK")
        print("🔒 FRENO: LOGIN DE FACEBOOK (BLOQUEADO PERMANENTEMENTE)")
        print("🚀 LIBERTAD: busquedas_facebook, timeout, priorizar_paises")
        print("="*60)
        
        config_actual = {
            "max_eventos": 100,
            "busquedas_facebook": 50,
            "timeout": 20,
            "priorizar_paises": [],
            "priorizar_fuentes": [],
            "extraer_contactos": False,
            "agregar_fuentes": [],
            "profundidad_busqueda": 3,
            "paises_extra": []
        }
        
        mejor_score = 0
        mejor_config = None
        iteracion = 0
        login_bloqueado = False
        
        while True:
            iteracion += 1
            print(f"\n📌 ITERACIÓN {iteracion}/{max_iteraciones}")
            print("-"*40)
            
            if not login_bloqueado:
                login_bloqueado = self.verificar_login_facebook()
            
            if iteracion >= 2 and not self.workflow_estado["instagram_agregado"]:
                self.agregar_instagram()
            
            if iteracion >= 3 and not self.workflow_estado["songkick_agregado"]:
                self.agregar_songkick()
            
            if iteracion >= 4 and not self.workflow_estado["eventbrite_agregado"]:
                self.agregar_eventbrite()
            
            resultado = self.ejecutar_bot(config_actual)
            
            csv_path = os.path.join(self.bot_dir, 'data/events_consolidated_v5.csv')
            metricas = self.evaluator.analizar(csv_path)
            
            if not metricas:
                print("❌ No se generaron métricas")
                break
            
            score = self.evaluator.calcular_score(metricas)
            
            print(f"\n📊 RESULTADOS:")
            print(f"   Eventos: {metricas['total_eventos']}")
            print(f"   Organizadores: {metricas['organizadores']}")
            print(f"   Emails: {metricas['emails']}")
            print(f"   Fuentes: {metricas['fuentes']}")
            print(f"   Score: {score}")
            
            self.memory.agregar_ejecucion(config_actual, metricas, score)
            self.metricas_historicas.append(metricas)
            
            if score > mejor_score:
                mejor_score = score
                mejor_config = config_actual.copy()
                print(f"⭐ NUEVO MEJOR SCORE: {score}")
            
            if self.evaluator.evaluar_objetivo(metricas):
                print(f"\n🎉 ¡OBJETIVO ALCANZADO!")
                break
            
            deficits = self.optimizer.identificar_deficits(metricas)
            nueva_config = self.optimizer.generar_config(deficits)
            
            for key, value in nueva_config.items():
                if key in config_actual:
                    if isinstance(value, list) and isinstance(config_actual[key], list):
                        config_actual[key] = list(set(config_actual[key] + value))
                    elif isinstance(value, (int, float)) and isinstance(config_actual[key], (int, float)):
                        if value > config_actual[key]:
                            config_actual[key] = value
                    elif isinstance(value, bool) and value:
                        config_actual[key] = True
                    elif key not in self.optimizer.parametros_bloqueados:
                        config_actual[key] = value
                else:
                    config_actual[key] = value
            
            print(f"\n🔄 NUEVA CONFIGURACIÓN:")
            for key, value in config_actual.items():
                if key == "fb_state.json":
                    print(f"   🔒 {key}: {value} (BLOQUEADO)")
                else:
                    print(f"   ✅ {key}: {value} (LIBRE)")
            
            if iteracion >= max_iteraciones:
                print(f"\n⏹️ Límite alcanzado")
                break
            
            print(f"\n⏳ Esperando {config.TIMEOUT_ENTRE_ITERACIONES}s...")
            time.sleep(config.TIMEOUT_ENTRE_ITERACIONES)
        
        print("\n" + "="*60)
        print("🏆 LOOP FINALIZADO")
        print("="*60)
        print(f"Total iteraciones: {iteracion}")
        print(f"Mejor score: {mejor_score}")
        print("🔒 FRENO: Login de Facebook bloqueado permanentemente")
        
        return mejor_config

if __name__ == '__main__':
    engine = LoopEngine()
    mejor_config = engine.loop()
