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