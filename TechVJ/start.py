# Don't Remove Credit Tg - @VJ_Botz  
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import asyncio 
import logging
import time
from pyrogram.client import Client
from pyrogram import filters
from pyrogram.errors import (
    FloodWait, UserIsBlocked, InputUserDeactivated, AuthKeyUnregistered, 
    SessionExpired, SessionRevoked, ChannelPrivate, UserNotParticipant,
    PeerIdInvalid, MessageIdInvalid, ChannelInvalid, UsernameInvalid,
    UsernameNotOccupied
)
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message 
from config import (
    API_ID, API_HASH, ERROR_MESSAGE, MAX_BATCH_SIZE, PROGRESS_UPDATE_INTERVAL, 
    MAX_FILE_SIZE, DOWNLOAD_CHUNK_SIZE, MAX_CONCURRENT_DOWNLOADS, CONNECTION_TIMEOUT,
    MAX_RETRIES, RETRY_DELAY, SLEEP_THRESHOLD, ADMINS
)
from database.db import db
from TechVJ.strings import HELP_TXT, START_TXT, ERROR_MESSAGES
from datetime import datetime

logger = logging.getLogger(__name__)

def is_valid_telegram_post_link(text):
    """Validate if text is a valid Telegram post link"""
    try:
        text = text.strip()
        if not text.startswith('https://t.me/'):
            return False
        
        parts = text.split('/')
        if len(parts) < 5:
            return False
        
        # Handle different formats
        if parts[3] == 'c' and len(parts) >= 6:
            try:
                int(parts[4])
                int(parts[5].split('-')[0])
                return True
            except (ValueError, IndexError):
                return False
        elif parts[3] == 'b' and len(parts) >= 6:
            try:
                int(parts[5].split('-')[0])
                return True
            except (ValueError, IndexError):
                return False
        else:
            try:
                # Username format
                username = parts[3]
                int(parts[4].split('-')[0])
                return True
            except (ValueError, IndexError):
                return False
    except Exception:
        return False

def parse_telegram_link(url):
    """Parse Telegram link and return chat info and message ID"""
    try:
        parts = url.split('/')
        
        if parts[3] == 'c':
            # Private channel: https://t.me/c/123456789/123
            chat_id = int('-100' + parts[4])
            msg_part = parts[5]
        elif parts[3] == 'b':
            # Bot link: https://t.me/b/123456789_abc/123
            chat_id = int('-100' + parts[4].split('_')[0])
            msg_part = parts[5]
        else:
            # Public channel/group: https://t.me/username/123
            chat_id = parts[3]  # Username
            msg_part = parts[4]
        
        # Handle range or single message
        if '-' in msg_part:
            start_id, end_id = msg_part.split('-')
            return chat_id, int(start_id), int(end_id)
        else:
            msg_id = int(msg_part)
            return chat_id, msg_id, None
            
    except (ValueError, IndexError) as e:
        logger.error(f"Error parsing link {url}: {e}")
        return None, None, None

class SerialBatchManager:
    """Enhanced serial batch download manager with proper cancellation"""
    USER_TASKS = {}
    CANCEL_FLAGS = {}
    PROGRESS_MESSAGES = {}  # Store progress messages for cancellation updates
    
    @classmethod
    def start_batch(cls, user_id, task_info):
        """Start a batch task for user"""
        cls.USER_TASKS[user_id] = task_info
        cls.CANCEL_FLAGS[user_id] = False
    
    @classmethod
    def set_progress_message(cls, user_id, message):
        """Store progress message for cancellation updates"""
        cls.PROGRESS_MESSAGES[user_id] = message
    
    @classmethod
    def get_progress_message(cls, user_id):
        """Get stored progress message"""
        return cls.PROGRESS_MESSAGES.get(user_id)
    
    @classmethod
    def is_active(cls, user_id):
        """Check if user has active batch"""
        return user_id in cls.USER_TASKS
    
    @classmethod
    async def cancel_batch(cls, user_id):
        """Cancel user's batch download and update UI"""
        cls.CANCEL_FLAGS[user_id] = True
        
        # Update progress message to show cancellation
        progress_msg = cls.PROGRESS_MESSAGES.get(user_id)
        if progress_msg:
            try:
                await progress_msg.edit(
                    "🛑 **Your Current Process Terminated Due To User Request ⚠️❌**\n\n"
                    "💖 **R-TeleSwiftBot💖**\n"
                    "Process cancelled successfully!"
                )
            except Exception as e:
                logger.error(f"Error updating cancellation message: {e}")
        
        # Clean up
        if user_id in cls.USER_TASKS:
            del cls.USER_TASKS[user_id]
        if user_id in cls.PROGRESS_MESSAGES:
            del cls.PROGRESS_MESSAGES[user_id]
    
    @classmethod
    def is_cancelled(cls, user_id):
        """Check if batch is cancelled"""
        return cls.CANCEL_FLAGS.get(user_id, False)
    
    @classmethod
    def clear_batch(cls, user_id):
        """Clear batch task"""
        if user_id in cls.USER_TASKS:
            del cls.USER_TASKS[user_id]
        if user_id in cls.PROGRESS_MESSAGES:
            del cls.PROGRESS_MESSAGES[user_id]
        cls.CANCEL_FLAGS[user_id] = False

