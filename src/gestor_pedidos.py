from buscador import obtener_datos_mejor_precio
import re


def parsear_linea_pedido(linea):
    linea = linea.strip()
    if not linea:
        return None
    
    producto = ""
    cantidad_str = ""
    cantidad_val = 0.0

    # 1. Intentar formato "Producto (Cantidad)"
    match_parenthesis = re.search(r"^(.*?)\s*\((.*?)\)$", linea)
    if match_parenthesis:
        producto = match_parenthesis.group(1).strip()
        cantidad_str = match_parenthesis.group(2).strip()
    else:
        # Fallback: lógica antigua (coma o primer número)
        partes = linea.split(',')
        if len(partes) >= 2:
            producto = partes[0].strip()
            cantidad_str = partes[1].strip()
        else:
            match_num = re.search(r"(\d+)", linea)
            if match_num:
                idx = match_num.start()
                producto = linea[:idx].strip()
                cantidad_str = linea[idx:].strip()
            else:
                producto = linea
                cantidad_str = "1" # Default si no hay cantidad
    
    # Calcular valor numérico para el precio
    match_val = re.search(r"(\d+(\.\d+)?)", cantidad_str)
    if match_val:
        cantidad_val = float(match_val.group(1))
        # Normalización básica
        c_lower = cantidad_str.lower()
        if re.search(r"(gramos|gr|g\b|g\s)", c_lower) and "kg" not in c_lower:
             cantidad_val = cantidad_val / 1000.0
    else:
        cantidad_val = 1.0

    return {
        "item": producto,
        "cantidad_str": cantidad_str, 
        "cantidad_val": cantidad_val
    }

def generar_pedido(lista_lineas):
    # Reiniciar el archivo de salida
    with open("ORDEN_FINAL.txt", "w", encoding="utf-8") as f:
        f.write("")

    lista_items = []
    for linea in lista_lineas:
        item = parsear_linea_pedido(linea)
        if item:
            lista_items.append(item)
    
    if lista_items:
        procesar_lista_compra(lista_items)
    else:
        print("No se encontraron items válidos para procesar.")

def procesar_lista_compra(lista_items):
    # Diccionario para agrupar: proveedor -> { nombre_producto_real -> { 'cantidades': [], 'precio_u': 0, 'subtotal': 0, 'es_fav': bool } }
    agrupado = {}
    
    for item_data in lista_items:
        item_buscado = item_data["item"]
        cant_str = item_data["cantidad_str"]
        cant_val = item_data["cantidad_val"]
        
        datos = obtener_datos_mejor_precio(item_buscado)
        
        if datos and "error" not in datos:
            proveedor = datos["proveedor"]
            precio_unitario = datos["precio"]
            nombre_real = datos["producto"]
            es_favorito = datos.get("es_favorito", False)
            coste_item = precio_unitario * cant_val
            
            if proveedor not in agrupado:
                agrupado[proveedor] = {}
            
            if nombre_real not in agrupado[proveedor]:
                agrupado[proveedor][nombre_real] = {
                    "cantidades": [],
                    "precio_u": precio_unitario,
                    "subtotal": 0.0,
                    "es_fav": es_favorito
                }
            
            agrupado[proveedor][nombre_real]["cantidades"].append(cant_str)
            agrupado[proveedor][nombre_real]["subtotal"] += coste_item
            # Mantener flag de favorito si alguno lo es (aunque deberían ser todos iguales por producto)
            if es_favorito: 
                agrupado[proveedor][nombre_real]["es_fav"] = True
                
        else:
            print(f"Advertencia: No se encontró producto para '{item_buscado}'")

    # Generar archivo de salida
    with open("ORDEN_FINAL.txt", "w", encoding="utf-8") as f:
        f.write("=== ORDEN DE COMPRA AGRUPADA ===\n\n")
        
        total_global = 0.0
        
        for proveedor, productos in agrupado.items():
            f.write(f"=== {proveedor} ===\n")
            total_proveedor = 0.0
            
            for nombre_prod, info in productos.items():
                # Formatear cantidades: "5kg + 2kg"
                cantidades_visibles = " + ".join(info["cantidades"])
                subtotal = info["subtotal"]
                precio = info["precio_u"]
                marca = " ⭐" if info["es_fav"] else ""
                
                linea = f"- {nombre_prod}{marca}: {cantidades_visibles} (x {precio}€/ud = {subtotal:.2f}€)\n"
                f.write(linea)
                total_proveedor += subtotal
            
            f.write(f"Total Proveedor: {total_proveedor:.2f}€\n\n")
            total_global += total_proveedor
            
    print(f"Orden generada en ORDEN_FINAL.txt. Total global: {total_global:.2f}€")

if __name__ == "__main__":
    archivo_compra = "lista_compra.txt"
    print(f"Leyendo lista de compra de '{archivo_compra}'...")
    lista_compra = leer_archivo_compra(archivo_compra)
    
    if lista_compra:
        procesar_lista_compra(lista_compra)
    else:
        print("No se encontraron items para procesar.")
