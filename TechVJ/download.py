# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import asyncio
import logging
import re
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, ChannelPrivate, ChatWriteForbidden, PeerIdInvalid, ChannelInvalid, UsernameNotOccupied
from database.db import db
from config import API_ID, API_HASH, MAX_BATCH_SIZE

logger = logging.getLogger(__name__)

# Improved link patterns
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

async def resolve_peer(user_client, chat_username):
    """Resolve peer with better error handling"""
    try:
        if chat_username.startswith('c/'):
            # Private channel with numeric ID
            chat_id = int('-100' + chat_username[2:])
        else:
            # Public username - try to resolve it
            chat_id = chat_username
            
        # Try to get chat info first to resolve the peer
        try:
            chat_info = await user_client.get_chat(chat_id)
            return chat_info.id
        except PeerIdInvalid:
            # If peer is invalid, try to search for it
            if not chat_username.startswith('c/'):
                # For usernames, try to resolve via username
                try:
                    chat_info = await user_client.get_chat(f"@{chat_username}")
                    return chat_info.id
                except:
                    pass
            raise PeerIdInvalid("Channel not accessible")
        
    except Exception as e:
        logger.error(f"Error resolving peer {chat_username}: {e}")
        raise

async def handle_single_download(client, message: Message, session: str, link_match):
    """Handle single post download with improved error handling"""
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
            await status_msg.edit("🔍 **Resolving channel...**")
            
            # Resolve peer first
            try:
                chat_id = await resolve_peer(user_client, chat_username)
                await status_msg.edit("📥 **Fetching content...**")
            except PeerIdInvalid:
                await status_msg.edit(
                    "❌ **Channel not accessible!**\n\n"
                    "**Possible reasons:**\n"
                    "• You haven't joined this channel/group\n"
                    "• Channel is private and you're not a member\n"
                    "• Channel doesn't exist or was deleted\n\n"
                    "**Solution:** Join the channel first, then try again."
                )
                return
            except Exception as e:
                await status_msg.edit(f"❌ **Error accessing channel:** {str(e)}")
                return
            
            # Get the message
            try:
                target_message = await user_client.get_messages(chat_id, message_id)
                
                if not target_message or target_message.empty:
                    await status_msg.edit("❌ **Message not found!** Please check the message ID.")
                    return
                
                await status_msg.edit("📤 **Downloading and sending...**")
                
                # Copy the message
                await target_message.copy(
                    chat_id=message.from_user.id,
                    caption=f"✅ **Downloaded Successfully!**\n\n📱 **From:** {chat_username}\n📧 **Message ID:** {message_id}\n\n💖 **Powered by R-TeleSwiftBot**"
                )
                
                await status_msg.edit("✅ **Download completed successfully!**")
                logger.info(f"Successfully downloaded message {message_id} from {chat_username} for user {message.from_user.id}")
                
            except Exception as e:
                logger.error(f"Error getting message: {e}")
                await status_msg.edit("❌ **Failed to get message!** Message may not exist or be accessible.")
                
        finally:
            try:
                await user_client.disconnect()
            except:
                pass
            
    except Exception as e:
        logger.error(f"Single download error: {e}")
        await message.reply_text("❌ **Download failed!** Please try again.")

async def handle_batch_download(client, message: Message, session: str, batch_match):
    """Handle batch download with improved error handling"""
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
            
            # Resolve peer first
            try:
                chat_id = await resolve_peer(user_client, chat_username)
            except PeerIdInvalid:
                await status_msg.edit(
                    "❌ **Channel not accessible!**\n\n"
                    "Please join the channel first, then try again."
                )
                return
            except Exception as e:
                await status_msg.edit(f"❌ **Error accessing channel:** {str(e)}")
                return
            
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
                    target_message = await user_client.get_messages(chat_id, current_id)
                    
                    if target_message and not target_message.empty:
                        # Copy the message
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
            try:
                await user_client.disconnect()
            except:
                pass
            
    except Exception as e:
        logger.error(f"Batch download error: {e}")
        await message.reply_text("❌ **Batch download failed!** Please try again.")
