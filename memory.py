import json
import os
from datetime import datetime
import pandas as pd

class Memory:
    def __init__(self, archivo="data/memoria_mejora.json"):
        self.archivo = archivo
        self.datos = self.cargar()
    
    def cargar(self):
        try:
            with open(self.archivo, 'r') as f:
                return json.load(f)
        except:
            return {"ejecuciones": [], "mejores_configs": [], "historial": []}
    
    def guardar(self):
        os.makedirs(os.path.dirname(self.archivo), exist_ok=True)
        
        # Función para convertir tipos no serializables
        def convertir_serializable(obj):
            if isinstance(obj, dict):
                return {k: convertir_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convertir_serializable(item) for item in obj]
            elif isinstance(obj, (pd.Series, pd.DataFrame)):
                return obj.to_dict()
            elif isinstance(obj, (pd.Timestamp, datetime)):
                return obj.isoformat()
            elif hasattr(obj, 'dtype'):
                if 'int' in str(obj.dtype):
                    return int(obj)
                elif 'float' in str(obj.dtype):
                    return float(obj)
                else:
                    return str(obj)
            else:
                return obj
        
        # Convertir datos
        datos_serializables = convertir_serializable(self.datos)
        
        with open(self.archivo, 'w') as f:
            json.dump(datos_serializables, f, indent=2)
    
    def agregar_ejecucion(self, config, metricas, score):
        self.datos["ejecuciones"].append({
            "config": config,
            "metricas": metricas,
            "score": score,
            "timestamp": datetime.now().isoformat()
        })
        self.datos["historial"].append(metricas)
        self.guardar()
    
    def get_mejor_config(self):
        if self.datos["ejecuciones"]:
            mejor = max(self.datos["ejecuciones"], key=lambda x: x["score"])
            return mejor["config"]
        return None