async def safe_delete_file(file_path):
    """Safely delete a file"""
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"Deleted file: {file_path}")
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {e}")

async def validate_session(session_string):
    """Validate if session is still active"""
    try:
        test_client = Client(
            ":memory:", 
            session_string=session_string, 
            api_id=API_ID, 
            api_hash=API_HASH,
            sleep_threshold=SLEEP_THRESHOLD
        )
        await asyncio.wait_for(test_client.connect(), timeout=15.0)
        await asyncio.wait_for(test_client.get_me(), timeout=10.0)
        await test_client.disconnect()
        return True
    except (AuthKeyUnregistered, SessionExpired, SessionRevoked):
        return False
    except Exception as e:
        logger.error(f"Session validation error: {e}")
        return False

async def create_client_with_retry(user_data, max_retries=2):
    """Create and connect client with optimized settings for ultra-high speed"""
    if not user_data:
        raise Exception("No session data provided")
    
    # First validate the session
    if not await validate_session(user_data):
        raise Exception("Session expired or invalid - please /logout and /login again")
    
    for attempt in range(max_retries):
        try:
            acc = Client(
                f":memory:{attempt}_{int(time.time())}", 
                session_string=user_data, 
                api_hash=API_HASH, 
                api_id=API_ID,
                sleep_threshold=5,  # Ultra-fast response
                max_concurrent_transmissions=20,  # Maximum speed
                takeout=False,
                device_model="R-TeleSwiftBot💖",
                system_version="Ultra High Speed 2.0"
            )
            await asyncio.wait_for(acc.connect(), timeout=10.0)
            
            # Test connection
            await asyncio.wait_for(acc.get_me(), timeout=8.0)
            return acc
            
        except (AuthKeyUnregistered, SessionExpired, SessionRevoked):
            raise Exception("Session expired - please /logout and /login again")
        except Exception as e:
            logger.warning(f"Client connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
            else:
                raise Exception(f"Failed to connect: {str(e)[:100]}")

# Enhanced progress tracking
progress_data = {}

def create_progress_bar(percentage):
    """Create an enhanced visual progress bar"""
    filled = int(percentage // 5)  # 20 blocks for 100%
    bar = "🟩" * filled + "⬜" * (20 - filled)
    return bar

async def progress(current, total, message, type_op, start_time=None):
    """Ultra-enhanced progress callback with cancellation handling"""
    try:
        # Get user ID from message
        user_id = message.chat.id
        
        # Check if cancelled and handle immediately
        if SerialBatchManager.is_cancelled(user_id):
            try:
                await message.edit(
                    "🛑 **Your Current Process Terminated Due To User Request ⚠️❌**\n\n"
                    "💖 **R-TeleSwiftBot💖**\n"
                    "Process cancelled successfully!"
                )
            except Exception:
                pass
            return
        
        if start_time is None:
            start_time = time.time()
        
        percentage = current * 100 / total
        progress_key = f"{message.chat.id}_{message.id}_{type_op}"
        
        # Ultra-fast updates - update every 2% or every 1.5 seconds
        current_time = time.time()
        if progress_key in progress_data:
            last_update_time, last_percentage = progress_data[progress_key]
            if (current_time - last_update_time < 1.5 and 
                abs(percentage - last_percentage) < 2.0 and 
                percentage < 100):
                return
        
        progress_data[progress_key] = (current_time, percentage)
        
        # Calculate speed and ETA
        elapsed_time = current_time - start_time
        if elapsed_time > 0:
            speed = current / elapsed_time
            eta_seconds = (total - current) / speed if speed > 0 else 0
            eta = time.strftime('%M:%S', time.gmtime(eta_seconds)) if eta_seconds < 3600 else "∞"
            speed_mb = speed / (1024 * 1024)
        else:
            speed_mb = 0
            eta = "Calculating..."
        
        # Convert sizes to human readable
        current_mb = current / (1024 * 1024)
        total_mb = total / (1024 * 1024)
        
        # Create enhanced progress bar
        progress_bar = create_progress_bar(percentage)
        
        # Enhanced emoji and operation text
        if type_op == "down":
            emoji = "⬇️"
            operation = "Downloading"
            speed_indicator = "🚀" if speed_mb > 5 else "⚡" if speed_mb > 1 else "📥"
        else:
            emoji = "⬆️" 
            operation = "Uploading"
            speed_indicator = "🚀" if speed_mb > 3 else "⚡" if speed_mb > 0.5 else "📤"
        
        # Ultra-enhanced progress message
        progress_text = (
            f"{emoji} **R-TeleSwiftBot💖 {operation}** `{percentage:.1f}%`\n\n"
            f"{progress_bar}\n\n"
            f"📊 **Size:** `{current_mb:.1f} MB` / `{total_mb:.1f} MB`\n"
            f"{speed_indicator} **Speed:** `{speed_mb:.2f} MB/s`\n"
            f"⏱️ **ETA:** `{eta}`\n"
            f"🕐 **Elapsed:** `{time.strftime('%M:%S', time.gmtime(elapsed_time))}`\n"
            f"💖 **Ultra High Speed Mode**"
        )
        
        # Try to edit the message
        try:
            await message.edit(progress_text)
        except Exception:
            pass  # Ignore edit errors
            
    except Exception as e:
        logger.error(f"Progress error: {e}")

async def ultra_fast_download(acc, msg, status_msg, user_id):
    """Ultra-fast download with maximum speed optimization and cancellation check"""
    start_time = time.time()
    
    # Store progress message for cancellation
    SerialBatchManager.set_progress_message(user_id, status_msg)
    
    for attempt in range(2):  # Quick retry for speed
        try:
            # Check if cancelled before starting
            if SerialBatchManager.is_cancelled(user_id):
                await status_msg.edit(
                    "🛑 **Your Current Process Terminated Due To User Request ⚠️❌**\n\n"
                    "💖 **R-TeleSwiftBot💖**\n"
                    "Process cancelled successfully!"
                )
                return None
                
            logger.info(f"R-TeleSwiftBot💖 ultra-fast download attempt {attempt + 1} for message {msg.id}")
            
            file = await acc.download_media(
                msg, 
                progress=progress, 
                progress_args=[status_msg, "down", start_time]
            )
            
            # Check if cancelled after download
            if SerialBatchManager.is_cancelled(user_id):
                if file and os.path.exists(file):
                    await safe_delete_file(file)
                await status_msg.edit(
                    "🛑 **Your Current Process Terminated Due To User Request ⚠️❌**\n\n"
                    "💖 **R-TeleSwiftBot💖**\n"
                    "Process cancelled successfully!"
                )
                return None
            
            if file and os.path.exists(file):
                return file
            else:
                raise Exception("Downloaded file not found")
                
        except FloodWait as fw:
            if fw.value > 30:  # If flood wait is too long, break
                await status_msg.edit(f"❌ **Rate limited for {fw.value}s - try again later**")
                return None
            logger.warning(f"FloodWait {fw.value}s on attempt {attempt + 1}")
            await asyncio.sleep(fw.value)
        except Exception as e:
            logger.warning(f"Download attempt {attempt + 1} failed: {e}")
            if attempt == 0:  # Only retry once
                await asyncio.sleep(2)
            else:
                raise e
    
    return None

async def get_optimized_thumbnail(acc, msg):
    """Get optimized thumbnail with ultra-fast processing"""
    try:
        thumbnail_path = None
        
        # Video thumbnail
        if msg.video and hasattr(msg.video, 'thumbs') and msg.video.thumbs:
            try:
                largest_thumb = max(msg.video.thumbs, key=lambda x: getattr(x, 'file_size', 0))
                thumbnail_path = await asyncio.wait_for(
                    acc.download_media(largest_thumb.file_id),
                    timeout=15.0
                )
                logger.info(f"Video thumbnail downloaded successfully: {thumbnail_path}")
            except Exception as e:
                logger.warning(f"Video thumbnail download failed: {e}")
        
        # Document thumbnail  
        elif msg.document and hasattr(msg.document, 'thumbs') and msg.document.thumbs:
            try:
                largest_thumb = max(msg.document.thumbs, key=lambda x: getattr(x, 'file_size', 0))
                thumbnail_path = await asyncio.wait_for(
                    acc.download_media(largest_thumb.file_id),
                    timeout=15.0
                )
                logger.info(f"Document thumbnail downloaded successfully: {thumbnail_path}")
            except Exception as e:
                logger.warning(f"Document thumbnail download failed: {e}")
        
        # Audio thumbnail
        elif msg.audio and hasattr(msg.audio, 'thumbs') and msg.audio.thumbs:
            try:
                largest_thumb = max(msg.audio.thumbs, key=lambda x: getattr(x, 'file_size', 0))
                thumbnail_path = await asyncio.wait_for(
                    acc.download_media(largest_thumb.file_id),
                    timeout=15.0
                )
                logger.info(f"Audio thumbnail downloaded successfully: {thumbnail_path}")
            except Exception as e:
                logger.warning(f"Audio thumbnail download failed: {e}")
        
        # Photo - use a smaller resolution as thumbnail
        elif msg.photo:
            try:
                # For photos, download the smallest size as thumbnail
                if hasattr(msg.photo, 'file_size') and msg.photo.file_size > 0:
                    thumbnail_path = await asyncio.wait_for(
                        acc.download_media(msg.photo.file_id),
                        timeout=15.0
                    )
                    logger.info(f"Photo thumbnail created successfully: {thumbnail_path}")
            except Exception as e:
                logger.warning(f"Photo thumbnail creation failed: {e}")
        
        # Verify thumbnail
        if thumbnail_path and os.path.exists(thumbnail_path) and os.path.getsize(thumbnail_path) > 0:
            return thumbnail_path
        else:
            logger.info("No valid thumbnail generated")
            return None
            
    except Exception as e:
        logger.error(f"Error getting thumbnail: {e}")
        return None

def get_file_caption(msg):
    """Return EXACT original caption without any modifications"""
    try:
        # FIXED: Return original caption exactly as it is
        if hasattr(msg, 'caption') and msg.caption:
            original_caption = str(msg.caption).strip()
            logger.info(f"Preserving original caption: {original_caption[:100]}...")
            return original_caption
        else:
            # If no caption exists, return None (no caption)
            logger.info("No original caption found")
            return None
        
    except Exception as e:
        logger.error(f"Caption extraction error: {e}")
        return None

# Add cancel command handler
@Client.on_message(filters.command("cancel") & filters.private)
async def cancel_handler(bot, message):
    """Handle cancel command - FIXED"""
    try:
        user_id = message.from_user.id
        
        if SerialBatchManager.is_active(user_id):
            await SerialBatchManager.cancel_batch(user_id)
            await message.reply_text(
                "🛑 **Cancellation Request Received!**\n\n"
                "Your current download process is being terminated...\n\n"
                "💖 **R-TeleSwiftBot💖**"
            )
            logger.info(f"User {user_id} cancelled batch operation")
        else:
            await message.reply_text(
                "ℹ️ **No Active Process**\n\n"
                "You don't have any active download processes to cancel.\n\n"
                "💖 **R-TeleSwiftBot💖**"
            )
    except Exception as e:
        logger.error(f"Cancel handler error: {e}")
        await message.reply_text("❌ **Error processing cancel request**")

@Client.on_message(filters.command("start") & filters.private & ~filters.forwarded)
async def start(client, message):
    """Enhanced start command with beautiful interface - MODIFIED"""
    try:
        await db.update_last_active(message.from_user.id)
        
        # Add user to database if not exists
        if not await db.is_user_exist(message.from_user.id):
            await db.add_user(message.from_user.id, message.from_user.first_name or "User")
            logger.info(f"New user started bot: {message.from_user.id}")
        
        # Create buttons - Channel button removed, Developer contact updated
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📖 ʜᴇʟᴘ", callback_data="help"),
                InlineKeyboardButton("🔐 ʟᴏɢɪɴ", callback_data="login_help")
            ],
            [
                InlineKeyboardButton("👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/fightermonk110")
            ]
        ])
        
        await message.reply_text(
            text=START_TXT.format(user_mention=message.from_user.mention),
            quote=True,
            reply_markup=keyboard
        )
        
        logger.info(f"Start command served to user: {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Start command error: {e}")
        await message.reply_text(
            "❌ **Error starting bot!** Please try again later.\n\n💖 R-TeleSwiftBot💖",
            quote=True
        )

