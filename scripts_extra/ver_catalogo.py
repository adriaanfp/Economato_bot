import pandas as pd
import os

CSV_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "catalogo_unificado.csv")

def inspeccionar(filtro):
    if not os.path.exists(CSV_FILE):
        print("❌ catalogo_unificado.csv no encontrado.")
        return

    try:
        df = pd.read_csv(CSV_FILE)
        # Normalizar para buscar sin mayúsculas
        df['match'] = df['producto_norm'].astype(str).str.lower()
        
        # Filtrar
        resultados = df[df['match'].str.contains(filtro.lower())]
        
        if resultados.empty:
            print(f"❌ No se encontraron productos con '{filtro}'.")
        else:
            print(f"✅ Productos encontrados con '{filtro}':")
            print("-" * 50)
            for _, row in resultados.iterrows():
                print(f"🔹 {row['producto_norm']} | Prov: {row['proveedor']} | {row['precio']}€")
            print("-" * 50)

    except Exception as e:
        print(f"Error leyendo catálogo: {e}")

if __name__ == "__main__":
    inspeccionar("tomat")
