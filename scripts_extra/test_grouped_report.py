import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from gestor_pedidos import generar_pedido

# Simular lista de pedidos desde el bot
lista_simulada = [
    "Tomates (5kg)",
    "Leche (2 litros)",
    "Tomates (3 cajas)",       # Mismo producto, diferente cantidad
    "Leche Entera (1 pack)"    # Producto diferente similar
]

print("Generando pedido simulado...")
generar_pedido(lista_simulada)

print("\n--- Contenido de ORDEN_FINAL.txt ---")
try:
    with open("ORDEN_FINAL.txt", "r", encoding="utf-8") as f:
        print(f.read())
except Exception as e:
    print(e)
