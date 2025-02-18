from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext
from PIL import Image, ImageDraw, ImageFont
import random
from datetime import datetime
import asyncio
from threading import Thread
import os

# Evitar problemas con Werkzeug en Vercel
os.environ["WERKZEUG_RUN_MAIN"] = "true"

app = Flask(__name__)

# Enlace de tu grupo público de Telegram
GRUPO_TELEGRAM = "@Nequifrontxchat"

# Tu token del bot
TOKEN = "7889044431:AAG3izjUjO5e9vwGu0XatE_-oC51_ApTtVc"

# Estados del flujo
TIPO_TRANSFERENCIA, NOMBRE_DESTINATARIO, NUMERO_DESTINATARIO, NUMERO_REMITENTE, MONTO, MENSAJE = range(6)

# Diccionario para almacenar datos temporales
user_data = {}

# Inicializamos el bot de Telegram
application = Application.builder().token(TOKEN).build()

async def start(update: Update, context: CallbackContext):
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

@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data(as_text=True)
    update = Update.de_json(json_str, application.bot)
    asyncio.run(application.process_update(update))
    return "OK", 200

def run():
    app.run(host="0.0.0.0", port=8080)

async def main():
    # Configurar Webhook en Vercel con tu dominio
    webhook_url = "https://botdaviplataa.vercel.app/webhook"
    await application.bot.set_webhook(webhook_url)

    # Definir handlers del bot
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            TIPO_TRANSFERENCIA: [MessageHandler(filters.TEXT & ~filters.COMMAND, start)], 
        },
        fallbacks=[CommandHandler("cancel", cancelar)],
    )

    application.add_handler(conversation_handler)

if __name__ == "__main__":
    # Iniciar Flask en un hilo aparte para mantener el servidor activo
    Thread(target=run).start()
    
    # Ejecutar la lógica del bot
    asyncio.run(main())