@Client.on_callback_query()
async def callback_handler(client, callback_query):
    """Enhanced callback query handler"""
    try:
        data = callback_query.data
        user_id = callback_query.from_user.id
        
        await db.update_last_active(user_id)
        
        if data == "help":
            await callback_query.edit_message_text(
                HELP_TXT,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🏠 ʙᴀᴄᴋ", callback_data="back_to_start")]
                ])
            )
            
        elif data == "login_help":
            login_text = (
                "🔐 **R-TeleSwiftBot💖 ʟᴏɢɪɴ ɪɴsᴛʀᴜᴄᴛɪᴏɴs**\n\n"
                "To use this ultra-fast bot, you need to login first:\n\n"
                "📱 **Steps:**\n"
                "1. Send `/login` command\n"
                "2. Enter your phone number with country code\n"
                "3. Enter OTP received on Telegram\n"
                "4. If required, enter 2FA password\n\n"
                "🔒 **Security:** Your session is stored securely\n"
                "💖 Use `/logout` to remove session anytime"
            )
            await callback_query.edit_message_text(
                login_text,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🏠 ʙᴀᴄᴋ", callback_data="back_to_start")]
                ])
            )
            
        elif data == "back_to_start":
            # Create buttons - Channel button removed, Developer contact updated
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📖 ʜᴇʟᴘ", callback_data="help"),
                    InlineKeyboardButton("🔐 ʟᴏɢɪɴ", callback_data="login_help")
                ],
                [
                    InlineKeyboardButton("👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/fightermonk110")
                ]
            ])
            
            await callback_query.edit_message_text(
                START_TXT.format(user_mention=callback_query.from_user.mention),
                reply_markup=keyboard
            )
        
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Callback query error: {e}")
        try:
            await callback_query.answer("❌ Error occurred!", show_alert=True)
        except:
            pass

