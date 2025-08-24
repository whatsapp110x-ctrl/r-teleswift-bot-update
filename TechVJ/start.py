# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db import db
from TechVJ.strings import START_TXT

logger = logging.getLogger(__name__)

@Client.on_message(filters.command("start") & filters.private)
async def start(client, message):
    """Handle start command with updated interface"""
    try:
        user_id = message.from_user.id
        
        # Add user to database
        if not await db.is_user_exist(user_id):
            await db.add_user(user_id, message.from_user.first_name)
        
        await db.update_last_active(user_id)
        
        # UPDATED buttons - Removed Channel, Updated Developer link
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📖 Help", callback_data="help"),
                InlineKeyboardButton("⚡ Features", callback_data="features")
            ],
            [
                InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/fightermonk110")
            ]
        ])
        
        await message.reply_text(
            START_TXT.format(user_mention=message.from_user.mention),
            reply_markup=buttons
        )
        
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await message.reply_text("❌ An error occurred. Please try again later.")
