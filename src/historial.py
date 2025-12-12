import pandas as pd
import os
import re
from datetime import datetime
from openpyxl.styles import Font, PatternFill, Alignment

# Ruta del archivo
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HISTORIAL_FILE = os.path.join(BASE_DIR, "historial_pedidos.xlsx")

def parse_pedido_string(item_str):
    """
    Parsea una cadena de pedido tipo: 'Tomate (5kg) (Precio est: 10.5€)'
    
    Retorna:
        (producto, cantidad, precio_float)
    """
    # Regex para extraer precio
    # Busca "Precio est:" seguido de números y decimales opcionales
    precio_match = re.search(r'Precio est:\s*([\d\.]+)', item_str)
    if precio_match:
        try:
            precio = float(precio_match.group(1))
        except ValueError:
            precio = 0.0
    else:
        precio = 0.0

    # Para nombre y cantidad, asumimos formato "Nombre (Cantidad)"
    # Quitamos la parte del precio para limpiar
    item_clean = re.sub(r'\(Precio est:.*?\)', '', item_str).strip()
    
    # Intentar extraer cantidad entre paréntesis al final
    cantidad_match = re.search(r'\((.*?)\)$', item_clean)
    if cantidad_match:
        cantidad = cantidad_match.group(1)
        producto = item_clean.replace(f"({cantidad})", "").strip()
    else:
        cantidad = "1 unidad" # Default
        producto = item_clean
        
    return producto, cantidad, precio

def generate_summary(df_detalle):
    """
    Genera un DataFrame de resumen agrupado por proveedor.
    """
    summary = df_detalle.groupby("Proveedor")["Precio Total"].sum().reset_index()
    summary.rename(columns={"Precio Total": "Total Gastado"}, inplace=True)
    
    # Calcular Gran Total
    grand_total = summary["Total Gastado"].sum()
    
    # Crear fila de total
    total_row = pd.DataFrame([{"Proveedor": "GRAN TOTAL", "Total Gastado": grand_total}])
    summary = pd.concat([summary, total_row], ignore_index=True)
    
    return summary

def style_excel(writer, df_detalle, df_summary):
    """
    Aplica estilos profesionales al Excel.
    """
    workbook = writer.book
    
    # --- Estilar Hoja Detalle ---
    worksheet = writer.sheets['Detalle']
    
    # Headers en Negrita y Fondo Gris Claro
    header_font = Font(bold=True)
    header_fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")
    
    for cell in worksheet[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")

    # Formato Moneda para columna Precio (Column E -> index 5 si es 1-based, pero mejor buscarla)
    # Pandas escribe columnas en orden. df_detalle cols: Fecha, Prov, Prod, Cant, Precio
    precio_col_idx = df_detalle.columns.get_loc("Precio Total") + 1
    
    for row in worksheet.iter_rows(min_row=2, min_col=precio_col_idx, max_col=precio_col_idx):
        for cell in row:
            cell.number_format = '#,##0.00€'

    # Auto-ajustar ancho columnas
    for column_cells in worksheet.columns:
        length = max(len(str(cell.value) or "") for cell in column_cells)
        worksheet.column_dimensions[column_cells[0].column_letter].width = length + 2

    # --- Estilar Hoja Resumen ---
    worksheet_sum = writer.sheets['Resumen_Gastos']
    
    for cell in worksheet_sum[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")

    # Formato Moneda Columna 2 (Total)
    total_col_idx = df_summary.columns.get_loc("Total Gastado") + 1
    for row in worksheet_sum.iter_rows(min_row=2, min_col=total_col_idx, max_col=total_col_idx):
        for cell in row:
            cell.number_format = '#,##0.00€'
            
    # Resaltar fila Gran Total (última)
    last_row = worksheet_sum.max_row
    for cell in worksheet_sum[last_row]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="000000", end_color="000000", fill_type="solid")

    for column_cells in worksheet_sum.columns:
        length = max(len(str(cell.value) or "") for cell in column_cells)
        worksheet_sum.column_dimensions[column_cells[0].column_letter].width = length + 2


def guardar_pedido_historial(pedidos_por_proveedor):
    """
    Procesa, guarda y regenera el Excel con dos pestañas.
    """
    filas_nuevas = []
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Procesar nuevos datos
    for proveedor, items in pedidos_por_proveedor.items():
        for item_str in items:
            prod, cant, precio = parse_pedido_string(item_str)
            filas_nuevas.append({
                "Fecha": fecha_actual,
                "Proveedor": proveedor,
                "Producto": prod,
                "Cantidad": cant,
                "Precio Total": precio
            })
            
    if not filas_nuevas:
        print("⚠ No hay nuevos pedidos para guardar.")
        return

    df_nuevos = pd.DataFrame(filas_nuevas)

    # 2. Cargar datos existentes si los hay
    if os.path.exists(HISTORIAL_FILE):
        try:
            # Leemos solo la hoja Detalle para acumular
            df_existente = pd.read_excel(HISTORIAL_FILE, sheet_name='Detalle')
            df_final = pd.concat([df_existente, df_nuevos], ignore_index=True)
        except Exception:
            # Si falla (ej: archivo corrupto o formato viejo), empezamos de cero o hacemos backup
            # Por simplicidad, asumimos nuevo si falla.
            print("⚠ Archivo existente no compatible o corrupto. Creando nuevo.")
            df_final = df_nuevos
    else:
        df_final = df_nuevos

    # 3. Generar Resumen
    df_resumen = generate_summary(df_final)

    # 4. Guardar con estilos
    try:
        # Usamos engine='openpyxl' explícitamente
        with pd.ExcelWriter(HISTORIAL_FILE, engine='openpyxl') as writer:
            df_final.to_excel(writer, sheet_name='Detalle', index=False)
            df_resumen.to_excel(writer, sheet_name='Resumen_Gastos', index=False)
            
            # Aplicar estilos
            style_excel(writer, df_final, df_resumen)
            
        print(f"✅ Historial y Resumen actualizados en: {HISTORIAL_FILE}")
        
    except Exception as e:
        print(f"❌ Error crítico al escribir Excel: {e}")
