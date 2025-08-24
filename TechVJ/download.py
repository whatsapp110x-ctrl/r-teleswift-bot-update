# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import asyncio
import logging
import re
import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, ChatAdminRequired, ChannelPrivate, ChatWriteForbidden
from database.db import db
from config import API_ID, API_HASH, MAX_BATCH_SIZE

logger = logging.getLogger(__name__)

# Link pattern for Telegram URLs
LINK_PATTERN = re.compile(r'https://t\.me/(?:c/)?([^/]+)/(\d+)(?:-(\d+))?')
BATCH_PATTERN = re.compile(r'https://t\.me/(?:c/)?([^/]+)/(\d+)-(\d+)')

@Client.on_message(filters.private & filters.text & ~filters.command(['start', 'help', 'login', 'logout', 'cancel', 'broadcast', 'stats']))
async def handle_link(client, message: Message):
    """Handle Telegram links for download"""
    try:
        user_id = message.from_user.id
        text = message.text.strip()
        
        # Update user activity
        await db.update_last_active(user_id)
        
        # Check if user is logged in
        session = await db.get_session(user_id)
        if not session:
            return await message.reply_text(
                "❌ **You're not logged in!**\n\n"
                "Please use /login command first to authenticate with your Telegram account.\n\n"
                "After logging in, you can send me any Telegram link to download content."
            )
        
        # Validate link format
        if not text.startswith('https://t.me/'):
            return await message.reply_text(
                "❌ **Invalid link format!**\n\n"
                "Please send a valid Telegram link:\n"
                "• `https://t.me/username/123`\n"
                "• `https://t.me/c/123456789/123`\n"
                "• For batch: `https://t.me/username/100-150`"
            )
        
        # Check if it's a batch download
        batch_match = BATCH_PATTERN.match(text)
        if batch_match:
            await handle_batch_download(client, message, session, batch_match)
        else:
            # Single download
            link_match = LINK_PATTERN.match(text)
            if link_match:
                await handle_single_download(client, message, session, link_match)
            else:
                await message.reply_text(
                    "❌ **Invalid Telegram link!**\n\n"
                    "Supported formats:\n"
                    "• `https://t.me/username/123`\n"
                    "• `https://t.me/c/123456789/123`\n"
                    "• For batch: `https://t.me/username/100-150`"
                )
                
    except Exception as e:
        logger.error(f"Error handling link: {e}")
        await message.reply_text("❌ **An error occurred!** Please try again later.")

async def handle_single_download(client, message: Message, session: str, link_match):
    """Handle single post download"""
    try:
        chat_username = link_match.group(1)
        message_id = int(link_match.group(2))
        
        status_msg = await message.reply_text("⬇️ **Processing your request...**")
        
        # Create user client
        user_client = Client(
            ":memory:",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=session
        )
        
        try:
            await user_client.connect()
            await status_msg.edit("🔍 **Fetching content...**")
            
            # Get the message
            try:
                if chat_username.startswith('c/'):
                    # Private channel with ID
                    chat_id = int('-100' + chat_username[2:])
                else:
                    # Public username
                    chat_id = chat_username
                
                target_message = await user_client.get_messages(chat_id, message_id)
                
                if not target_message:
                    await status_msg.edit("❌ **Message not found!**")
                    return
                
                await status_msg.edit("📤 **Downloading and sending...**")
                
                # Forward the message
                await target_message.copy(
                    chat_id=message.from_user.id,
                    caption=f"✅ **Downloaded Successfully!**\n\n📱 **From:** {chat_username}\n📧 **Message ID:** {message_id}\n\n💖 **Powered by R-TeleSwiftBot**"
                )
                
                await status_msg.edit("✅ **Download completed successfully!**")
                
            except ChannelPrivate:
                await status_msg.edit("❌ **Channel is private!** You must join the channel first.")
            except ChatAdminRequired:
                await status_msg.edit("❌ **Admin rights required!** You don't have permission to access this content.")
            except Exception as e:
                logger.error(f"Error getting message: {e}")
                await status_msg.edit("❌ **Failed to access content!** Please check the link and try again.")
                
        finally:
            await user_client.disconnect()
            
    except Exception as e:
        logger.error(f"Single download error: {e}")
        await message.reply_text("❌ **Download failed!** Please try again.")

