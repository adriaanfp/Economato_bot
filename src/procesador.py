import pandas as pd
import os
from thefuzz import process

def normalize_and_unify():
    # Define column mappings for each supplier
    # This could be more dynamic in a real system, but hardcoded for this task
    mappings = {
        'Proveedor_A.xlsx': {
            'Producto': 'producto',
            'Coste': 'precio',
            'Envase': 'formato'
        },
        'Proveedor_B.xlsx': {
            'Item': 'producto',
            'Precio_Unidad': 'precio',
            'Formato_Venta': 'formato'
        }
    }

    unified_data = []
    input_dir = 'proveedores_input'

    for filename in os.listdir(input_dir):
        if filename.endswith('.xlsx'):
            filepath = os.path.join(input_dir, filename)
            try:
                df = pd.read_excel(filepath)
                
                # Identify supplier based on filename
                if filename in mappings:
                    mapping = mappings[filename]
                    
                    # Rename columns
                    df = df.rename(columns=mapping)
                    
                    # Keep only relevant columns
                    cols_to_keep = ['producto', 'precio', 'formato']
                    # Check if all columns exist
                    if all(col in df.columns for col in cols_to_keep):
                        df = df[cols_to_keep]
                        df['proveedor'] = filename.replace('.xlsx', '')
                        unified_data.append(df)
                    else:
                        print(f"Warning: Missing columns in {filename}. Found: {df.columns}")
                else:
                    print(f"Warning: No mapping found for {filename}")

            except Exception as e:
                print(f"Error processing {filename}: {e}")

    if unified_data:
        final_df = pd.concat(unified_data, ignore_index=True)
        
        # Basic normalization of product names (lowercase)
        final_df['producto_norm'] = final_df['producto'].str.lower().str.strip()
        
        # Sort by price to help with "cheapest price" queries
        final_df = final_df.sort_values(by=['producto_norm', 'precio'])
        
        # Save to CSV
        output_file = 'catalogo_unificado.csv'
        final_df.to_csv(output_file, index=False)
        print(f"Successfully created {output_file}")
        print(final_df)
    else:
        print("No data unified.")

if __name__ == "__main__":
    normalize_and_unify()
