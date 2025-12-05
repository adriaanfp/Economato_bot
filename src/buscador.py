import pandas as pd
from thefuzz import process
import json
import os

# Definir rutas absolutas para evitar errores de "File not found"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREFERENCIAS_FILE = os.path.join(BASE_DIR, "preferencias.json")
CSV_FILE = os.path.join(BASE_DIR, "catalogo_unificado.csv")

def load_preferences():
    if not os.path.exists(PREFERENCIAS_FILE):
        return {}
    try:
        with open(PREFERENCIAS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def obtener_datos_mejor_precio(producto_buscado):
    if not os.path.exists(CSV_FILE):
        return {"error": "catalogo_unificado.csv no encontrado. Ejecuta procesador.py primero."}

    try:
        df = pd.read_csv(CSV_FILE)
    except Exception as e:
        return {"error": f"Error al leer el catálogo: {e}"}

    # Aseguramos que la columna proveedor sea string
    df['proveedor'] = df['proveedor'].astype(str)

    # Obtener lista de productos únicos normalizados
    choices = df['producto_norm'].unique().tolist()
    
    # Buscar coincidencias
    matches = process.extract(producto_buscado.lower(), choices, limit=10)
    
    # Filtrar por puntuación > 60
    valid_matches = [match[0] for match in matches if match[1] > 60]
    
    if not valid_matches:
        return None

    # Filtrar dataframe por estos productos
    candidates = df[df['producto_norm'].isin(valid_matches)].copy()
    
    if candidates.empty:
         return None

    # --- LÓGICA VIP ---
    prefs = load_preferences()
    
    proveedor_favorito = None
    if prefs:
        # Buscar si el producto buscado tiene preferencia
        match_pref = process.extractOne(producto_buscado.lower(), list(prefs.keys()))
        if match_pref and match_pref[1] > 80:
            proveedor_favorito = prefs[match_pref[0]]
    
    es_favorito = False
    
    if proveedor_favorito:
        # Comparación case-insensitive
        vip_candidates = candidates[candidates['proveedor'].str.lower() == proveedor_favorito.lower()]
        
        if not vip_candidates.empty:
            candidates = vip_candidates
            es_favorito = True
    # ------------------

    # Encontrar la fila con el precio mínimo
    best_option = candidates.loc[candidates['precio'].idxmin()]
    
    return {
        "producto": best_option['producto'],
        "proveedor": best_option['proveedor'],
        "precio": best_option['precio'],
        "nombre_real": best_option['producto'],
        "es_favorito": es_favorito
    }

def buscar_mejor_precio(producto_buscado):
    datos = obtener_datos_mejor_precio(producto_buscado)
    
    if not datos:
        return f"❌ No se encontraron coincidencias para '{producto_buscado}'."
        
    if "error" in datos:
        return datos["error"]

    icono_vip = "⭐ VIP" if datos['es_favorito'] else "💰 Mejor Precio"
    return f"{icono_vip}: {datos['producto']} | Proveedor: {datos['proveedor']} | Precio: {datos['precio']}€"

if __name__ == "__main__":
    print("--- Probando Buscador ---")
    print(buscar_mejor_precio("tomate"))