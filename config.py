# Configuración del loop
import os

# Directorios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOT_DIR = os.path.expanduser("~/dharmadhatu_bot")

# Modelo de Ollama
OLLAMA_MODEL = "dharmadhatu-fast"

# Objetivos del loop
OBJETIVO_EVENTOS = 200
OBJETIVO_ORGANIZADORES = 40
MAX_ITERACIONES = 10

# Pesos para el score
PESO_EVENTOS = 1.0
PESO_ORGANIZADORES = 2.0
PESO_EMAILS = 3.0
PESO_FUENTES = 10.0

# Tiempos
TIMEOUT_ENTRE_ITERACIONES = 5
