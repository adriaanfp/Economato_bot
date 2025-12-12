import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from buscador import obtener_datos_mejor_precio
from gestor_pedidos import generar_pedido
from enviador import enviar_correos_pedidos

def test_sistema():
    print("🚀 Iniciando Test Completo del Sistema...\n")

    # 1. Simular Carrito (Casos difíciles)
    carrito = [
        "Tomate Pera (5kg)",
        "Leche Entera (10 Litros)",
        "ProductoInexistente (1ud)",
        "Huevos L (3 docenas)"
    ]
    print(f"🛒 Carrito Simulado: {carrito}\n")

    # 2. Prueba del Buscador
    print("🔍 [TEST] Buscador de Precios:")
    for item in carrito:
        # Extraer nombre simple para el buscador (simulando lo que hace el enviador)
        import re
        match = re.search(r"^(.*?)\s*\((.*?)\)$", item)
        nombre = match.group(1).strip() if match else item
        
        datos = obtener_datos_mejor_precio(nombre)
        
        if datos and "proveedor" in datos:
            print(f"   ✅ '{item}' -> Detectado: '{datos['producto']}' | Prov: {datos['proveedor']} (OK)")
        else:
            print(f"   ❌ '{item}' -> No encontrado (Esperado para items falsos)")

    print("\n📦 [TEST] Generador de Pedidos:")
    # 3. Prueba del Agrupador
    generar_pedido(carrito)
    
    # Leer resultado
    try:
        with open("ORDEN_FINAL.txt", "r", encoding="utf-8") as f:
            contenido = f.read()
            print("   📄 Contenido de ORDEN_FINAL.txt:")
            print("-" * 40)
            print(contenido.strip())
            print("-" * 40)
    except Exception as e:
        print(f"   ❌ Error leyendo orden: {e}")

    print("\n📧 [TEST] Simulacro de Envío (Dry Run):")
    # 4. Simulacro de Envío
    reporte = enviar_correos_pedidos(carrito, dry_run=True)
    print(reporte)

    print("\n✅ Test completado.")

if __name__ == "__main__":
    test_sistema()
