import pandas as pd
import os

# Create directory if it doesn't exist
os.makedirs('proveedores_input', exist_ok=True)

# Proveedor A Data
data_a = {
    'Producto': ['Tomates', 'Solomillo de Ternera', 'Leche Entera', 'Huevos', 'Patatas'],
    'Coste': [1.50, 25.00, 0.90, 2.10, 0.80],
    'Envase': ['Kg', 'Kg', 'Litro', 'Docena', 'Kg']
}
df_a = pd.DataFrame(data_a)
df_a.to_excel('proveedores_input/Proveedor_A.xlsx', index=False)
print("Created Proveedor_A.xlsx")

# Proveedor B Data (Different structure)
data_b = {
    'Item': ['Tomate Pera', 'Solomillo Vacuno', 'Leche', 'Huevos L', 'Patata Monalisa'],
    'Precio_Unidad': [1.40, 26.50, 0.85, 2.20, 0.75],
    'Formato_Venta': ['Kilogramo', 'Kilogramo', 'L', '12 uds', 'Kilogramo']
}
df_b = pd.DataFrame(data_b)
df_b.to_excel('proveedores_input/Proveedor_B.xlsx', index=False)
print("Created Proveedor_B.xlsx")
