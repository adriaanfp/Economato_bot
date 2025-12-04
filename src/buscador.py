import pandas as pd
from thefuzz import process
import json
import os

PREFERENCIAS_FILE = "preferencias.json"

def load_preferences():
    if not os.path.exists(PREFERENCIAS_FILE):
        return {}
    try:
        with open(PREFERENCIAS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def obtener_datos_mejor_precio(producto_buscado):
    try:
        df = pd.read_csv('catalogo_unificado.csv')
    except FileNotFoundError:
        return {"error": "catalogo_unificado.csv no encontrado. Ejecuta procesador.py primero."}

    # Get list of unique product names (normalized)
    choices = df['producto_norm'].unique().tolist()
    
    # Find top matches
    matches = process.extract(producto_buscado.lower(), choices, limit=10)
    
    # Filter by score > 60
    valid_matches = [match[0] for match in matches if match[1] > 60]
    
    if not valid_matches:
        return None

    # Filter dataframe for these products
    candidates = df[df['producto_norm'].isin(valid_matches)]
    
    if candidates.empty:
         return None

    # --- LOGICA VIP ---
    prefs = load_preferences()
    
    # Fuzzy match for preferences
    # Check if 'producto_buscado' is similar to any key in prefs
    proveedor_favorito = None
    if prefs:
        match_pref = process.extractOne(producto_buscado.lower(), list(prefs.keys()))
        if match_pref and match_pref[1] > 80: # Threshold for preference match
            proveedor_favorito = prefs[match_pref[0]]
    
    es_favorito = False
    
    if proveedor_favorito:
        # Check if favorite provider is in candidates
        vip_candidates = candidates[candidates['proveedor'] == proveedor_favorito]
        if not vip_candidates.empty:
            # If exists, force selection from this provider (cheapest among them if multiple)
            candidates = vip_candidates
            es_favorito = True
    # ------------------

    # Find the row with the minimum price
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

    return f"💰 GANADOR: {datos['producto']} | Proveedor: {datos['proveedor']} | Precio: {datos['precio']}€"

if __name__ == "__main__":
    print("--- Probando Buscador ---")
    print(buscar_mejor_precio("solomillo"))
    print(buscar_mejor_precio("leche"))
    print(buscar_mejor_precio("tomate"))
    print(buscar_mejor_precio("huevos"))