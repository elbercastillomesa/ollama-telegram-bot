import logging
import os
import requests
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Cargar variables
load_dotenv()
LLM_MODEL = os.getenv("LLM_MODEL")
TOKEN = os.getenv("TELEGRAM_BOT_API_KEY")
OLLAMA_URL = "http://localhost:11434/api/generate"

# Configuración de logs
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Definimos el único estado que necesitamos
CHAT = range(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Inicia la conversación y activa el modo chat."""
    reply_markup = ReplyKeyboardMarkup([['Done']], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        f"¡Hola! Soy tu Odroid C2 con {LLM_MODEL}. \nEnvíame cualquier mensaje y te responderé. \nEscribe 'Done' o pulsa el botón para terminar.",
        reply_markup=reply_markup
    )
    return CHAT

async def chat_with_ollama(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Envía el texto directamente a Ollama y devuelve la respuesta."""
    user_text = update.message.text
    
    # Notificar que estamos procesando (importante en la Odroid C2)
    await update.message.reply_chat_action("typing")
    
    logger.info(f"Enviando a Ollama: {user_text}")
    
    try:
        payload = {
            "model": LLM_MODEL,
            "prompt": user_text,
            "system": "You are a helpful AI assistant. Keep your answers very short, concise, and direct to the point. Avoid long explanations.",
            "stream": False,
            "options": {
                "num_predict": 200,
                "temperature": 0.7
            }
        }
        
        # Timeout largo porque la Odroid C2 es lenta procesando
        response = requests.post(OLLAMA_URL, json=payload, timeout=360)
        
        if response.status_code == 200:
            answer = response.json().get('response', 'No recibí respuesta.')
            await update.message.reply_text(answer)
        else:
            await update.message.reply_text(f"Error de Ollama: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("Me costó procesar eso. ¿Podemos intentar otra vez?")

    return CHAT

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Termina la conversación."""
    await update.message.reply_text(
        "Adiós. Aquí estaré cuando me necesites.", 
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHAT: [
                # Filtramos 'Done' para que no se envíe al modelo
                MessageHandler(filters.TEXT & ~filters.Regex("^Done$"), chat_with_ollama)
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), stop)],
    )

    application.add_handler(conv_handler)
    
    print("Bot en marcha... Presiona Ctrl+C para detener.")
    application.run_polling()

if __name__ == "__main__":
    main()