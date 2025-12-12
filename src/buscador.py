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

def buscar_coincidencias(input_usuario):
    """
    Busca coincidencias del input del usuario en el catálogo unificado.
    Retorna:
    - ('exact', nombre_real): Si > 90%
    - ('ambiguous', [opciones]): Si 60% <= similitud <= 90%
    - ('no_match', None): Si < 60%
    """
    if not os.path.exists(CSV_FILE):
        return "no_match", None

    try:
        df = pd.read_csv(CSV_FILE)
    except Exception:
        return "no_match", None

    # Normalizar columna producto
    choices = df['producto_norm'].unique().tolist()
    
    # Regla 0 (Match Exacto case-insensitive)
    input_lower = input_usuario.lower()
    choices_lower = [c.lower() for c in choices]
    if input_lower in choices_lower:
        # Recuperar el nombre original
        idx = choices_lower.index(input_lower)
        return "exact", choices[idx]

    # Fuzzy Search
    matches = process.extract(input_usuario, choices, limit=5)
    
    # Filtrar por umbral mínimo (80)
    filtered = [m for m in matches if m[1] >= 80]
    
    if not filtered:
        return "no_match", None

    best = filtered[0]
    
    # Regla 1 (Casi Perfecto)
    if best[1] >= 98:
        return "exact", best[0]

    # Regla 2 (Candidato Único)
    if len(filtered) == 1:
        return "exact", best[0]
    
    # Regla 3 (Gap/Distancia)
    second = filtered[1]
    if (best[1] - second[1]) >= 10:
        return "exact", best[0]

    # Regla 4 (Plurales)
    # Comprobar si la única diferencia entre el 1º y el 2º es una 's' al final
    name1 = best[0].lower()
    name2 = second[0].lower()
    
    # Verificar si uno es plural del otro (simplemente agregando 's')
    if (name1 == name2 + 's') or (name2 == name1 + 's'):
        # Si son el mismo producto (singular/plural), devolvemos el de mayor puntuación (el 1º) como exacto
        return "exact", best[0]

    # Si no se cumple nada -> Ambigüedad
    return "ambiguous", [m[0] for m in filtered[:3]]

def obtener_datos_mejor_precio(producto_buscado):
    if not os.path.exists(CSV_FILE):
        return {"error": "catalogo_unificado.csv no encontrado. Ejecuta procesador.py primero."}

    try:
        df = pd.read_csv(CSV_FILE)
    except Exception as e:
        return {"error": f"Error al leer el catálogo: {e}"}

    # Aseguramos que la columna proveedor sea string
    df['proveedor'] = df['proveedor'].astype(str)

    # USAR LÓGICA CENTRALIZADA
    match_type, match_result = buscar_coincidencias(producto_buscado)
    
    nombre_final = None
    
    if match_type == "exact":
        nombre_final = match_result
    elif match_type == "ambiguous":
        # Si es ambiguo, para generación de pedidos automática, tomamos el primero
        # pero logueamos advertencia (o idealmente devolvemos error si es estricto)
        # Por ahora tomamos el primero de la lista de ambigüedad
        nombre_final = match_result[0] 
    else:
        return None

    # Filtrar dataframe por este nombre final
    candidates = df[df['producto_norm'] == nombre_final].copy()
    
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