@Client.on_message(filters.command("help") & filters.private & ~filters.forwarded)
async def help_command(client, message):
    """Enhanced help command"""
    try:
        await db.update_last_active(message.from_user.id)
        
        await message.reply_text(
            HELP_TXT,
            quote=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 ʙᴀᴄᴋ", callback_data="back_to_start")]
            ])
        )
        
    except Exception as e:
        logger.error(f"Help command error: {e}")
        await message.reply_text("❌ **Error showing help!** Please try again.")

@Client.on_message(filters.text & filters.private & ~filters.forwarded & ~filters.command(['start', 'help', 'login', 'logout', 'cancel']))
async def handle_message(client, message):
    """Enhanced message handler for ultra-fast serial batch downloads"""
    try:
        user_id = message.from_user.id
        await db.update_last_active(user_id)
        
        # Check if user has active batch
        if SerialBatchManager.is_active(user_id):
            return await message.reply_text(
                "⏳ **R-TeleSwiftBot💖 Busy!**\n\n"
                "🔄 You have an active download in progress.\n"
                "Please wait for it to complete or use `/cancel` to stop it.\n\n"
                "💡 **Tip:** Use serial batch processing for better speed!\n"
                "💖 **Ultra High Speed Mode**"
            )
        
        # Validate link
        link_text = message.text.strip()
        if not is_valid_telegram_post_link(link_text):
            return await message.reply_text(ERROR_MESSAGES['invalid_link'])
        
        # Check login status
        user_data = await db.get_session(user_id)
        if not user_data:
            return await message.reply_text(ERROR_MESSAGES['not_logged_in'])
        
        # Parse the link
        chat_id, start_msg_id, end_msg_id = parse_telegram_link(link_text)
        if chat_id is None:
            return await message.reply_text(ERROR_MESSAGES['invalid_link'])
        
        # Handle single vs batch download
        if end_msg_id is None:
            # Single download
            await handle_single_download(client, message, user_data, chat_id, start_msg_id, link_text)
        else:
            # Serial batch download
            await handle_serial_batch_download(client, message, user_data, chat_id, start_msg_id, end_msg_id, link_text)
    
    except Exception as e:
        logger.error(f"Message handler error: {e}")
        await message.reply_text(ERROR_MESSAGES['unknown_error'])

