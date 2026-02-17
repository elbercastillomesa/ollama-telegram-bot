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

# Load environment variables
load_dotenv()
LLM_MODEL = os.getenv("LLM_MODEL")
TOKEN = os.getenv("TELEGRAM_BOT_API_KEY")
OLLAMA_URL = "http://localhost:11434/api/generate"

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Conversation state
CHAT = range(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start chat and clear previous memory."""
    context.user_data["ollama_context"] = [] # Clear memory at startup
    
    reply_markup = ReplyKeyboardMarkup([['Done']], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        f"Memory activated. I'm your assistant on Odroid C2.\nModel: {LLM_MODEL}\n\nHow can I help you?",
        reply_markup=reply_markup
    )
    return CHAT

async def chat_with_ollama(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_text = update.message.text
    await update.message.reply_chat_action("typing")
    
    # Retrieve the context (the "memory") stored in the user session
    history = context.user_data.get("ollama_context", [])

    try:
        payload = {
            "model": LLM_MODEL,
            "prompt": user_text,
            "system": "You are an AI assistant. Your responses MUST be very short and direct. Maximum 2 sentences.",
            "context": history, # Send the context numbers from the previous response
            "stream": False,
            "options": {
                "num_predict": 250, # Force short response to save RAM
                "temperature": 0.7
            }
        }
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=300)
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get('response', 'I have no response.')
            
            # SAVE the new context for the next question
            context.user_data["ollama_context"] = data.get("context")
            
            await update.message.reply_text(answer)
        else:
            await update.message.reply_text(f"Error {response.status_code} in Ollama.")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("Memory or connection error. Try with something shorter.")

    return CHAT

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End and clear session data."""
    context.user_data.clear() 
    await update.message.reply_text("History cleared. Goodbye!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHAT: [MessageHandler(filters.TEXT & ~filters.Regex("^Done$"), chat_with_ollama)],
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), stop)],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()