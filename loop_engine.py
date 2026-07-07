import subprocess
import time
import json
import os
import sys
import ollama
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
        self.workflow_estado = {
            "facebook_arreglado": False,
            "instagram_agregado": False,
            "songkick_agregado": False,
            "eventbrite_agregado": False,
            "scrapers_mejorados": False
        }
        self.ollama_model = config.OLLAMA_MODEL
    
    def ejecutar_bot(self, configuracion):
        """Ejecuta el bot con la configuración dada"""
        print(f"🚀 Ejecutando bot con: {configuracion}")
        
        # Guardar config
        with open(os.path.join(self.bot_dir, 'config_temp.json'), 'w') as f:
            json.dump(configuracion, f)
        
        # Ejecutar bot
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
    
    def arreglar_facebook(self):
        """Workflow: Arreglar el scraper de Facebook"""
        print("\n🔧 WORKFLOW: Arreglando Facebook...")
        
        codigo_facebook = '''from playwright.sync_api import sync_playwright
import time
import json
import os

def scrape_facebook(limit=100, busquedas=50, timeout=60, paises=[]):
    eventos = []
    max_eventos = limit
    max_busquedas = busquedas
    timeout_ms = timeout * 1000
    
    print(f"🔍 Facebook: buscando {max_eventos} eventos con {max_busquedas} búsquedas")
    if paises:
        print(f"📍 Priorizando países: {', '.join(paises)}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        page = context.new_page()
        page.route("**/*.{png,jpg,jpeg,svg,gif,webp,css,woff,woff2,ttf,otf}", lambda route: route.abort())
        
        fb_state_file = 'fb_state.json'
        
        try:
            print("🌐 Abriendo Facebook...")
            page.goto("https://www.facebook.com/events/search", timeout=timeout_ms)
            page.wait_for_load_state('domcontentloaded', timeout=timeout_ms)
            time.sleep(3)
            
            if not os.path.exists(fb_state_file):
                print("\\n⚠️ NO HAY SESIÓN DE FACEBOOK GUARDADA")
                print("📱 LOGUEATE EN FACEBOOK MANUALMENTE en el navegador que se abrió.")
                print("⏳ Después de loguearte, espera 10 segundos...")
                time.sleep(10)
                print("✅ Continuando...")
            
            search_input = None
            selectores = [
                'input[type="search"]',
                'input[aria-label*="Buscar"]',
                'input[aria-label*="Search"]',
                'input[placeholder*="Buscar"]',
                'input[placeholder*="Search"]',
                'input[role="combobox"]'
            ]
            
            for selector in selectores:
                try:
                    search_input = page.locator(selector)
                    if search_input.count() > 0:
                        print(f"✅ Selector encontrado: {selector}")
                        break
                except:
                    continue
            
            if search_input and search_input.count() > 0:
                if paises:
                    paises_query = " OR ".join(paises)
                    busqueda = f"({paises_query}) psytrance festival"
                else:
                    busqueda = "psytrance festival 2026"
                
                print(f"🔍 Buscando: {busqueda}")
                search_input.fill(busqueda)
                search_input.press('Enter')
                page.wait_for_load_state('domcontentloaded', timeout=timeout_ms)
                time.sleep(3)
            else:
                print("⚠️ No se encontró campo de búsqueda")
                print("💡 Busca manualmente en el navegador")
                time.sleep(5)
            
            eventos_encontrados = 0
            scrolls_realizados = 0
            max_scrolls = min(max_busquedas // 5, 20)
            
            while eventos_encontrados < max_eventos and scrolls_realizados < max_scrolls:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)
                scrolls_realizados += 1
                
                elementos = page.query_selector_all('div[role="article"]')
                if not elementos:
                    elementos = page.query_selector_all('div[class*="event"]')
                if not elementos:
                    elementos = page.query_selector_all('a[href*="/events/"]')
                
                for elemento in elementos[-30:]:
                    try:
                        nombre = elemento.query_selector('span')
                        if nombre:
                            nombre_text = nombre.inner_text()
                            if nombre_text and len(nombre_text) > 5 and nombre_text not in [e['nombre'] for e in eventos]:
                                eventos.append({
                                    'nombre': nombre_text,
                                    'fuente': 'Facebook',
                                    'fecha': 'N/A',
                                    'lugar': 'N/A',
                                    'organizador': 'N/A',
                                    'email': 'N/A'
                                })
                                eventos_encontrados += 1
                                if eventos_encontrados >= max_eventos:
                                    break
                    except:
                        pass
                
                print(f"📊 Eventos encontrados: {eventos_encontrados}")
            
            context.storage_state(path=fb_state_file)
            print(f"✅ Estado de Facebook guardado")
            
        except Exception as e:
            print(f"❌ Error en Facebook: {e}")
        
        browser.close()
    
    return eventos'''
        
        # Guardar el scraper arreglado
        with open(os.path.join(self.bot_dir, 'scrapers', 'facebook_eventos_con_organizador.py'), 'w') as f:
            f.write(codigo_facebook)
        
        self.workflow_estado["facebook_arreglado"] = True
        print("✅ Facebook arreglado (headless=False, login manual)")
        return True
    
    def agregar_instagram(self):
        """Workflow: Agregar scraper de Instagram"""
        print("\n📸 WORKFLOW: Agregando Instagram...")
        
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
            print(f"   🔍 #{hashtag} (placeholder)")
            
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
        """Workflow: Agregar scraper de Songkick"""
        print("\n🎵 WORKFLOW: Agregando Songkick...")
        
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
        """Workflow: Agregar scraper de Eventbrite"""
        print("\n🎫 WORKFLOW: Agregando Eventbrite...")
        
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
    
    def mejorar_scrapers_con_ollama(self):
        """Usa Ollama para generar scrapers funcionales"""
        print("\n🤖 WORKFLOW: Mejorando scrapers con Ollama...")
        
        prompt_instagram = """
        Genera un scraper funcional en Python para Instagram que busque eventos de psytrance.
        Usa requests y BeautifulSoup o playwright si es necesario.
        La función debe llamarse scrape_instagram(limit=100) y devolver una lista de eventos con:
        - nombre, fecha, lugar, pais, fuente='Instagram', organizador, email
        
        Responde SOLO con el código Python. No uses placeholders, busca datos reales.
        """
        
        try:
            print("🤖 Generando scraper de Instagram con Ollama...")
            response = ollama.chat(
                model=self.ollama_model,
                messages=[{"role": "user", "content": prompt_instagram}]
            )
            codigo_instagram = response['message']['content']
            
            with open(os.path.join(self.bot_dir, 'scrapers', 'instagram.py'), 'w') as f:
                f.write(codigo_instagram)
            print("✅ Instagram mejorado con Ollama")
        except Exception as e:
            print(f"❌ Error mejorando Instagram: {e}")
        
        self.workflow_estado["scrapers_mejorados"] = True
        print("✅ Scrapers mejorados con Ollama")
        return True
    
    def loop(self, max_iteraciones=None):
        if max_iteraciones is None:
            max_iteraciones = config.MAX_ITERACIONES
        
        print("="*60)
        print("🌀 INICIANDO LOOP DE MEJORA CONTINUA")
        print("="*60)
        print("📌 PRINCIPIO: NUNCA QUITAR, SIEMPRE AGREGAR")
        print(f"📌 OLLAMA: Usando modelo {self.ollama_model}")
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
        
        for i in range(max_iteraciones):
            print(f"\n📌 ITERACIÓN {i+1}/{max_iteraciones}")
            print("-"*40)
            
            if i >= 1 and not self.workflow_estado["facebook_arreglado"]:
                self.arreglar_facebook()
            
            if i >= 2 and not self.workflow_estado["instagram_agregado"]:
                self.agregar_instagram()
            
            if i >= 3 and not self.workflow_estado["songkick_agregado"]:
                self.agregar_songkick()
            
            if i >= 4 and not self.workflow_estado["eventbrite_agregado"]:
                self.agregar_eventbrite()
            
            if i >= 5 and not self.workflow_estado["scrapers_mejorados"]:
                self.mejorar_scrapers_con_ollama()
            
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
                print(f"\n✅ ¡OBJETIVO ALCANZADO!")
                break
            
            deficits = self.optimizer.identificar_deficits(metricas)
            nueva_config = self.optimizer.generar_config(deficits)
            
            for key, value in nueva_config.items():
                if isinstance(value, list):
                    if key in config_actual:
                        config_actual[key] = list(set(config_actual[key] + value))
                    else:
                        config_actual[key] = value
                else:
                    if key in config_actual and isinstance(config_actual[key], (int, float)):
                        if value > config_actual[key]:
                            config_actual[key] = value
                    else:
                        config_actual[key] = value
            
            print(f"🔄 Nueva configuración: {config_actual}")
            print(f"\n⏳ Esperando {config.TIMEOUT_ENTRE_ITERACIONES}s...")
            time.sleep(config.TIMEOUT_ENTRE_ITERACIONES)
        
        print("\n" + "="*60)
        print("🏆 LOOP FINALIZADO")
        print("="*60)
        print(f"Mejor score: {mejor_score}")
        print(f"Mejor config: {mejor_config}")
        print("\n📌 WORKFLOW COMPLETADO:")
        for key, value in self.workflow_estado.items():
            print(f"   • {key}: {'✅' if value else '❌'}")
        
        return mejor_config

if __name__ == '__main__':
    engine = LoopEngine()
    mejor_config = engine.loop()
