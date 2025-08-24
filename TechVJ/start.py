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
        
        # Quick thumbnail extraction with shorter timeout
        if msg.video and hasattr(msg.video, 'thumbs') and msg.video.thumbs:
            largest_thumb = max(msg.video.thumbs, key=lambda x: getattr(x, 'file_size', 0))
            thumbnail_path = await asyncio.wait_for(
                acc.download_media(largest_thumb.file_id),
                timeout=15.0
            )
        elif msg.document and hasattr(msg.document, 'thumbs') and msg.document.thumbs:
            largest_thumb = max(msg.document.thumbs, key=lambda x: getattr(x, 'file_size', 0))
            thumbnail_path = await asyncio.wait_for(
                acc.download_media(largest_thumb.file_id),
                timeout=15.0
            )
        elif msg.photo:
            thumbnail_path = await asyncio.wait_for(
                acc.download_media(msg.photo.file_id),
                timeout=15.0
            )
        
        return thumbnail_path if thumbnail_path and os.path.exists(thumbnail_path) else None
            
    except Exception as e:
        logger.error(f"Error getting thumbnail: {e}")
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

@Client.on_message(filters.command("start") & filters.private)
async def start_message(bot, message):
    """Handle start command"""
    try:
        await db.update_last_active(message.from_user.id)
        
        if not await db.is_user_exist(message.from_user.id):
            await db.add_user(message.from_user.id, message.from_user.first_name)
            logger.info(f"New user added: {message.from_user.id}")
        
        start_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💖 Help", callback_data="help"),
             InlineKeyboardButton("🔐 Login", callback_data="login")],
            [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/fightermonk110")]
        ])
        
        await message.reply_text(
            START_TXT.format(user_mention=message.from_user.mention),
            reply_markup=start_kb
        )
        
    except Exception as e:
        logger.error(f"Start command error: {e}")

@Client.on_message(filters.command("help") & filters.private)
async def help_message(bot, message):
    """Handle help command"""
    try:
        await db.update_last_active(message.from_user.id)
        
        help_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔐 Login", callback_data="login")],
            [InlineKeyboardButton("🏠 Home", callback_data="start")]
        ])
        
        await message.reply_text(
            HELP_TXT,
            reply_markup=help_kb
        )
        
    except Exception as e:
        logger.error(f"Help command error: {e}")

@Client.on_callback_query()
async def callback_handler(bot, query):
    """Handle callback queries"""
    try:
        await query.answer()
        data = query.data
        
        if data == "start":
            start_kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("💖 Help", callback_data="help"),
                 InlineKeyboardButton("🔐 Login", callback_data="login")],
                [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/fightermonk110")]
            ])
            
            await query.message.edit_text(
                START_TXT.format(user_mention=query.from_user.mention),
                reply_markup=start_kb
            )
            
        elif data == "help":
            help_kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔐 Login", callback_data="login")],
                [InlineKeyboardButton("🏠 Home", callback_data="start")]
            ])
            
            await query.message.edit_text(
                HELP_TXT,
                reply_markup=help_kb
            )
            
        elif data == "login":
            await query.message.edit_text(
                "🔐 **Login Process**\n\n"
                "To login with your Telegram account, send the command:\n\n"
                "`/login`\n\n"
                "💖 **R-TeleSwiftBot💖**"
            )
            
    except Exception as e:
        logger.error(f"Callback handler error: {e}")