async def handle_single_download(client, message, user_data, chat_id, msg_id, original_link):
    """Handle single message download with EXACT original caption preservation"""
    user_id = message.from_user.id
    acc = None
    file_path = None
    thumbnail_path = None
    
    try:
        # Start batch tracking
        SerialBatchManager.start_batch(user_id, {"type": "single"})
        
        # Create status message
        status_msg = await message.reply_text(
            "🚀 **R-TeleSwiftBot💖 Initializing...**\n\n"
            "⚡ **Ultra High Speed Mode Activated**\n"
            "📥 **Preparing to download...**"
        )
        
        # Store progress message
        SerialBatchManager.set_progress_message(user_id, status_msg)
        
        # Create client
        try:
            acc = await create_client_with_retry(user_data)
            await status_msg.edit("✅ **Connected!** Fetching content...")
        except Exception as e:
            return await status_msg.edit(f"❌ **Connection failed:** {str(e)[:100]}")
        
        # Check cancellation
        if SerialBatchManager.is_cancelled(user_id):
            await status_msg.edit(
                "🛑 **Your Current Process Terminated Due To User Request ⚠️❌**\n\n"
                "💖 **R-TeleSwiftBot💖**\n"
                "Process cancelled successfully!"
            )
            return
        
        # Get message
        try:
            target_msg = await acc.get_messages(chat_id, msg_id)
            if not target_msg:
                raise Exception("Message not found or inaccessible")
        except Exception as e:
            return await status_msg.edit(ERROR_MESSAGES['access_denied'])
        
        # Check if message has media
        if not (target_msg.video or target_msg.document or target_msg.photo or target_msg.audio or target_msg.voice or target_msg.animation):
            if target_msg.text:
                # Text message
                await status_msg.edit("📝 **Text message found!**")
                return await client.send_message(user_id, target_msg.text)
            else:
                return await status_msg.edit("❌ **No downloadable content found!**")
        
        # Check file size
        file_size = 0
        if target_msg.video:
            file_size = target_msg.video.file_size
        elif target_msg.document:
            file_size = target_msg.document.file_size
        elif target_msg.photo:
            file_size = target_msg.photo.file_size
        elif target_msg.audio:
            file_size = target_msg.audio.file_size
        
        if file_size > MAX_FILE_SIZE:
            return await status_msg.edit(ERROR_MESSAGES['file_too_large'])
        
        # Check cancellation before download
        if SerialBatchManager.is_cancelled(user_id):
            await status_msg.edit(
                "🛑 **Your Current Process Terminated Due To User Request ⚠️❌**\n\n"
                "💖 **R-TeleSwiftBot💖**\n"
                "Process cancelled successfully!"
            )
            return
        
        # Get thumbnail FIRST
        await status_msg.edit("🖼️ **Generating thumbnail...**")
        thumbnail_path = await get_optimized_thumbnail(acc, target_msg)
        
        # Download file
        await status_msg.edit("⬇️ **R-TeleSwiftBot💖 Downloading...**\n\n💖 **Ultra High Speed Mode**")
        file_path = await ultra_fast_download(acc, target_msg, status_msg, user_id)
        
        # Check cancellation after download
        if SerialBatchManager.is_cancelled(user_id):
            if file_path:
                await safe_delete_file(file_path)
            if thumbnail_path:
                await safe_delete_file(thumbnail_path)
            return
        
        if not file_path:
            await status_msg.edit("❌ **Download failed!**")
            return
        
        # FIXED: Get exact original caption
        original_caption = get_file_caption(target_msg)
        
        # Upload file with EXACT original caption
        await status_msg.edit("⬆️ **Uploading...**")
        
        try:
            # Check cancellation before upload
            if SerialBatchManager.is_cancelled(user_id):
                await safe_delete_file(file_path)
                if thumbnail_path:
                    await safe_delete_file(thumbnail_path)
                await status_msg.edit(
                    "🛑 **Your Current Process Terminated Due To User Request ⚠️❌**\n\n"
                    "💖 **R-TeleSwiftBot💖**\n"
                    "Process cancelled successfully!"
                )
                return
            
            # Send file based on type with EXACT original caption
            if target_msg.video:
                await client.send_video(
                    chat_id=user_id,
                    video=file_path,
                    thumb=thumbnail_path,
                    caption=original_caption,  # EXACT original caption
                    progress=progress,
                    progress_args=[status_msg, "up"]
                )
            elif target_msg.document:
                await client.send_document(
                    chat_id=user_id,
                    document=file_path,
                    thumb=thumbnail_path,
                    caption=original_caption,  # EXACT original caption
                    progress=progress,
                    progress_args=[status_msg, "up"]
                )
            elif target_msg.photo:
                await client.send_photo(
                    chat_id=user_id,
                    photo=file_path,
                    caption=original_caption  # EXACT original caption
                )
            elif target_msg.audio:
                await client.send_audio(
                    chat_id=user_id,
                    audio=file_path,
                    thumb=thumbnail_path,
                    caption=original_caption,  # EXACT original caption
                    progress=progress,
                    progress_args=[status_msg, "up"]
                )
            
            # Check final cancellation
            if SerialBatchManager.is_cancelled(user_id):
                await status_msg.edit(
                    "🛑 **Your Current Process Terminated Due To User Request ⚠️❌**\n\n"
                    "💖 **R-TeleSwiftBot💖**\n"
                    "Process cancelled successfully!"
                )
            else:
                await status_msg.edit("✅ **Download completed successfully!** 💖")
            
        except Exception as e:
            logger.error(f"Upload error: {e}")
            await status_msg.edit("❌ **Upload failed!**")
            
        # Cleanup files
        await safe_delete_file(file_path)
        if thumbnail_path:
            await safe_delete_file(thumbnail_path)
                
    except Exception as e:
        logger.error(f"Single download error: {e}")
        await message.reply_text("❌ **Download process failed!**")
        # Cleanup on error
        if file_path:
            await safe_delete_file(file_path)
        if thumbnail_path:
            await safe_delete_file(thumbnail_path)
    finally:
        SerialBatchManager.clear_batch(user_id)
        if acc:
            try:
                await acc.disconnect()
            except:
                pass

