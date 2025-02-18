from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext
from PIL import Image, ImageDraw, ImageFont
import random
from datetime import datetime

app = Flask(__name__)

# Enlace de tu grupo público de Telegram
GRUPO_TELEGRAM = "@Nequifrontxchat"

# Tu token del bot
TOKEN = "7889044431:AAG3izjUjO5e9vwGu0XatE_-oC51_ApTtVc"

# Estados del flujo
TIPO_TRANSFERENCIA, NOMBRE_DESTINATARIO, NUMERO_DESTINATARIO, NUMERO_REMITENTE, MONTO, MENSAJE = range(6)

# Diccionario para almacenar datos temporales
user_data = {}

# Función para verificar si el usuario está en el grupo de Telegram
async def verificar_membresia(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    try:
        chat_member = await context.bot.get_chat_member(GRUPO_TELEGRAM, user_id)
        if chat_member.status not in ['member', 'administrator', 'creator']:
            await update.message.reply_text(
                "Debes unirte al grupo de Telegram para usar este bot. "
                "Por favor, entra aquí: https://t.me/Nequifrontxchat"
            )
            return False
    except Exception:
        await update.message.reply_text("No se pudo verificar tu membresía. Asegúrate de que el bot tenga permisos.")
        return False
    return True

# Función para generar el comprobante
def generar_comprobante(nombre_destinatario, destinatario, remitente, monto, mensaje=None):
    try:
        plantilla = Image.open("plantilla.png")
        draw = ImageDraw.Draw(plantilla)
    except Exception as e:
        print(f"Error al cargar la plantilla: {e}")
        return None

    font_path = "/storage/emulated/0/Download/FiraSans-Regular.otf"
    try:
        font_pequeno = ImageFont.truetype(font_path, 26)
        font_valor = ImageFont.truetype(font_path, 36)
        font_mensaje = ImageFont.truetype(font_path, 28)
    except Exception as e:
        print(f"Error al cargar la fuente: {e}")
        return None

    posiciones = {
        "nombre_destinatario": (85, 621),
        "destinatario": (84, 644),
        "monto": (85, 789),
        "remitente": (77, 915),
        "fecha": (82, 1089),
        "aprobacion": (83, 1172),
        "mensaje": (80.5, 1012.2),
    }

    fecha_actual = datetime.now().strftime("%d/%m/%Y - %I:%M %p")
    numero_aprobacion = str(random.randint(100000, 999999))
    destinatario_formateado = f"*****{destinatario[-4:]}"
    desde_texto = f"Daviplata - ****{remitente[-4:]}"

    try:
        draw.text(posiciones["nombre_destinatario"], nombre_destinatario, font=font_pequeno, fill="black")
        draw.text(posiciones["destinatario"], destinatario_formateado, font=font_pequeno, fill="black")
        draw.text(posiciones["monto"], f"${monto}", font=font_valor, fill="black")
        draw.text(posiciones["remitente"], desde_texto, font=font_pequeno, fill="black")
        draw.text(posiciones["fecha"], fecha_actual, font=font_pequeno, fill="black")
        draw.text(posiciones["aprobacion"], numero_aprobacion, font=font_pequeno, fill="black")

        if mensaje:
            draw.text(posiciones["mensaje"], mensaje, font=font_mensaje, fill="black")

    except Exception as e:
        print(f"Error al escribir en la imagen: {e}")
        return None

    output_path = "comprobante_generado.png"
    try:
        plantilla.save(output_path)
        return output_path
    except Exception as e:
        print(f"Error al guardar la imagen: {e}")
        return None

# Función para iniciar el bot
async def start(update: Update, context: CallbackContext):
    if not await verificar_membresia(update, context):
        return

    await update.message.reply_text(
        "Hola, bienvenido a DAVIFRONTX\n"
        "Puedes generar un comprobante falso similar al de DAVIPLATA real.\n\n"
        "Selecciona el tipo de transferencia:\n"
        "📌1: Transferencia Normal Daviplata\n"
        "📌2: Daviplata Transfiya\n\n"
        "⚒️ BOT CREADO POR @Frontman87"
    )
    return TIPO_TRANSFERENCIA

async def cancelar(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "🚫 **OPERACIÓN CANCELADA** 🚫\n\n"
        "GRACIAS POR USAR NUESTROS SERVICIOS, VUELVA PRONTO 👋🏻\n\n"
        "Si quieres generar otro comprobante, presiona /start.",
        parse_mode="Markdown"
    )
    return ConversationHandler.END

async def seleccionar_transferencia(update: Update, context: CallbackContext):
    texto = update.message.text.lower()
    if texto in ["1", "transferencia normal daviplata"]:
        user_data[update.message.from_user.id] = {"tipo_transferencia": "normal"}
    elif texto in ["2", "daviplata transfiya"]:
        user_data[update.message.from_user.id] = {"tipo_transferencia": "transfiya"}
    else:
        await update.message.reply_text("Opción no válida. Selecciona 1 o 2.")
        return TIPO_TRANSFERENCIA

    await update.message.reply_text("Ingresa el nombre del destinatario.")
    return NOMBRE_DESTINATARIO

# Define la ruta para manejar las solicitudes de Webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data(as_text=True)
    update = Update.de_json(json_str, application.bot)
    application.process_update(update)
    return "OK", 200

def main():
    application = Application.builder().token(TOKEN).build()

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            TIPO_TRANSFERENCIA: [MessageHandler(filters.TEXT & ~filters.COMMAND, seleccionar_transferencia)],
            NOMBRE_DESTINATARIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, obtener_nombre_destinatario)],
            NUMERO_DESTINATARIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, obtener_numero_destinatario)],
            NUMERO_REMITENTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, obtener_numero_remitente)],
            MONTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, obtener_monto)],
            MENSAJE: [MessageHandler(filters.TEXT & ~filters.COMMAND, obtener_mensaje)],
        },
        fallbacks=[CommandHandler("cancel", cancelar)],
    )

    application.add_handler(conversation_handler)
    application.run_polling()

if __name__ == "__main__":
    main()