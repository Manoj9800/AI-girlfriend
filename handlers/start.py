from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import Database

db = Database()

NAME, AGE, GENDER = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    if not db.get_user(user.id):
        db.add_user(user.id, user.username, user.first_name)
    keyboard = [[InlineKeyboardButton("💬 Chat", callback_data="menu_chat")],
                [InlineKeyboardButton("🎮 Games", callback_data="menu_games")],
                [InlineKeyboardButton("📱 Social", callback_data="menu_social")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"Hey {user.first_name}! 💖\nI'm Saline. What would you like to do?", reply_markup=reply_markup)
    return ConversationHandler.END

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Nice name 😍! How old are you?")
    return AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['age'] = update.message.text
    keyboard = [
        [InlineKeyboardButton("Boy 👦", callback_data='gender_male')],
        [InlineKeyboardButton("Girl 👧", callback_data='gender_female')]
    ]
    await update.message.reply_text("Gender please?", reply_markup=InlineKeyboardMarkup(keyboard))
    return GENDER

async def get_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    gender = query.data.split('_')[1]
    user_id = query.from_user.id
    db.update_user(user_id, {"gender": gender})
    await query.edit_message_text("All set! 😘 Type anything to start chatting!")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Setup cancelled. You can /start again anytime.")
    return ConversationHandler.END

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💬 Chat with Me", callback_data="menu_chat")],
        [InlineKeyboardButton("🎮 Love Games", callback_data="menu_games")],
        [InlineKeyboardButton("📱 Social Media", callback_data="menu_social")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings")],
        [InlineKeyboardButton("👑 Premium", callback_data="menu_premium")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        await update.callback_query.edit_message_text("What would you like to do today? 💕", reply_markup=reply_markup)
    else:
        await update.message.reply_text("What would you like to do today? 💕", reply_markup=reply_markup)
