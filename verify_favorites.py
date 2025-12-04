import json
import os
from src.buscador import obtener_datos_mejor_precio

PREFERENCIAS_FILE = "preferencias.json"

def set_preference(product, provider):
    with open(PREFERENCIAS_FILE, 'w', encoding='utf-8') as f:
        json.dump({product.lower(): provider}, f)

def clear_preferences():
    with open(PREFERENCIAS_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f)

def test_vip_logic():
    print("--- INICIANDO TEST VIP ---")
    
    # 1. Limpiar preferencias
    clear_preferences()
    
    # 2. Buscar 'tomate' (debería ser el más barato por defecto)
    print("\n1. Buscando 'tomate' sin preferencias...")
    res_normal = obtener_datos_mejor_precio("tomate")
    print(f"Normal: {res_normal['proveedor']} - {res_normal['precio']}€ (Favorito: {res_normal.get('es_favorito', False)})")
    
    # 3. Forzar un proveedor caro (si existe otro)
    # Asumimos que hay varios proveedores. Si 'res_normal' es Proveedor A, intentaremos forzar Proveedor B si existe en el CSV.
    # Para este test, simplemente forzaremos un nombre de proveedor y veremos si el buscador lo intenta filtrar.
    # Necesitamos saber qué proveedores hay.
    
    import pandas as pd
    df = pd.read_csv('catalogo_unificado.csv')
    tomates = df[df['producto_norm'].str.contains('tomate', case=False)]
    proveedores = tomates['proveedor'].unique()
    
    if len(proveedores) < 2:
        print("⚠️ No hay suficientes proveedores de tomate para probar el cambio. Saltando test de cambio.")
        return

    proveedor_actual = res_normal['proveedor']
    otro_proveedor = [p for p in proveedores if p != proveedor_actual][0]
    
    print(f"\n2. Forzando preferencia: 'tomate' -> '{otro_proveedor}'")
    set_preference("tomate", otro_proveedor)
    
    # TEST FUZZY: Buscamos "tomates" (plural) para ver si detecta la preferencia de "tomate"
    print(f"   Buscando 'tomates' (plural) para probar fuzzy match...")
    res_vip = obtener_datos_mejor_precio("tomates")
    print(f"VIP: {res_vip['proveedor']} - {res_vip['precio']}€ (Favorito: {res_vip.get('es_favorito', False)})")
    
    if res_vip['proveedor'] == otro_proveedor and res_vip.get('es_favorito'):
        print("✅ ÉXITO: El proveedor cambió al favorito (con fuzzy match).")
    else:
        print(f"❌ FALLO: Esperaba {otro_proveedor}, obtuvo {res_vip['proveedor']}")

    # 4. Borrar preferencia
    print("\n3. Borrando preferencia...")
    clear_preferences()
    res_back = obtener_datos_mejor_precio("tomate")
    print(f"Back: {res_back['proveedor']} - {res_back['precio']}€")
    
    if res_back['proveedor'] == proveedor_actual:
        print("✅ ÉXITO: Volvió al proveedor original (más barato).")
    else:
        print("❌ FALLO: No volvió al original.")

if __name__ == "__main__":
    try:
        test_vip_logic()
    except Exception as e:
        print(f"Error en el test: {e}")
