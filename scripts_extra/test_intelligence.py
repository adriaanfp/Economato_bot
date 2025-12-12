import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from buscador import buscar_coincidencias

def test(input_str):
    print(f"Input: '{input_str}'")
    try:
        res = buscar_coincidencias(input_str)
        print(f"Result: {res}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 20)

if __name__ == "__main__":
    print("--- Testing Logic ---\n")
    
    # 1. Exact / Autocorrect (>95%)
    # Assuming 'Tomate' or 'Leche' is in the catalog
    test("Leche") # Exact match

    # 2. Single Candidate Rule (80-94% but unique)
    # If 'Tomate Pera' exists but 'Tomate' input is 88%, it should auto-accept if it's the only one.
    test("Tomate") 

    # Plural Rule Check (Tomates -> Tomate or Tomates if exists)
    test("Tomates") 

    # 3. Real Doubt Rule (Multiple >80%)
    # 'Lech' should trigger multiple if 'Leche', 'Leche Entera', etc. exist
    test("Lech") 

    # 4. Strict Reject (<80%)
    test("Vino")
    test("Computadora")

    # 5. Regex Extraction Test
    print("\n--- Testing Quantity Extraction ---")
    import re
    def extraer_cantidad(texto):
        patron = r"(\d+(?:[.,]\d+)?)\s*(kg|kilos|l|litros|unidades|u|g|gramos|ml|cl|uds|cajas|botes|botellas)?$"
        match = re.search(patron, texto, re.IGNORECASE)
        if match:
            cantidad_completa = match.group(0).strip()
            producto_limpio = texto[:match.start()].strip()
            return cantidad_completa, producto_limpio
        return None, texto

    item = "Tomate 6 kg"
    q, clean = extraer_cantidad(item)
    print(f"'{item}' -> Q: '{q}', Clean: '{clean}'")
    
    item = "Leche 50L"
    q, clean = extraer_cantidad(item)
    print(f"'{item}' -> Q: '{q}', Clean: '{clean}'")
    
    item = "Solomillo de ternera 2.5 kilos"
    q, clean = extraer_cantidad(item)
    print(f"'{item}' -> Q: '{q}', Clean: '{clean}'")

    print("\n--- Score Analysis ---")
    from thefuzz import process
    try:
        import pandas as pd
        df = pd.read_csv("catalogo_unificado.csv")
        choices = df['producto_norm'].unique().tolist()
        
        def show_scores(term):
            print(f"Scores for '{term}':")
            matches = process.extract(term, choices, limit=3)
            for m in matches:
                print(f"  - {m[0]}: {m[1]}")
                
        show_scores("Tomate")
        show_scores("Leche")
        show_scores("Lech")
    except Exception as e:
        print(f"Skipping value analysis: {e}")
