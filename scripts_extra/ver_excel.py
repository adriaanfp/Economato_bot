import pandas as pd
import os

FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "historial_pedidos.xlsx")

def main():
    if os.path.exists(FILE_PATH):
        try:
            df = pd.read_excel(FILE_PATH)
            if df.empty:
                print(f"ℹ️  El archivo {FILE_PATH} está vacío.")
            else:
                print(f"📋 Contenido de {FILE_PATH}:\n")
                print(df.to_string())
                print(f"\nTotal de filas: {len(df)}")
        except Exception as e:
            print(f"❌ Error al leer el archivo: {e}")
    else:
        print(f"⚠️  El archivo {FILE_PATH} no existe aún.")

if __name__ == "__main__":
    main()
