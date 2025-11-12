import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, CallbackQueryHandler, ConversationHandler
)
from config import Config
from database import Database
from gemini_client import GeminiClient

# Handlers (imported from handlers package)
from handlers.start import start, get_name, get_age, get_gender, cancel, show_main_menu, NAME, AGE, GENDER
from handlers.chat import handle_message, handle_about_me, handle_social_media, change_tone, change_language
from handlers.games import show_games_menu, start_love_quiz, handle_quiz_answer, love_meter

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

db = Database()
gemini = GeminiClient()

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    try:
        if data == 'menu_main':
            await show_main_menu_from_query(query, context)
        elif data == 'menu_chat':
            await query.edit_message_text("💬 Let's chat! Just send me a message and I'll respond! 😊")
        elif data == 'menu_games':
            await show_games_menu_from_query(query, context)
        elif data == 'menu_social':
            await handle_social_media_from_query(query, context)
        elif data == 'menu_settings':
            await show_settings_menu(query, context)
        elif data == 'menu_premium':
            await show_premium_menu(query, context)
        elif data == 'game_quiz':
            await start_love_quiz(update, context)
        elif data.startswith('quiz_answer_'):
            await handle_quiz_answer(update, context)
        elif data == 'game_lovemeter':
            await love_meter(update, context)
        elif data.startswith('setting_tone_'):
            tone = data.split('_')[-1]
            await change_tone_from_query(query, context, tone)
        elif data.startswith('setting_lang_'):
            language = data.split('_')[-1]
            await change_language_from_query(query, context, language)
        elif data == 'premium_upgrade':
            await show_premium_payment(query, context)
        elif data == 'refer_friend':
            await show_referral_info(query, context)
    except Exception as e:
        logger.error(f"Error in callback handler: {e}")
        await query.edit_message_text("Sorry, something went wrong! 😔\nPlease try again.")

