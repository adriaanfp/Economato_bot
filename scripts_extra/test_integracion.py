import sys
import os
import re

# Add src to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from buscador import obtener_datos_mejor_precio
from gestor_pedidos import generar_pedido
from enviador import enviar_correos_pedidos

def test_integracion():
    print("🚀 Iniciando Test de Integración con Datos Masivos...\n")

    # 1. Definir Escenario (Carrito variado)
    carrito = [
        "Manzana Golden (5kg)",    # Frutas Paco
        "Manzana Golden (2kg)",    # Repetido (debe agrupar)
        "Lejía Conejo (3 litros)", # Limpieza Total
        "Salmón Noruego (1 pieza)",# Pescados Mar
        "Solomillo Ternera (2kg)", # Carnes Pepe
        "Unicornio (1ud)"          # Inexistente
    ]
    print(f"🛒 Carrito Simulado: {carrito}\n")

    # Fase 1: Buscador
    print("🔍 [FASE 1] Buscador de Precios:")
    for item in carrito:
        # Limpieza simple de nombre para el buscador (simulando lógica de enviador)
        match = re.search(r"^(.*?)\s*\((.*?)\)$", item)
        nombre = match.group(1).strip() if match else item
        
        datos = obtener_datos_mejor_precio(nombre)
        
        if datos and "proveedor" in datos:
            print(f"   ✅ '{item}' -> '{datos['producto']}' | Prov: {datos['proveedor']} | Precio: {datos['precio']}€")
        else:
            print(f"   ❌ '{item}' -> No encontrado (Correcto si es 'Unicornio')")

    print("\n📦 [FASE 2] Gestor de Pedidos (Agrupación):")
    generar_pedido(carrito)
    
    # Verificación visual del contenido
    try:
        with open("ORDEN_FINAL.txt", "r", encoding="utf-8") as f:
            contenido = f.read()
            print("   📄 Contenido de ORDEN_FINAL.txt:")
            print("-" * 40)
            print(contenido.strip())
            print("-" * 40)
            
            if "5kg + 2kg" in contenido or "2kg + 5kg" in contenido:
                print("   ✅ Agrupación visual detectada (Manzanas sumadas).")
            else:
                print("   ⚠️ Advertencia: No se detectó la agrupación visual esperada.")

    except Exception as e:
        print(f"   ❌ Error leyendo orden: {e}")

    print("\n📧 [FASE 3] Enviador (Simulacro):")
    print("   Enviando correos en modo Dry-Run...")
    # Nota: Usamos dry_run=True como definimos en enviador.py
    reporte = enviar_correos_pedidos(carrito, dry_run=True)
    print(reporte)

    print("\n✅ Test de Integración completado.")

if __name__ == "__main__":
    test_integracion()
