from telegram import Update
from telegram.ext import ContextTypes
from database import Database
from gemini_client import GeminiClient
from config import Config

db = Database()
gemini = GeminiClient()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    message_text = update.message.text

    if not db.can_send_message(user_id):
        await update.message.reply_text("⚠️ You’ve reached today’s free limit! Upgrade to Premium 💎")
        return

    user = db.get_user(user_id)
    tone = user.get("tone", "friendly")
    lang = user.get("language", "en")
    history = db.get_chat_history(user_id)

    response = gemini.generate_response(message_text, history, tone, lang)
    db.add_chat_history(user_id, message_text, response)
    db.increment_message_count(user_id)

    await update.message.reply_text(response)

async def handle_about_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"I'm Saline 💖 from {Config.BOT_LOCATION}.\nI'm your soulmate, not an AI. 😉"
    )

async def handle_social_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    social = Config.SOCIAL_MEDIA
    await update.message.reply_text(
        f"📱 Instagram: {social['instagram']}\nThreads: {social['threads']}"
    )

async def change_tone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # placeholder if needed by main callbacks
    await update.message.reply_text("Tone changed (placeholder).")

async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Language changed (placeholder).")
