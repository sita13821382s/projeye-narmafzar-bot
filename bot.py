import logging
import pandas as pd
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    InlineQueryHandler,
    CallbackQueryHandler
)
from uuid import uuid4

# ------------------------- Logging Setup -------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(name)

# ------------------------- Bot Token -------------------------
BOT_TOKEN = " "
# ------------------------- CSV Reading -------------------------
def load_csv(file_path, encoding='utf-8'):
    try:
        df = pd.read_csv(file_path, encoding=encoding)
        return df
    except Exception as err:
        logger.error(f"خطا در خواندن فایل CSV: {err}")
        return pd.DataFrame()

# ------------------------- Command Handlers -------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username or "دوست عزیز"
    welcome_msg = f"سلام {user_name}! خوش اومدی. برای راهنما /help رو بزن."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_msg)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=HELP_TEXT)

# ------------------------- Reviews Processing -------------------------
def fetch_reviews_for_app(df_reviews, app_name, max_reviews=5):
    filtered = df_reviews[df_reviews['App'] == app_name]
    return filtered.head(max_reviews)

def reviews_to_text(df_reviews):
    if df_reviews.empty:
        return "نظری برای این اپلیکیشن یافت نشد."

    parts = []
    for idx, row in enumerate(df_reviews.itertuples(), 1):
        parts.append(f"نظر {idx}:\n{row.Translated_Review}\nاحساسات: {row.Sentiment}\n")

    return "\n".join(parts)

# ------------------------- Callback Query Handler -------------------------
async def handle_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    app = query.data.split(":")[1]
    reviews_path = r"مسیر فایلای خودت برا ریویو ها"
    reviews_df = load_csv(reviews_path)
    app_reviews = fetch_reviews_for_app(reviews_df, app)
    message_text = reviews_to_text(app_reviews)

    await context.bot.send_message(chat_id=query.from_user.id, text=message_text)

# ------------------------- Inline Query Handler -------------------------
async def inline_search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    search_text = update.inline_query.query
    logger.info(f"جستجوی درون خطی: {search_text}")

    if not search_text:
        await context.bot.answer_inline_query(update.inline_query.id, [])
        return

    apps_csv_path = r"مسیر فایلا خودت"
    apps_df = load_csv(apps_csv_path)

    if apps_df.empty:
        logger.error("فایل CSV اپلیکیشن‌ها خالی است.")
        await context.bot.answer_inline_query(update.inline_query.id, [])
        return

    results = []
    matched_apps = apps_df[apps_df['App'].str.contains(search_text, case=False, na=False)]

    if matched_apps.empty:
        await context.bot.answer_inline_query(update.inline_query.id, [])
        return

    for _, app_row in matched_apps.iterrows():
        keyboard = [
            [InlineKeyboardButton("نمایش ۵ نظر", callback_data=f"show_reviews:{app_row['App']}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)