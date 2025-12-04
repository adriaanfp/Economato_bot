import logging
import json
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from gestor_pedidos import generar_pedido

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("❌ Error: No se encontró la variable TELEGRAM_TOKEN en el archivo .env")

PREFERENCIAS_FILE = "preferencias.json"

# Carrito global
carrito = []

def load_preferences():
    if not os.path.exists(PREFERENCIAS_FILE):
        return {}
    try:
        with open(PREFERENCIAS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error cargando preferencias: {e}")
        return {}

def save_preferences(data):
    try:
        with open(PREFERENCIAS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Error guardando preferencias: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="¡Hola Chef! 👨‍🍳\nEmpieza a escribir los ingredientes que necesitas (ej: 'Leche, 50 L').\nPuedes escribir varios separados por comas o saltos de línea.\n\nComandos VIP:\n/vip [producto] [proveedor] - Forzar un proveedor\n/quitarvip [producto] - Volver al más barato\n\n⚠️ IMPORTANTE: Cuando termines, envía /pedir en un mensaje NUEVO y SEPARADO para generar la orden."
    )

async def vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 2:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Uso incorrecto. Ejemplo: /vip Tomate Proveedor_A"
        )
        return

    proveedor = context.args[-1]
    producto = " ".join(context.args[:-1]).lower()
    
    prefs = load_preferences()
    prefs[producto] = proveedor
    save_preferences(prefs)
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"⭐ Guardado: '{producto}' se comprará siempre a '{proveedor}'."
    )

async def quitarvip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Uso incorrecto. Ejemplo: /quitarvip Tomate"
        )
        return

    producto = " ".join(context.args).lower()
    
    prefs = load_preferences()
    if producto in prefs:
        del prefs[producto]
        save_preferences(prefs)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"🗑️ VIP eliminado. Ahora '{producto}' se comprará al mejor precio disponible."
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"⚠️ No tenía guardado ningún favorito para '{producto}'."
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    # Normalizar separadores: reemplazar saltos de línea por comas
    texto_normalizado = texto.replace('\n', ',')
    # Dividir por comas y limpiar
    items = [item.strip() for item in texto_normalizado.split(',') if item.strip()]
    
    if items:
        carrito.extend(items)
        
        lista_items_msg = "\n".join([f"- {item}" for item in items])
        msg = f"✅ He añadido {len(items)} cosas:\n{lista_items_msg}"
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=msg
        )

async def pedir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global carrito
    if not carrito:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="El carrito está vacío. Añade items antes de pedir."
        )
        return

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Generando pedido... ⏳"
    )

    try:
        # Generar el archivo ORDEN_FINAL.txt usando el gestor
        generar_pedido(carrito)

        # Leer el archivo generado
        with open("ORDEN_FINAL.txt", "r", encoding="utf-8") as f:
            contenido = f.read()

        # Enviar contenido al chat
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"📝 **Orden Generada:**\n\n{contenido}"
        )
        
        # Vaciar carrito
        carrito = []
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="✅ Pedido completado y carrito vaciado."
        )

    except Exception as e:
        logging.error(f"Error al generar pedido: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Ocurrió un error al generar el pedido."
        )

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    pedir_handler = CommandHandler('pedir', pedir)
    vip_handler = CommandHandler('vip', vip)
    quitarvip_handler = CommandHandler('quitarvip', quitarvip)
    
    # Filtramos mensajes de texto que NO sean comandos
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    
    application.add_handler(start_handler)
    application.add_handler(pedir_handler)
    application.add_handler(vip_handler)
    application.add_handler(quitarvip_handler)
    application.add_handler(message_handler)
    
    print("Bot iniciado...")
    application.run_polling()
