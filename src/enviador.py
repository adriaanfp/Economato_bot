import smtplib
import json
import os
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from buscador import obtener_datos_mejor_precio
from historial import guardar_pedido_historial

# Cargar variables de entorno (para la contraseña del correo)
load_dotenv()

# --- CONFIGURACIÓN ---
# Si usas Gmail, necesitas una "Contraseña de Aplicación" (ver instrucciones)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = os.getenv("EMAIL_USER")  # Tu correo (ponlo en el .env)
EMAIL_PASSWORD = os.getenv("EMAIL_PASS") # Tu contraseña de aplicación (ponla en el .env)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTACTOS_FILE = os.path.join(BASE_DIR, "contactos.json")

def cargar_contactos():
    if not os.path.exists(CONTACTOS_FILE):
        return {}
    try:
        with open(CONTACTOS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def enviar_correos_pedidos(carrito, dry_run=False):
    """
    Toma el carrito, agrupa por proveedor y envía los correos.
    Si dry_run=True, simula el envío y devuelve el reporte sin conectar al SMTP.
    """
    contactos = cargar_contactos()
    
    # Validar credenciales solo si no es dry_run
    if not dry_run and (not EMAIL_SENDER or not EMAIL_PASSWORD):
        return "❌ Error: Faltan configurar EMAIL_USER o EMAIL_PASS en el archivo .env"

    pedidos_por_proveedor = {}
    
    # 1. Procesar el carrito y agrupar items
    for item_texto in carrito:
        item_texto = item_texto.strip()
        if not item_texto: continue
        
        # Extraer nombre del producto usando Regex
        match = re.search(r"^(.*?)\s*\((.*?)\)$", item_texto)
        if match:
            producto_nombre = match.group(1).strip()
        else:
            producto_nombre = item_texto
        
        datos = obtener_datos_mejor_precio(producto_nombre)
        
        if datos and "proveedor" in datos:
            prov = datos["proveedor"]
            if prov not in pedidos_por_proveedor:
                pedidos_por_proveedor[prov] = []
            
            linea_pedido = f"{item_texto} (Precio aprox: {datos['precio']}€)"
            pedidos_por_proveedor[prov].append(linea_pedido)
        else:
            if "DESCONOCIDO" not in pedidos_por_proveedor:
                pedidos_por_proveedor["DESCONOCIDO"] = []
            pedidos_por_proveedor["DESCONOCIDO"].append(f"{item_texto} - (No encontrado en catálogo)")

    # 2. Enviar correos (o simular)
    reporte = []
    
    try:
        server = None
        if not dry_run:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)

        for proveedor, items in pedidos_por_proveedor.items():
            email_destino = None
            for nombre_contacto, email in contactos.items():
                if nombre_contacto.lower() == proveedor.lower():
                    email_destino = email
                    break
            
            # Preparar contenido
            items_html = "".join([f"<li>{i}</li>" for i in items])
            # (Aquí iría la construcción del HTML completo, simplificado para no repetir código masivo)
            
            if email_destino:
                if dry_run:
                    reporte.append(f"🔌 [SIMULACRO] Enviando a {proveedor} ({email_destino}): {len(items)} items")
                else:
                    msg = MIMEMultipart('alternative')
                    msg['From'] = EMAIL_SENDER
                    msg['To'] = email_destino
                    msg['Subject'] = f"Nuevo Pedido - {proveedor}"
                    
                    text_content = f"Hola {proveedor},\nItems:\n" + "\n".join([f"- {i}" for i in items])
                    msg.attach(MIMEText(text_content, 'plain'))
                    # (Adjuntar HTML si se desea)
                    
                    server.send_message(msg)
                    reporte.append(f"✅ Enviado a {proveedor} ({email_destino})")
            else:
                reporte.append(f"⚠️ {proveedor}: No tengo su email en contactos.json")

        # Guardar historial
        try:
            if not dry_run:
                guardar_pedido_historial(pedidos_por_proveedor)
                reporte.append("💾 Historial de pedidos actualizado.")
            else:
                reporte.append("💾 [SIMULACRO] Historial se actualizaría aquí.")
        except Exception as e_hist:
            reporte.append(f"⚠️ No se pudo guardar el historial: {e_hist}")

        if server:
            server.quit()
            
        return "\n".join(reporte)

    except Exception as e:
        return f"❌ Error enviando correos: {str(e)}"
