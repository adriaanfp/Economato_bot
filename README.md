# Gestor de Economato Hotelero con Bot de Telegram

Este proyecto es un sistema de gestión de pedidos para un economato hotelero. Permite unificar catálogos de proveedores, buscar el mejor precio para productos y gestionar pedidos a través de un bot de Telegram.

## Estructura del Proyecto

- `src/`: Código fuente del proyecto.
  - `bot_telegram.py`: El bot que interactúa con el usuario. Recibe listas de compra y gestiona favoritos.
  - `buscador.py`: Lógica para buscar productos en el catálogo unificado y determinar el mejor precio (o el proveedor VIP).
  - `gestor_pedidos.py`: Genera la orden final en texto plano.
  - `procesador.py`: Script para normalizar y unificar los Excel de proveedores en un CSV maestro.
- `proveedores_input/`: Carpeta donde se colocan los Excel de los proveedores.
- `preferencias.json`: Almacena las preferencias VIP del usuario (ignorada en git).

## Instalación

1.  Clona el repositorio.
2.  Crea un entorno virtual:
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```
3.  Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```
4.  Configura las variables de entorno (ver sección Seguridad).

## Uso

1.  **Preparar Datos**: Coloca los catálogos `.xlsx` en `proveedores_input/` y ejecuta:
    ```bash
    python src/procesador.py
    ```
2.  **Iniciar Bot**:
    ```bash
    python src/bot_telegram.py
    ```
3.  **Telegram**:
    - `/start`: Inicia la interacción.
    - Escribe tu lista de compra (ej: "Leche, Tomates").
    - `/vip [producto] [proveedor]`: Fuerza un proveedor favorito.
    - `/quitarvip [producto]`: Elimina la preferencia.
    - `/pedir`: Genera la orden final.

## Seguridad

Este proyecto requiere un Token de Telegram.
**NO** subas tu token al repositorio.
Crea un archivo `.env` (basado en `.env.example` si existiera) y añade:
```
TELEGRAM_TOKEN=tu_token_aqui
```
(Nota: La implementación actual lee el token directamente. Se recomienda refactorizar para usar `python-dotenv`).