async def handle_batch_download(client, message: Message, session: str, batch_match):
    """Handle batch download"""
    try:
        chat_username = batch_match.group(1)
        start_id = int(batch_match.group(2))
        end_id = int(batch_match.group(3))
        
        # Validate batch size
        batch_size = end_id - start_id + 1
        if batch_size > MAX_BATCH_SIZE:
            return await message.reply_text(
                f"❌ **Batch too large!**\n\n"
                f"Max batch size: {MAX_BATCH_SIZE}\n"
                f"Your batch size: {batch_size}\n\n"
                f"Please use smaller batches."
            )
        
        if batch_size <= 0:
            return await message.reply_text("❌ **Invalid range!** End ID must be greater than start ID.")
        
        status_msg = await message.reply_text(
            f"📦 **Batch Download Started**\n\n"
            f"📊 **Range:** {start_id} to {end_id}\n"
            f"📈 **Total:** {batch_size} messages\n"
            f"⏳ **Status:** Initializing..."
        )
        
        # Create user client
        user_client = Client(
            ":memory:",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=session
        )
        
        try:
            await user_client.connect()
            
            success_count = 0
            failed_count = 0
            
            for current_id in range(start_id, end_id + 1):
                try:
                    # Update progress every 5 messages
                    if (current_id - start_id) % 5 == 0:
                        progress = ((current_id - start_id + 1) / batch_size) * 100
                        await status_msg.edit(
                            f"📦 **Batch Download in Progress**\n\n"
                            f"📊 **Range:** {start_id} to {end_id}\n"
                            f"📈 **Progress:** {progress:.1f}%\n"
                            f"⚡ **Current:** {current_id}\n"
                            f"✅ **Success:** {success_count}\n"
                            f"❌ **Failed:** {failed_count}"
                        )
                    
                    # Get the message
                    if chat_username.startswith('c/'):
                        chat_id = int('-100' + chat_username[2:])
                    else:
                        chat_id = chat_username
                    
                    target_message = await user_client.get_messages(chat_id, current_id)
                    
                    if target_message and not target_message.empty:
                        # Forward the message
                        await target_message.copy(
                            chat_id=message.from_user.id,
                            caption=f"📦 **Batch Download**\n📧 **ID:** {current_id}/{end_id}\n💖 **R-TeleSwiftBot**"
                        )
                        success_count += 1
                    else:
                        failed_count += 1
                    
                    # Small delay to avoid flood
                    await asyncio.sleep(0.5)
                    
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    continue
                except Exception as e:
                    logger.error(f"Error downloading message {current_id}: {e}")
                    failed_count += 1
                    continue
            
            # Final status
            await status_msg.edit(
                f"✅ **Batch Download Completed!**\n\n"
                f"📊 **Range:** {start_id} to {end_id}\n"
                f"📈 **Total:** {batch_size} messages\n"
                f"✅ **Success:** {success_count}\n"
                f"❌ **Failed:** {failed_count}\n"
                f"📈 **Success Rate:** {(success_count/batch_size)*100:.1f}%\n\n"
                f"💖 **Powered by R-TeleSwiftBot**"
            )
            
        finally:
            await user_client.disconnect()
            
    except Exception as e:
        logger.error(f"Batch download error: {e}")
        await message.reply_text("❌ **Batch download failed!** Please try again.")

@Client.on_message(filters.command("cancel") & filters.private)
async def cancel_operation(client, message):
    """Handle cancel command"""
    try:
        await message.reply_text(
            "🛑 **Operation Cancelled**\n\n"
            "All ongoing operations have been cancelled.\n"
            "You can start a new download anytime!"
        )
    except Exception as e:
        logger.error(f"Cancel command error: {e}")
        await message.reply_text("❌ An error occurred.")