@Client.on_message(filters.private & filters.text & ~filters.command(['start', 'help', 'login', 'logout', 'cancel', 'broadcast', 'stats']))
async def handle_request(bot, message):
    """Handle download requests with enhanced cancellation support"""
    try:
        await db.update_last_active(message.from_user.id)
        user_id = message.from_user.id
        
        # Check if user has active process
        if SerialBatchManager.is_active(user_id):
            return await message.reply_text(
                "⚠️ **You already have an active download process!**\n\n"
                "Please wait for it to complete or use `/cancel` to stop it.\n\n"
                "💖 **R-TeleSwiftBot💖**"
            )
        
        # Get user session
        user_data = await db.get_session(user_id)
        if not user_data:
            return await message.reply_text(ERROR_MESSAGES['not_logged_in'])
        
        text = message.text.strip()
        
        # Validate link
        if not is_valid_telegram_post_link(text):
            return await message.reply_text(ERROR_MESSAGES['invalid_link'])
        
        # Parse link
        chat_id, start_id, end_id = parse_telegram_link(text)
        if not chat_id or not start_id:
            return await message.reply_text(ERROR_MESSAGES['invalid_link'])
        
        # Create client
        try:
            acc = await create_client_with_retry(user_data)
        except Exception as e:
            logger.error(f"Client creation error: {e}")
            return await message.reply_text(f"❌ **Connection failed:** {str(e)}")
        
        try:
            if end_id:  # Batch download
                await handle_batch_download(bot, message, acc, chat_id, start_id, end_id, user_id)
            else:  # Single download
                await handle_single_download(bot, message, acc, chat_id, start_id, user_id)
        finally:
            try:
                await acc.disconnect()
            except:
                pass
                
    except Exception as e:
        logger.error(f"Request handler error: {e}")
        await message.reply_text(ERROR_MESSAGES['unknown_error'])

