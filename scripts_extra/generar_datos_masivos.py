import pandas as pd
import os
import shutil

# Configuración
OUTPUT_DIR = "proveedores_input"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Datos Base (Diccionarios de productos)
frutas_verduras = [
    {"Item": "Tomate Pera", "Precio": 1.40, "Formato": "kg"},
    {"Item": "Tomate Rama", "Precio": 1.60, "Formato": "kg"},
    {"Item": "Tomate Cherry", "Precio": 2.50, "Formato": "kg"},
    {"Item": "Tomate Ensalada", "Precio": 1.80, "Formato": "kg"},
    {"Item": "Patata Monalisa", "Precio": 0.90, "Formato": "kg"},
    {"Item": "Patata Kennebec", "Precio": 1.10, "Formato": "kg"},
    {"Item": "Patata Roja", "Precio": 1.20, "Formato": "kg"},
    {"Item": "Cebolla Grano", "Precio": 0.60, "Formato": "kg"},
    {"Item": "Cebolla Morada", "Precio": 0.80, "Formato": "kg"},
    {"Item": "Manzana Golden", "Precio": 1.50, "Formato": "kg"},
    {"Item": "Manzana Fuji", "Precio": 1.70, "Formato": "kg"},
    {"Item": "Plátano Canarias", "Precio": 1.90, "Formato": "kg"},
    {"Item": "Naranja Mesa", "Precio": 1.20, "Formato": "kg"},
    {"Item": "Limón Malla", "Precio": 1.50, "Formato": "malla"},
]

lacteos = [
    {"Item": "Leche Entera", "Precio": 0.85, "Formato": "litro"},
    {"Item": "Leche Semidesnatada", "Precio": 0.85, "Formato": "litro"},
    {"Item": "Leche Desnatada", "Precio": 0.85, "Formato": "litro"},
    {"Item": "Leche Soja", "Precio": 1.20, "Formato": "litro"},
    {"Item": "Leche Avena", "Precio": 1.30, "Formato": "litro"},
    {"Item": "Mantequilla Bloque", "Precio": 8.00, "Formato": "kg"},
    {"Item": "Nata Cocina", "Precio": 3.50, "Formato": "litro"},
    {"Item": "Queso Cheddar Lonchas", "Precio": 9.00, "Formato": "kg"},
    {"Item": "Queso Mozzarella Rallado", "Precio": 7.50, "Formato": "kg"},
    {"Item": "Huevo L", "Precio": 0.15, "Formato": "unidad"},
]

carnes = [
    {"Item": "Solomillo Ternera", "Precio": 22.00, "Formato": "kg"},
    {"Item": "Entrecot Vaca", "Precio": 18.00, "Formato": "kg"},
    {"Item": "Pechuga Pollo", "Precio": 6.50, "Formato": "kg"},
    {"Item": "Muslo Pollo", "Precio": 4.50, "Formato": "kg"},
    {"Item": "Solomillo Cerdo", "Precio": 9.00, "Formato": "kg"},
    {"Item": "Lomo Adobado", "Precio": 7.00, "Formato": "kg"},
    {"Item": "Carne Picada Mixta", "Precio": 8.00, "Formato": "kg"},
]

pescados = [
    {"Item": "Salmón Noruego", "Precio": 14.00, "Formato": "kg"},
    {"Item": "Merluza Rodaja", "Precio": 12.00, "Formato": "kg"},
    {"Item": "Bacalao Desalado", "Precio": 16.00, "Formato": "kg"},
    {"Item": "Langostino Cocido", "Precio": 11.00, "Formato": "kg"},
    {"Item": "Sepia Limpia", "Precio": 10.00, "Formato": "kg"},
]

limpieza = [
    {"Item": "Lejía Conejo", "Precio": 0.90, "Formato": "litro"},
    {"Item": "Detergente Ropa", "Precio": 12.00, "Formato": "bidón"},
    {"Item": "Lavavajillas Mano", "Precio": 2.50, "Formato": "litro"},
    {"Item": "Limpiacristales", "Precio": 1.50, "Formato": "spray"},
    {"Item": "Rollo Cocina Ind", "Precio": 4.00, "Formato": "pack"},
    {"Item": "Bolsa Basura 100L", "Precio": 3.00, "Formato": "rollo"},
]

general_cash = []
# General cash tiene un poco de todo, con precios slightly diferent (+- 10%)
import random

def get_varied_price(precio_base):
    # Variar +- 10%
    factor = random.uniform(0.9, 1.1)
    return round(precio_base * factor, 2)

# Populating General Cash with random items from all categories
todos = frutas_verduras + lacteos + carnes + pescados + limpieza
# Tomamos el 60% de los productos para General Cash
subset_general = random.sample(todos, int(len(todos) * 0.6))

for item in subset_general:
    general_cash.append({
        "Item": item["Item"],
        "Precio": get_varied_price(item["Precio"]),
        "Formato": item["Formato"]
    })

# --- Generación de Dataframes ---

def guardar_excel(data, nombre_archivo):
    df = pd.DataFrame(data)
    # Renombrar columnas para asegurar compatibilidad si el script original espera algo específico
    # El script original espera: Item, Precio_Unidad, Formato_Venta
    df.columns = ["Item", "Precio_Unidad", "Formato_Venta"]
    path = os.path.join(OUTPUT_DIR, nombre_archivo)
    df.to_excel(path, index=False)
    print(f"✅ Generado: {path} ({len(df)} items)")

print("--- Generando Datos Masivos ---")

# 1. Frutas Paco (Especialista Frutas) - Precios base
guardar_excel(frutas_verduras, "Frutas_Paco.xlsx")

# 2. Verduras Maria (Especialista Frutas - Competencia)
# Maria tiene precios un poco diferentes y quizás no todo
verduras_maria = []
for item in frutas_verduras:
    if random.choice([True, True, False]): # 66% chance de tenerlo
        verduras_maria.append({
            "Item": item["Item"],
            "Precio": get_varied_price(item["Precio"]),
            "Formato": item["Formato"]
        })
guardar_excel(verduras_maria, "Verduras_Maria.xlsx")

# 3. Lacteos Central
guardar_excel(lacteos, "Lacteos_Central.xlsx")

# 4. Carnes Pepe
guardar_excel(carnes, "Carnes_Pepe.xlsx")

# 5. Pescados Mar
guardar_excel(pescados, "Pescados_Mar.xlsx")

# 6. Limpieza Total
guardar_excel(limpieza, "Limpieza_Total.xlsx")

# 7. General Cash (El que tiene de todo)
guardar_excel(general_cash, "General_Cash.xlsx")

print("\n🚀 Datos de prueba generados exitosamente en 'proveedores_input/'.")
print("👉 Ahora ejecuta: python src/procesador.py  para unificarlos.")
