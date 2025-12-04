from buscador import obtener_datos_mejor_precio
import re


def parsear_linea_pedido(linea):
    linea = linea.strip()
    if not linea:
        return None
    partes = linea.split(',')
    if len(partes) >= 2:
        producto = partes[0].strip()
        cantidad_str = partes[1].strip()
    else:
        # Si no hay coma, intentar separar por el primer número encontrado
        match_num = re.search(r"(\d+)", linea)
        if match_num:
            idx = match_num.start()
            producto = linea[:idx].strip()
            cantidad_str = linea[idx:].strip()
        else:
            print(f"Advertencia: No se detectó estructura válida en '{linea}'")
            return None
        
        # Extraer número usando regex
        match = re.search(r"(\d+(\.\d+)?)", cantidad_str)
        if match:
            cantidad = float(match.group(1))
            
            # Normalización de unidades
            cantidad_lower = cantidad_str.lower()
            
            # Primero descartar kilogramos explícitos para evitar coincidencia con 'g'
            if "kg" in cantidad_lower or "kilo" in cantidad_lower:
                pass # Ya está en la unidad correcta (o asumimos Kg)
            elif re.search(r"(gramos|gr|g\b|g\s)", cantidad_lower):
                    cantidad = cantidad / 1000.0
            
            return {"item": producto, "cantidad": cantidad}
        else:
                print(f"Advertencia: No se encontró cantidad válida en '{linea}'")
    return None

def leer_archivo_compra(nombre_archivo):
    lista_items = []
    try:
        with open(nombre_archivo, 'r', encoding='utf-8') as f:
            for linea in f:
                item = parsear_linea_pedido(linea)
                if item:
                    lista_items.append(item)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{nombre_archivo}'")
    return lista_items

def generar_pedido(lista_lineas):
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
    ordenes_por_proveedor = {}
    
    for item_data in lista_items:
        item_buscado = item_data["item"]
        cantidad = item_data["cantidad"]
        
        datos = obtener_datos_mejor_precio(item_buscado)
        
        if datos and "error" not in datos:
            proveedor = datos["proveedor"]
            precio_unitario = datos["precio"]
            nombre_producto = datos["producto"]
            es_favorito = datos.get("es_favorito", False)
            subtotal = precio_unitario * cantidad
            
            if proveedor not in ordenes_por_proveedor:
                ordenes_por_proveedor[proveedor] = {
                    "items": [],
                    "total": 0.0
                }
            
            ordenes_por_proveedor[proveedor]["items"].append({
                "producto": nombre_producto,
                "cantidad": cantidad,
                "precio_unitario": precio_unitario,
                "subtotal": subtotal,
                "es_favorito": es_favorito
            })
            ordenes_por_proveedor[proveedor]["total"] += subtotal
        else:
            print(f"Advertencia: No se encontró producto para '{item_buscado}'")

    # Generar archivo de salida
    with open("ORDEN_FINAL.txt", "w", encoding="utf-8") as f:
        for proveedor, data in ordenes_por_proveedor.items():
            f.write(f"=== {proveedor} ===\n")
            for item in data["items"]:
                marca_favorito = " ⭐" if item.get("es_favorito") else ""
                f.write(f"- {item['producto']}{marca_favorito}: {item['cantidad']} un. x {item['precio_unitario']}€ = {item['subtotal']:.1f}€\n")
            f.write(f"Total Proveedor: {data['total']:.1f}€\n\n")
            
    print("Orden generada en ORDEN_FINAL.txt")

if __name__ == "__main__":
    archivo_compra = "lista_compra.txt"
    print(f"Leyendo lista de compra de '{archivo_compra}'...")
    lista_compra = leer_archivo_compra(archivo_compra)
    
    if lista_compra:
        procesar_lista_compra(lista_compra)
    else:
        print("No se encontraron items para procesar.")