async def show_main_menu_from_query(query, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💬 Chat with Me", callback_data="menu_chat")],
        [InlineKeyboardButton("🎮 Love Games", callback_data="menu_games")],
        [InlineKeyboardButton("📱 Social Media", callback_data="menu_social")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings")],
        [InlineKeyboardButton("👑 Premium", callback_data="menu_premium")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("What would you like to do today? 💕", reply_markup=reply_markup)

async def show_games_menu_from_query(query, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💝 Love Quiz", callback_data="game_quiz")],
        [InlineKeyboardButton("💑 Compatibility Test", callback_data="game_compatibility")],
        [InlineKeyboardButton("💌 Love Meter", callback_data="game_lovemeter")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🎮 Choose a love game to play! 💕", reply_markup=reply_markup)

async def handle_social_media_from_query(query, context: ContextTypes.DEFAULT_TYPE):
    text = f"""📱 Connect with me on social media! 💖

Threads: {Config.SOCIAL_MEDIA['threads']}
Instagram: {Config.SOCIAL_MEDIA['instagram']}

Follow me for more updates and cute content! 😊"""
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="menu_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

async def show_settings_menu(query, context: ContextTypes.DEFAULT_TYPE):
    user_id = query.from_user.id
    user = db.get_user(user_id)
    current_tone = user.get('tone', 'friendly') if user else 'friendly'
    current_language = user.get('language', 'en') if user else 'en'
    tone_names = {'flirting': 'Flirting 💕','bold': 'Bold 💪','love_guru': 'Love Guru 🧠','friendly': 'Friendly 😊'}
    language_names = {'en': 'English 🇺🇸','hi': 'Hindi 🇮🇳','hi-en': 'Hinglish 🌐','bn': 'Bengali 🇧🇩'}
    keyboard = [
        [InlineKeyboardButton(f"🎭 Tone: {tone_names.get(current_tone, current_tone)}", callback_data="setting_tone")],
        [InlineKeyboardButton(f"🌐 Language: {language_names.get(current_language, current_language)}", callback_data="setting_lang")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"""
⚙️ Settings

Current Settings:
• Conversation Tone: {tone_names.get(current_tone, current_tone)}
• Language: {language_names.get(current_language, current_language)}

Choose a setting to change:
    """
    await query.edit_message_text(text, reply_markup=reply_markup)

async def show_tone_settings(query, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Flirting 💕", callback_data="setting_tone_flirting")],
        [InlineKeyboardButton("Bold 💪", callback_data="setting_tone_bold")],
        [InlineKeyboardButton("Love Guru 🧠", callback_data="setting_tone_love_guru")],
        [InlineKeyboardButton("Friendly 😊", callback_data="setting_tone_friendly")],
        [InlineKeyboardButton("🔙 Back to Settings", callback_data="menu_settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Choose your preferred conversation tone: 🎭", reply_markup=reply_markup)

async def show_language_settings(query, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("English 🇺🇸", callback_data="setting_lang_en")],
        [InlineKeyboardButton("Hindi 🇮🇳", callback_data="setting_lang_hi")],
        [InlineKeyboardButton("Hinglish 🌐", callback_data="setting_lang_hi-en")],
        [InlineKeyboardButton("Bengali 🇧🇩", callback_data="setting_lang_bn")],
        [InlineKeyboardButton("🔙 Back to Settings", callback_data="menu_settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Choose your preferred language: 🌐", reply_markup=reply_markup)

async def change_tone_from_query(query, context: ContextTypes.DEFAULT_TYPE, tone: str):
    user_id = query.from_user.id
    db.update_user(user_id, {'tone': tone})
    tone_names = {'flirting': 'Flirting','bold': 'Bold','love_guru': 'Love Guru','friendly': 'Friendly'}
    await query.edit_message_text(f"✅ Conversation tone set to: {tone_names.get(tone, tone)}! 😊")
    await show_settings_menu(query, context)

async def change_language_from_query(query, context: ContextTypes.DEFAULT_TYPE, language: str):
    user_id = query.from_user.id
    db.update_user(user_id, {'language': language})
    language_names = {'en': 'English','hi': 'Hindi','hi-en': 'Hinglish','bn': 'Bengali'}
    await query.edit_message_text(f"✅ Language set to: {language_names.get(language, language)}! 😊")
    await show_settings_menu(query, context)

async def show_premium_menu(query, context: ContextTypes.DEFAULT_TYPE):
    user_id = query.from_user.id
    user = db.get_user(user_id)
    text = f"""👑 Premium Features

💎 What you get:
• Unlimited messages every day
• Priority responses
• Exclusive love games
• Advanced relationship insights
• Ad-free experience

💰 Price: ₹{Config.PREMIUM_PRICE}/month

🎁 Referral Program:
• Refer friends and get {Config.REFERRAL_POINTS} free messages each
• Both you and your friend benefit!

Your current status: {'PREMIUM 🎉' if user.get('is_premium') else 'FREE'}
Referral points: {user.get('referral_points', 0) if user else 0}
    """
    keyboard = [
        [InlineKeyboardButton("⭐ Upgrade Now", callback_data="premium_upgrade")],
        [InlineKeyboardButton("📤 Refer a Friend", callback_data="refer_friend")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

async def show_premium_payment(query, context: ContextTypes.DEFAULT_TYPE):
    text = f"""💳 Upgrade to Premium

To upgrade to premium, please send {Config.PREMIUM_PRICE} Telegram Stars to this bot.

Steps:
1. Click on the attachment icon (📎) next to the message input
2. Select "Telegram Stars"
3. Send {Config.PREMIUM_PRICE} Stars
4. Your premium status will be activated automatically!

For any issues, contact support.

Thank you for your support! 💖
    """
    keyboard = [
        [InlineKeyboardButton("🔙 Back", callback_data="menu_premium")],
        [InlineKeyboardButton("🆘 Contact Support", url="https://t.me/your_support")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

async def show_referral_info(query, context: ContextTypes.DEFAULT_TYPE):
    user_id = query.from_user.id
    user = db.get_user(user_id)
    referral_code = user.get('referral_code', f"REF{user_id}") if user else f"REF{user_id}"
    referral_link = f"https://t.me/{context.bot.username}?start={referral_code}"
    text = f"""📤 Referral Program

Invite your friends and both of you get {Config.REFERRAL_POINTS} free messages! 🎁

Your referral link:
{referral_link}

Share this link with your friends:
• When they join using your link
• And complete registration
• Both of you get {Config.REFERRAL_POINTS} free messages!

Your referral points: {user.get('referral_points', 0) if user else 0}
    """
    keyboard = [
        [InlineKeyboardButton("📋 Copy Link", callback_data="copy_link")],
        [InlineKeyboardButton("🔙 Back", callback_data="menu_premium")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error(msg="Exception while handling an update:", exc_info=context.error)
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "Sorry, I encountered an error! 😔\nPlease try again or contact support if the problem continues."
            )
    except Exception as e:
        logging.error(f"Error in error handler: {e}")

def main():
    application = Application.builder().token(Config.BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            GENDER: [CallbackQueryHandler(get_gender, pattern='^gender_')]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(handle_callback_query))

    application.add_handler(MessageHandler(
        filters.TEXT & (
            filters.Regex(r'(?i)(name|who are you|about you)') |
            filters.Regex(r'(?i)(ai|artificial|robot)') |
            filters.Regex(r'(?i)(where|from|location)')
        ), handle_about_me
    ))

    application.add_handler(MessageHandler(
        filters.TEXT & (
            filters.Regex(r'(?i)(image|photo|picture|video|social|instagram|threads)')
        ), handle_social_media
    ))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.add_error_handler(error_handler)

    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
