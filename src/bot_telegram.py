import logging
import json
import os
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from gestor_pedidos import generar_pedido
from enviador import enviar_correos_pedidos
from buscador import buscar_coincidencias

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "8379807849:AAGWftYM3kCi0EELxfMXSGG4ki0e8pp8LEE"
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

def extraer_cantidad(texto):
    """
    Extrae la cantidad (número + unidad opcional) del texto.
    Devuelve (cantidad_encontrada, producto_limpio).
    Ej: "Tomate 6 kg" -> ("6 kg", "Tomate")
    """
    # Regex para buscar número al final o número + unidad
    # Unidades comunes: kg, g, l, ml, unidades, uds, etc.
    # Soporta decimales con punto o coma
    patron = r"(\d+(?:[.,]\d+)?)\s*(kg|kilos|l|litros|unidades|u|g|gramos|ml|cl|uds|cajas|botes|botellas)?$"
    
    match = re.search(patron, texto, re.IGNORECASE)
    if match:
        cantidad_completa = match.group(0).strip()
        # Eliminar la cantidad del texto original
        producto_limpio = texto[:match.start()].strip()
        return cantidad_completa, producto_limpio
    
    return None, texto

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="¡Hola Chef! 👨‍🍳\nEmpieza a escribir los ingredientes que necesitas (ej: 'Leche, 50 L').\nPuedes escribir varios separados por comas o saltos de línea.\n\nComandos VIP:\n/vip [producto] [proveedor] - Forzar un proveedor\n/quitarvip [producto] - Volver al más barato\n\n⚠️ IMPORTANTE:\n3. Usa /carrito para revisar tu lista (verás números).\n5. Usa /borrar [nº] para quitar algo de la lista.\n6. Usa /vaciar para borrar todo y empezar de cero."
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
    # Normalizar separadores
    texto_normalizado = texto.replace('\n', ',')
    items = [item.strip() for item in texto_normalizado.split(',') if item.strip()]
    
    if not items:
        return

    # Procesar cada item con la nueva lógica
    respuestas = []
    
    for item in items:
        cantidad_str, item_limpio = extraer_cantidad(item)
        
        # Si no se extrajo cantidad, item_limpio es igual a item
        # Buscamos usando el nombre limpio
        tipo_match, resultado = buscar_coincidencias(item_limpio)
        
        if tipo_match == "exact":
            # Coincidencia > 90% -> Añadir directo
            # Si había cantidad, la pegamos al nombre real
            item_final = f"{resultado} ({cantidad_str})" if cantidad_str else resultado
            
            carrito.append(item_final)
            respuestas.append(f"✅ Añadido: {item_final}")
            
        elif tipo_match == "ambiguous":
            # Coincidencia 60-89% -> Preguntar
            # Aquí mostramos las opciones tal cual salen del catálogo
            opciones_str = ", ".join(resultado)
            respuestas.append(f"🤔 ¿Qué quisiste decir con '{item_limpio}'? Opciones: {opciones_str}")
            
        else: # no_match (< 60%)
            respuestas.append(f"❌ No encuentro nada parecido a '{item}' en el catálogo.")
    
    # Enviar todas las respuestas unidas
    full_response = "\n".join(respuestas)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=full_response
    )

async def ver_carrito(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global carrito
    if not carrito:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="El carrito está vacío. Añade items antes de ver el resumen."
        )
        return

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Generando resumen provisional... ⏳"
    )

    try:
        # Generar el archivo ORDEN_FINAL.txt usando el gestor (para previsualizar)
        generar_pedido(carrito)

        # Leer el archivo generado
        with open("ORDEN_FINAL.txt", "r", encoding="utf-8") as f:
            contenido = f.read()

        # Crear lista numerada para mostrar
        lista_numerada = "\n".join([f"{i+1}. {item}" for i, item in enumerate(carrito)])

        # Enviar contenido al chat
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"🛒 **Tu Lista de Compra:**\n{lista_numerada}\n\n📝 **Resumen Agrupado:**\n{contenido}\n\n📝 Si todo está bien, usa /enviar para cursar los pedidos.\n❌ Para borrar algo: /borrar [número]"
        )
        
        # YA NO Vaciamos carrito aquí
        # carrito = [] 

    except Exception as e:
        logging.error(f"Error al generar resumen: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Ocurrió un error al generar el resumen."
        )

    except Exception as e:
        logging.error(f"Error al generar pedido: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Ocurrió un error al generar el resumen."
        )

async def borrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global carrito
    if not context.args:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Debes indicar el número del artículo a borrar. Ejemplo: /borrar 1"
        )
        return

    try:
        indice = int(context.args[0]) - 1
        if 0 <= indice < len(carrito):
            item_eliminado = carrito.pop(indice)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"🗑️ Eliminado: {item_eliminado}"
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"❌ El número {indice + 1} no es válido. Revisa la lista con /carrito."
            )
    except ValueError:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Por favor, introduce un número válido."
        )

async def vaciar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global carrito
    carrito = []
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🗑️ Carrito vaciado por completo. Puedes empezar de cero."
    )

async def enviar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global carrito
    if not carrito:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ El carrito está vacío. No hay nada que enviar."
        )
        return

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Enviando correos a proveedores... ✉️"
    )

    # Llamar a la función de envío
    reporte = enviar_correos_pedidos(carrito)

    # Responder con el reporte
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"📧 **Reporte de Envío:**\n\n{reporte}"
    )

    # Si todo sale bien (o parcialmente bien), vaciamos el carrito
    # Solo si hay algún check verde
    if "✅" in reporte:
        carrito = []
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🗑️ Carrito vaciado tras el envío exitoso."
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ El carrito NO se ha vaciado porque hubo errores en el envío. Revisa y vuelve a intentar."
        )

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    carrito_handler = CommandHandler('carrito', ver_carrito)
    enviar_handler = CommandHandler('enviar', enviar)
    vip_handler = CommandHandler('vip', vip)
    quitarvip_handler = CommandHandler('quitarvip', quitarvip)
    borrar_handler = CommandHandler('borrar', borrar)
    vaciar_handler = CommandHandler('vaciar', vaciar)
    
    # Filtramos mensajes de texto que NO sean comandos
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    
    application.add_handler(start_handler)
    application.add_handler(carrito_handler)
    application.add_handler(enviar_handler)
    application.add_handler(vip_handler)
    application.add_handler(quitarvip_handler)
    application.add_handler(borrar_handler)
    application.add_handler(vaciar_handler)
    application.add_handler(message_handler)
    
    print("Bot iniciado...")
    application.run_polling()
