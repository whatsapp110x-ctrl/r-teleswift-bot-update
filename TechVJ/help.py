# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import logging
from pyrogram.client import Client
from pyrogram import filters
from database.db import db
from TechVJ.strings import HELP_TXT
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)

@Client.on_message(filters.command("help") & filters.private)
async def help_command(bot, message):
    """Handle help command"""
    try:
        await db.update_last_active(message.from_user.id)
        
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔐 Login Guide", url="https://t.me/VJ_Botz")],
            [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/VJ_Botz"),
             InlineKeyboardButton("📢 Channel", url="https://t.me/Tech_VJ")]
        ])
        
        await message.reply_text(HELP_TXT, reply_markup=buttons)
        
    except Exception as e:
        logger.error(f"Help command error: {e}")
        await message.reply_text("❌ An error occurred. Please try again.")

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
