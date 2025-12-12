import pandas as pd
import os

# Configuración
INPUT_DIR = "proveedores_input"
OUTPUT_DIR = "vistas_txt"

def convertir_excels_a_txt():
    # Crear carpeta de salida si no existe
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"📁 Carpeta creada: {OUTPUT_DIR}/")

    if not os.path.exists(INPUT_DIR):
        print(f"❌ Error: La carpeta '{INPUT_DIR}' no existe.")
        return

    archivos_generados = 0
    print(f"--- Iniciando conversión de Excels a TXT ---")

    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith(".xlsx"):
            input_path = os.path.join(INPUT_DIR, filename)
            
            # Nombre del archivo de salida (mismo nombre pero .txt)
            output_filename = os.path.splitext(filename)[0] + ".txt"
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            
            try:
                # Leer Excel
                df = pd.read_excel(input_path)
                
                # Convertir a string con formato tabla
                contenido = df.to_string(index=False)
                
                # Guardar en archivo de texto
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(contenido)
                
                # print(f"   📄 Generado: {output_filename}")
                archivos_generados += 1
                
            except Exception as e:
                print(f"❌ Error convirtiendo {filename}: {e}")

    print(f"✅ Se han generado {archivos_generados} archivos en la carpeta {OUTPUT_DIR}/")

if __name__ == "__main__":
    convertir_excels_a_txt()
