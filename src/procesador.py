import pandas as pd
import os
import re

def normalize_and_unify():
    unified_data = []
    input_dir = 'proveedores_input'

    # Keywords para detección de columnas
    KEYWORDS = {
        'producto': ['producto', 'item', 'nombre', 'articulo', 'description', 'descripción'],
        'precio': ['precio', 'price', 'pvp', 'coste', 'valor'],
        'formato': ['formato', 'unidad', 'venta', 'envase', 'unit']
    }

    print("--- Iniciando Procesamiento Universal de Catálogos ---")

    for filename in os.listdir(input_dir):
        if filename.endswith('.xlsx'):
            filepath = os.path.join(input_dir, filename)
            try:
                # Leer sin header específico primero para ver qué hay, pero pandas suele acertar con header=0
                df = pd.read_excel(filepath)
                
                # Normalizar nombres de columnas para facilitar búsqueda
                # (lowercase y strip)
                original_cols = df.columns.tolist()
                cols_map = {}
                used_cols = set()
                
                # Definir orden de prioridad para evitar que una columna sirva para dos cosas
                # Ej: Precio_Unidad -> debe ser PRECIO, no formato (por la palabra Unidad)
                targets_ordered = ['producto', 'precio', 'formato']

                for target in targets_ordered:
                    keys = KEYWORDS[target]
                    for col in original_cols:
                        if col in used_cols:
                            continue
                        
                        col_lower = str(col).lower().strip()
                        if any(k in col_lower for k in keys):
                            cols_map[target] = col
                            used_cols.add(col)
                            break # Encontramos la columna para este target, pasamos al siguiente target


                
                # Verificar si tenemos lo mínimo: producto y precio
                if 'producto' in cols_map and 'precio' in cols_map:
                    # Renombrar
                    rename_dict = {cols_map['producto']: 'producto', cols_map['precio']: 'precio'}
                    if 'formato' in cols_map:
                        rename_dict[cols_map['formato']] = 'formato'
                    
                    df = df.rename(columns=rename_dict)
                    
                    # Asegurar columna formato si falta
                    if 'formato' not in df.columns:
                        df['formato'] = '1 unidad'
                        print(f"⚠️ {filename}: No se detectó columna 'formato'. Asignado '1 unidad' por defecto.")
                    
                    # Seleccionar solo las columnas finales
                    df = df[['producto', 'precio', 'formato']].copy()
                    
                    # Añadir proveedor (nombre del archivo sin extensión)
                    df['proveedor'] = os.path.splitext(filename)[0]
                    
                    unified_data.append(df)
                    print(f"✅ Procesado: {filename} (Cols: {list(rename_dict.values())})")
                else:
                    print(f"❌ Saltado: {filename} - No se detectaron columnas de Producto o Precio. (Detectado: {cols_map})")

            except Exception as e:
                print(f"❌ Error procesando {filename}: {e}")

    if unified_data:
        final_df = pd.concat(unified_data, ignore_index=True)
        
        # Limpieza básica
        final_df['producto_norm'] = final_df['producto'].astype(str).str.lower().str.strip()
        final_df['precio'] = pd.to_numeric(final_df['precio'], errors='coerce')
        final_df = final_df.dropna(subset=['precio'])
        
        # Ordenar
        final_df = final_df.sort_values(by=['producto_norm', 'precio'])
        
        # Guardar
        output_file = 'catalogo_unificado.csv'
        final_df.to_csv(output_file, index=False)
        print(f"\n🎉 Catálogo unificado generado exitosamente: {output_file}")
        print(f"Total productos: {len(final_df)}")
    else:
        print("⚠️ No se pudo unificar ningún dato.")

if __name__ == "__main__":
    normalize_and_unify()