async def handle_single_download(bot, message, acc, chat_id, msg_id, user_id):
    """Handle single message download with cancellation support"""
    try:
        SerialBatchManager.start_batch(user_id, {"type": "single", "total": 1})
        
        # Initial status
        status_msg = await message.reply_text(
            "⚡ **R-TeleSwiftBot💖 Starting Download...**\n\n"
            "🔄 **Fetching message...**\n"
            "💖 **Ultra High Speed Mode**"
        )
        
        # Store progress message
        SerialBatchManager.set_progress_message(user_id, status_msg)
        
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
            msg = await acc.get_messages(chat_id, msg_id)
            if not msg or not msg.media:
                await status_msg.edit("❌ **No media found in this message!**")
                return
        except Exception as e:
            await status_msg.edit(f"❌ **Failed to access message:** {str(e)[:100]}")
            return
        
        # Check cancellation before download
        if SerialBatchManager.is_cancelled(user_id):
            await status_msg.edit(
                "🛑 **Your Current Process Terminated Due To User Request ⚠️❌**\n\n"
                "💖 **R-TeleSwiftBot💖**\n"
                "Process cancelled successfully!"
            )
            return
        
        # Download file
        file_path = await ultra_fast_download(acc, msg, status_msg, user_id)
        
        # Check cancellation after download
        if SerialBatchManager.is_cancelled(user_id):
            if file_path:
                await safe_delete_file(file_path)
            return
        
        if not file_path:
            await status_msg.edit("❌ **Download failed!**")
            return
        
        # Upload file
        await status_msg.edit("⬆️ **Uploading...**")
        
        try:
            # Get thumbnail
            thumbnail = await get_optimized_thumbnail(acc, msg)
            
            # Check cancellation before upload
            if SerialBatchManager.is_cancelled(user_id):
                await safe_delete_file(file_path)
                if thumbnail:
                    await safe_delete_file(thumbnail)
                await status_msg.edit(
                    "🛑 **Your Current Process Terminated Due To User Request ⚠️❌**\n\n"
                    "💖 **R-TeleSwiftBot💖**\n"
                    "Process cancelled successfully!"
                )
                return
            
            # Send file based on type
            if msg.video:
                await bot.send_video(
                    chat_id=user_id,
                    video=file_path,
                    thumb=thumbnail,
                    caption="📥 **Downloaded via R-TeleSwiftBot💖**",
                    progress=progress,
                    progress_args=[status_msg, "up"]
                )
            elif msg.document:
                await bot.send_document(
                    chat_id=user_id,
                    document=file_path,
                    thumb=thumbnail,
                    caption="📥 **Downloaded via R-TeleSwiftBot💖**",
                    progress=progress,
                    progress_args=[status_msg, "up"]
                )
            elif msg.photo:
                await bot.send_photo(
                    chat_id=user_id,
                    photo=file_path,
                    caption="📥 **Downloaded via R-TeleSwiftBot💖**"
                )
            elif msg.audio:
                await bot.send_audio(
                    chat_id=user_id,
                    audio=file_path,
                    thumb=thumbnail,
                    caption="📥 **Downloaded via R-TeleSwiftBot💖**",
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
            
            # Cleanup
            await safe_delete_file(file_path)
            if thumbnail:
                await safe_delete_file(thumbnail)
                
        except Exception as e:
            logger.error(f"Upload error: {e}")
            await status_msg.edit("❌ **Upload failed!**")
            await safe_delete_file(file_path)
            
    except Exception as e:
        logger.error(f"Single download error: {e}")
        await message.reply_text("❌ **Download process failed!**")
    finally:
        SerialBatchManager.clear_batch(user_id)

async def handle_batch_download(bot, message, acc, chat_id, start_id, end_id, user_id):
    """Handle batch download with proper cancellation support"""
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
                    f"⬇️ **R-TeleSwiftBot💖 Batch Processing**\n\n"
                    f"📊 **Progress:** {i}/{total_msgs} ({(i/total_msgs)*100:.1f}%)\n"
                    f"📦 **Current Message:** {msg_id}\n"
                    f"✅ **Success:** {successful}\n"
                    f"❌ **Failed:** {failed}\n\n"
                    f"💖 **Ultra High Speed Mode**"
                )
                await status_msg.edit(progress_text)
                
                # Get and process message
                msg = await acc.get_messages(chat_id, msg_id)
                if msg and msg.media:
                    file_path = await ultra_fast_download(acc, msg, status_msg, user_id)
                    
                    if SerialBatchManager.is_cancelled(user_id):
                        if file_path:
                            await safe_delete_file(file_path)
                        await status_msg.edit(
                            "🛑 **Your Current Process Terminated Due To User Request ⚠️❌**\n\n"
                            "💖 **R-TeleSwiftBot💖**\n"
                            "Process cancelled successfully!"
                        )
                        return
                    
                    if file_path:
                        # Send file
                        if msg.video:
                            await bot.send_video(
                                chat_id=user_id,
                                video=file_path,
                                caption=f"📥 **{i}/{total_msgs}** via R-TeleSwiftBot💖"
                            )
                        elif msg.document:
                            await bot.send_document(
                                chat_id=user_id,
                                document=file_path,
                                caption=f"📥 **{i}/{total_msgs}** via R-TeleSwiftBot💖"
                            )
                        elif msg.photo:
                            await bot.send_photo(
                                chat_id=user_id,
                                photo=file_path,
                                caption=f"📥 **{i}/{total_msgs}** via R-TeleSwiftBot💖"
                            )
                        elif msg.audio:
                            await bot.send_audio(
                                chat_id=user_id,
                                audio=file_path,
                                caption=f"📥 **{i}/{total_msgs}** via R-TeleSwiftBot💖"
                            )
                        
                        successful += 1
                        await safe_delete_file(file_path)
                    else:
                        failed += 1
                else:
                    failed += 1
                    
            except Exception as e:
                logger.error(f"Batch message {msg_id} error: {e}")
                failed += 1
            
            # Small delay between downloads
            await asyncio.sleep(1)
        
        # Final status
        if not SerialBatchManager.is_cancelled(user_id):
            final_text = (
                f"✅ **R-TeleSwiftBot💖 Batch Completed!**\n\n"
                f"📊 **Final Results:**\n"
                f"📦 **Total Messages:** {total_msgs}\n"
                f"✅ **Successfully Downloaded:** {successful}\n"
                f"❌ **Failed:** {failed}\n"
                f"📈 **Success Rate:** {(successful/total_msgs)*100:.1f}%\n\n"
                f"💖 **Ultra High Speed Mode**"
            )
            await status_msg.edit(final_text)
            
    except Exception as e:
        logger.error(f"Batch download error: {e}")
        await message.reply_text("❌ **Batch download failed!**")
    finally:
        SerialBatchManager.clear_batch(user_id)

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
