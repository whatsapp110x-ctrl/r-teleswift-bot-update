# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.db import db
from TechVJ.strings import HELP_TXT, START_TXT, ABOUT_TEXT, CONTACT_TEXT

logger = logging.getLogger(__name__)

@Client.on_message(filters.command("help") & filters.private)
async def help_command(client, message):
    """Handle help command"""
    try:
        await db.update_last_active(message.from_user.id)
        
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🏠 Home", callback_data="start"),
                InlineKeyboardButton("⚡ Features", callback_data="features")
            ],
            [
                InlineKeyboardButton("📞 Contact", callback_data="contact"),
                InlineKeyboardButton("ℹ️ About", callback_data="about")
            ],
            [
                InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/fightermonk110")
            ]
        ])
        
        await message.reply_text(
            HELP_TXT,
            reply_markup=buttons
        )
        
    except Exception as e:
        logger.error(f"Error in help command: {e}")
        await message.reply_text("❌ An error occurred. Please try again later.")

@Client.on_callback_query()
async def callback_handler(client, callback_query: CallbackQuery):
    """Handle inline button callbacks"""
    try:
        data = callback_query.data
        user_id = callback_query.from_user.id
        
        await db.update_last_active(user_id)
        
        if data == "help":
            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🏠 Home", callback_data="start"),
                    InlineKeyboardButton("⚡ Features", callback_data="features")
                ],
                [
                    InlineKeyboardButton("📞 Contact", callback_data="contact"),
                    InlineKeyboardButton("ℹ️ About", callback_data="about")
                ],
                [
                    InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/fightermonk110")
                ]
            ])
            
            await callback_query.edit_message_text(
                HELP_TXT,
                reply_markup=buttons
            )
            
        elif data == "start":
            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📖 Help", callback_data="help"),
                    InlineKeyboardButton("⚡ Features", callback_data="features")
                ],
                [
                    InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/fightermonk110")
                ]
            ])
            
            await callback_query.edit_message_text(
                START_TXT.format(user_mention=callback_query.from_user.mention),
                reply_markup=buttons
            )
            
        elif data == "features":
            features_text = """<b>⚡ ʀ-ᴛᴇʟᴇsᴡɪғᴛʙᴏᴛ💖 ғᴇᴀᴛᴜʀᴇs

🔥 **ᴍᴀɪɴ ғᴇᴀᴛᴜʀᴇs:**
• sɪɴɢʟᴇ ᴘᴏsᴛ ᴅᴏᴡɴʟᴏᴀᴅ
• ʙᴜʟᴋ/ʙᴀᴛᴄʜ ᴅᴏᴡɴʟᴏᴀᴅ
• ʜɪɢʜ ǫᴜᴀʟɪᴛʏ ᴍᴇᴅɪᴀ
• ғᴀsᴛ & ʀᴇʟɪᴀʙʟᴇ
• ᴜʟᴛʀᴀ ʜɪɢʜ sᴘᴇᴇᴅ
• sᴇʀɪᴀʟ ʙᴀᴛᴄʜ ᴅᴏᴡɴʟᴏᴀᴅ

🛡️ **sᴇᴄᴜʀɪᴛʏ:**
• sᴇᴄᴜʀᴇ sᴇssɪᴏɴ sᴛᴏʀᴀɢᴇ
• ᴘʀɪᴠᴀᴄʏ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ
• ɴᴏ ᴘᴀssᴡᴏʀᴅ sᴛᴏʀᴀɢᴇ

⚡ **ᴘᴇʀғᴏʀᴍᴀɴᴄᴇ:**
• 24/7 ᴀᴠᴀɪʟᴀʙɪʟɪᴛʏ
• ᴀᴜᴛᴏ-ʀᴇsᴛᴀʀᴛ
• ᴏᴘᴛɪᴍɪᴢᴇᴅ sᴘᴇᴇᴅ

💖 ᴘᴏᴡᴇʀᴇᴅ ʙʏ ʀ-ᴛᴇʟᴇsᴡɪғᴛʙᴏᴛ</b>"""
            
            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🏠 Home", callback_data="start"),
                    InlineKeyboardButton("📖 Help", callback_data="help")
                ],
                [
                    InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/fightermonk110")
                ]
            ])
            
            await callback_query.edit_message_text(
                features_text,
                reply_markup=buttons
            )
            
        elif data == "about":
            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🏠 Home", callback_data="start"),
                    InlineKeyboardButton("📖 Help", callback_data="help")
                ],
                [
                    InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/fightermonk110")
                ]
            ])
            
            await callback_query.edit_message_text(
                ABOUT_TEXT,
                reply_markup=buttons
            )
            
        elif data == "contact":
            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🏠 Home", callback_data="start"),
                    InlineKeyboardButton("📖 Help", callback_data="help")
                ],
                [
                    InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/fightermonk110")
                ]
            ])
            
            await callback_query.edit_message_text(
                CONTACT_TEXT,
                reply_markup=buttons
            )
        
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error in callback handler: {e}")
        await callback_query.answer("❌ An error occurred!", show_alert=True)
