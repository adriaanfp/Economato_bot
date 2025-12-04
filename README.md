# Hotel Commissary Manager with Telegram Bot

> 🚧 **Work in Progress (WIP)**: This project is currently under active development. Features are subject to change, and optimizations are ongoing.

This project is an order management system designed for a hotel commissary (*economato*). It allows users to unify supplier catalogs, automatically search for the best product prices, and manage orders seamlessly through a Telegram bot.

## Project Structure

- `src/`: Source code directory.
  - `bot_telegram.py`: The main bot interface. It receives shopping lists and manages user favorites.
  - `buscador.py`: Logic to search products within the unified catalog and determine the best price (or select the VIP supplier).
  - `gestor_pedidos.py`: Generates the final order in plain text format.
  - `procesador.py`: Script to normalize and unify different supplier Excel files into a master CSV.
- `proveedores_input/`: Directory to place supplier Excel catalogs (`.xlsx`).
- `preferencias.json`: Stores user VIP preferences (ignored by git).

## Installation

1.  Clone the repository.
2.  Create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Configure environment variables (see **Security** section).

## Usage

1.  **Prepare Data**: Place your supplier catalogs (`.xlsx` files) inside the `proveedores_input/` folder and run:
    ```bash
    python src/procesador.py
    ```
2.  **Start the Bot**:
    ```bash
    python src/bot_telegram.py
    ```
3.  **Telegram Commands**:
    - `/start`: Starts the interaction.
    - **Shopping List**: Simply type your items (e.g., "Milk, Tomatoes").
    - `/vip [product] [supplier]`: Forces a specific supplier for a product (overrides price logic).
    - `/quitarvip [product]`: Removes the preference (reverts to best price).
    - `/pedir`: Generates the final order text file.

## Security

This project requires a Telegram Bot Token.
**DO NOT** upload your token to the repository.

1. Create a `.env` file in the root directory (you can use `.env.example` as a reference).
2. Add your token inside:
   ```ini
   TELEGRAM_TOKEN=your_token_here