async def handle_serial_batch_download(client, message, user_data, chat_id, start_id, end_id, original_link):
    """Handle batch download with proper cancellation support and exact caption preservation"""
    user_id = message.from_user.id
    acc = None
    
    try:
        # Calculate batch info
        total_msgs = end_id - start_id + 1
        if total_msgs > MAX_BATCH_SIZE:
            return await message.reply_text(
                f"❌ **Batch too large!**\n\n"
                f"Maximum batch size: {MAX_BATCH_SIZE}\n"
                f"Your request: {total_msgs}\n\n"
                f"Please reduce the range."
            )
        
        SerialBatchManager.start_batch(user_id, {"type": "batch", "total": total_msgs})
        
        # Initial status
        status_msg = await message.reply_text(
            f"🔄 **R-TeleSwiftBot💖 Serial Batch Download**\n\n"
            f"📊 **Range:** {start_id} to {end_id}\n"
            f"📦 **Total Messages:** {total_msgs}\n"
            f"⚡ **Mode:** Ultra High Speed\n\n"
            f"🚀 **Starting download...**"
        )
        
        # Store progress message
        SerialBatchManager.set_progress_message(user_id, status_msg)
        
        # Create client
        try:
            acc = await create_client_with_retry(user_data)
        except Exception as e:
            return await status_msg.edit(f"❌ **Connection failed:** {str(e)}")
        
        successful = 0
        failed = 0
        
        # Process messages serially
        for i, msg_id in enumerate(range(start_id, end_id + 1), 1):
            # Check cancellation
            if SerialBatchManager.is_cancelled(user_id):
                await status_msg.edit(
                    "🛑 **Your Current Process Terminated Due To User Request ⚠️❌**\n\n"
                    "💖 **R-TeleSwiftBot💖**\n"
                    "Process cancelled successfully!"
                )
                return
            
            try:
                # Update progress
                progress_text = (
                    f"🔄 **R-TeleSwiftBot💖 Serial Batch**\n\n"
                    f"📊 **Processing:** {i}/{total_msgs}\n"
                    f"✅ **Success:** {successful}\n"
                    f"❌ **Failed:** {failed}\n"
                    f"🎯 **Current:** Message {msg_id}\n\n"
                    f"💖 **Ultra High Speed Mode**"
                )
                await status_msg.edit(progress_text)
                
                # Get message
                try:
                    target_msg = await acc.get_messages(chat_id, msg_id)
                    if not target_msg or not target_msg.media:
                        failed += 1
                        continue
                except Exception:
                    failed += 1
                    continue
                
                # Check file size
                file_size = 0
                if target_msg.video:
                    file_size = target_msg.video.file_size
                elif target_msg.document:
                    file_size = target_msg.document.file_size
                elif target_msg.photo:
                    file_size = target_msg.photo.file_size
                elif target_msg.audio:
                    file_size = target_msg.audio.file_size
                
                if file_size > MAX_FILE_SIZE:
                    failed += 1
                    continue
                
                # Download thumbnail
                thumbnail_path = await get_optimized_thumbnail(acc, target_msg)
                
                # Download file
                file_path = await ultra_fast_download(acc, target_msg, status_msg, user_id)
                
                if SerialBatchManager.is_cancelled(user_id):
                    if file_path:
                        await safe_delete_file(file_path)
                    if thumbnail_path:
                        await safe_delete_file(thumbnail_path)
                    return
                
                if not file_path:
                    failed += 1
                    continue
                
                # Get EXACT original caption
                original_caption = get_file_caption(target_msg)
                
                # Upload based on media type with EXACT original caption
                try:
                    if target_msg.video:
                        await client.send_video(
                            chat_id=user_id,
                            video=file_path,
                            thumb=thumbnail_path,
                            caption=original_caption
                        )
                    elif target_msg.document:
                        await client.send_document(
                            chat_id=user_id,
                            document=file_path,
                            thumb=thumbnail_path,
                            caption=original_caption
                        )
                    elif target_msg.photo:
                        await client.send_photo(
                            chat_id=user_id,
                            photo=file_path,
                            caption=original_caption
                        )
                    elif target_msg.audio:
                        await client.send_audio(
                            chat_id=user_id,
                            audio=file_path,
                            thumb=thumbnail_path,
                            caption=original_caption
                        )
                    
                    successful += 1
                    
                except Exception as upload_error:
                    logger.error(f"Upload error for message {msg_id}: {upload_error}")
                    failed += 1
                
                # Cleanup
                await safe_delete_file(file_path)
                if thumbnail_path:
                    await safe_delete_file(thumbnail_path)
                
                # Brief delay for stability
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error processing message {msg_id}: {e}")
                failed += 1
                continue
        
        # Final status
        if SerialBatchManager.is_cancelled(user_id):
            await status_msg.edit(
                "🛑 **Your Current Process Terminated Due To User Request ⚠️❌**\n\n"
                "💖 **R-TeleSwiftBot💖**\n"
                "Process cancelled successfully!"
            )
        else:
            final_text = (
                f"✅ **R-TeleSwiftBot💖 Batch Complete!**\n\n"
                f"📊 **Total Processed:** {total_msgs}\n"
                f"✅ **Successful:** {successful}\n"
                f"❌ **Failed:** {failed}\n\n"
                f"💖 **Ultra High Speed Mode**"
            )
            await status_msg.edit(final_text)
    
    except Exception as e:
        logger.error(f"Batch download error: {e}")
        await message.reply_text("❌ **Batch download failed!**")
    finally:
        SerialBatchManager.clear_batch(user_id)
        if acc:
            try:
                await acc.disconnect()
            except:
                pass

# Don't Remove Credit Tg - @VJ_Botz  
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
