# 🏨 Gestor de Economato Hotelero Inteligente

> **Sistema de gestión de pedidos automatizado con Bot de Telegram, comparador de precios inteligente y envío de correos.**

Este proyecto moderniza el departamento de compras de un hotel. Permite unificar catálogos de múltiples proveedores, encontrar automáticamente el mejor precio, gestionar la lista de la compra desde un chat y tramitar los pedidos por email con un solo comando.

## ✨ Características Principales

- **🧠 Búsqueda Inteligente ("Portero de Discoteca"):** Distingue entre productos similares (ej: *Leche Entera* vs *Semi*), corrige errores tipográficos y rechaza inputs basura.
- **💰 Comparador Automático:** Selecciona siempre el proveedor más barato para cada producto, salvo que tengas un favorito VIP.
- **📧 Envío de Correos Pro:** Genera y envía emails HTML profesionales a cada proveedor con su parte del pedido.
- **📊 Business Intelligence:** Guarda un historial (`historial_pedidos.xlsx`) con el detalle de compras y una tabla resumen de gastos por proveedor.
- **➕ Agrupación Visual:** Si pides lo mismo varias veces (ej: 5kg y luego 2kg), el sistema lo agrupa visualmente en el pedido final.

## 📂 Estructura del Proyecto

- `src/`: Código fuente.
  - `bot_telegram.py`: El cerebro del bot. Gestiona comandos y flujo de conversación.
  - `buscador.py`: Motor de búsqueda con lógica difusa (*fuzzy logic*) y reglas de desambiguación.
  - `enviador.py`: Gestor de correo SMTP. Genera emails HTML y distribuye pedidos.
  - `gestor_pedidos.py`: Genera los resúmenes de texto y agrupa cantidades.
  - `procesador.py`: Normaliza y unifica cualquier Excel de proveedores en una base de datos maestra (`catalogo_unificado.csv`).
  - `historial.py`: Registra cada pedido en un Excel contable.
- `proveedores_input/`: Carpeta para soltar los catálogos `.xlsx` de los proveedores.
- `scripts_extra/`: Herramientas de utilidad (generación de datos de prueba, tests de integración).
- `archivos de configuración`: `.env` (seguridad), `contactos.json` (emails), `preferencias.json` (favoritos).

## 🚀 Instalación

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/tu-usuario/Economato_bot.git](https://github.com/tu-usuario/Economato_bot.git)
    cd Economato_bot
    ```

2.  **Crear entorno virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuración Segura:**
    * Renombra `.env.example` a `.env` y añade tu **Token de Telegram** y credenciales de **Gmail**.
    * Renombra `contactos.json.example` a `contactos.json` y añade los emails reales de tus proveedores.

## 📖 Uso del Bot

### 1. Preparación de Datos
Coloca los catálogos de tus proveedores (`.xlsx`) en la carpeta `proveedores_input/` y actualiza la base de datos:
```bash
python src/procesador.py
