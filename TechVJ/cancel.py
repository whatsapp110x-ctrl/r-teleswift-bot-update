# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

from pyrogram import Client, filters
import logging

logger = logging.getLogger(__name__)

@Client.on_message(filters.command("cancel") & filters.private)
async def cancel_command(client, message):
    """Handle cancel command"""
    try:
        await message.reply_text(
            "🛑 **Operation Cancelled**\n\n"
            "All ongoing operations have been cancelled.\n"
            "You can start fresh anytime!\n\n"
            "💡 **Available commands:**\n"
            "• /start - Main menu\n"
            "• /help - Get help\n"
            "• /login - Login with your account\n"
            "• /logout - Logout from bot"
        )
    except Exception as e:
        logger.error(f"Cancel command error: {e}")
        await message.reply_text("❌ An error occurred.")
