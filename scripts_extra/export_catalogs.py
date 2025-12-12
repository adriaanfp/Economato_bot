import pandas as pd

try:
    df_a = pd.read_excel('proveedores_input/Proveedor_A.xlsx')
    with open('catalogo_proveedor_a.txt', 'w') as f:
        f.write(df_a.to_string(index=False))
    print("Created catalogo_proveedor_a.txt")

    df_b = pd.read_excel('proveedores_input/Proveedor_B.xlsx')
    with open('catalogo_proveedor_b.txt', 'w') as f:
        f.write(df_b.to_string(index=False))
    print("Created catalogo_proveedor_b.txt")

except Exception as e:
    print(f"Error: {e}")
