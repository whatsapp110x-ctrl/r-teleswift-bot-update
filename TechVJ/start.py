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
    
    @classmethod
    def start_batch(cls, user_id, task_info):
        """Start a batch task for user"""
        cls.USER_TASKS[user_id] = task_info
        cls.CANCEL_FLAGS[user_id] = False
    
    @classmethod
    def is_active(cls, user_id):
        """Check if user has active batch"""
        return user_id in cls.USER_TASKS
    
    @classmethod
    def cancel_batch(cls, user_id):
        """Cancel user's batch download"""
        cls.CANCEL_FLAGS[user_id] = True
        if user_id in cls.USER_TASKS:
            del cls.USER_TASKS[user_id]
    
    @classmethod
    def is_cancelled(cls, user_id):
        """Check if batch is cancelled"""
        return cls.CANCEL_FLAGS.get(user_id, False)
    
    @classmethod
    def clear_batch(cls, user_id):
        """Clear batch task"""
        if user_id in cls.USER_TASKS:
            del cls.USER_TASKS[user_id]
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
    """Ultra-enhanced progress callback with beautiful interface"""
    try:
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
    
    for attempt in range(2):  # Quick retry for speed
        try:
            # Check if cancelled before starting
            if SerialBatchManager.is_cancelled(user_id):
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

async def process_media_message(client, message, acc, msg, user_id, is_batch=False, batch_info=None):
    """Process media message with ultra-high speed and original caption preservation - NO SUCCESS MESSAGE"""
    file_path = None
    thumbnail = None
    
    try:
        # Check if cancelled at start
        if SerialBatchManager.is_cancelled(user_id):
            return False
        
        filename = None
        file_size = 0
        
        if msg.document:
            filename = getattr(msg.document, 'file_name', f'document_{msg.id}')
            file_size = msg.document.file_size
        elif msg.video:
            filename = f'video_{msg.id}.mp4'
            file_size = msg.video.file_size
        elif msg.photo:
            filename = f'photo_{msg.id}.jpg'
            file_size = msg.photo.file_size
        elif msg.audio:
            filename = getattr(msg.audio, 'file_name', f'audio_{msg.id}.mp3')
            file_size = msg.audio.file_size
        else:
            if not is_batch:
                await message.reply_text("❌ **No downloadable media found**")
            return False
        
        if file_size > MAX_FILE_SIZE:
            if not is_batch:
                await message.reply_text(
                    f"❌ **File too large!**\n\n"
                    f"📊 **Size:** `{file_size/1024/1024:.1f} MB`\n"
                    f"📏 **Max allowed:** `{MAX_FILE_SIZE/1024/1024:.1f} MB`"
                )
            return False
        
        # Enhanced status message with file info
        if is_batch and batch_info:
            status_text = (
                f"🚀 **R-TeleSwiftBot💖 Serial Download**\n\n"
                f"📦 **Batch:** `{batch_info['current']}/{batch_info['total']}`\n"
                f"📁 **File:** `{filename[:35]}...`\n"
                f"📊 **Size:** `{file_size/1024/1024:.1f} MB`\n"
                f"⚡ **Mode:** `Ultra High Speed`"
            )
        else:
            status_text = (
                f"🚀 **R-TeleSwiftBot💖 Download**\n\n"
                f"📁 **File:** `{filename[:40]}...`\n"
                f"📊 **Size:** `{file_size/1024/1024:.1f} MB`\n"
                f"⚡ **Mode:** `Ultra High Speed`"
            )
        
        status_msg = await message.reply_text(status_text)
        
        try:
            download_start_time = time.time()
            
            # Ultra-fast download
            file_path = await ultra_fast_download(acc, msg, status_msg, user_id)
            
            if not file_path or not os.path.exists(file_path):
                await status_msg.edit("❌ **Download failed - file not accessible**")
                return False
            
            # Check if cancelled after download
            if SerialBatchManager.is_cancelled(user_id):
                await safe_delete_file(file_path)
                await status_msg.edit("🛑 **Operation cancelled**")
                return False
            
            # Get thumbnail quickly
            thumbnail = await get_optimized_thumbnail(acc, msg)
            
            # Enhanced upload status
            await status_msg.edit(
                f"⬆️ **R-TeleSwiftBot💖 Upload**\n\n"
                f"📁 **File:** `{filename[:40]}...`\n"
                f"⚡ **Mode:** `Ultra High Speed`"
            )
            
            # PRESERVE ORIGINAL CAPTION - This is the key fix!
            original_caption = msg.caption if msg.caption else ""
            if original_caption:
                # Keep original caption exactly as it is, but add success message
                final_caption = f"{original_caption}\n\n✅ Downloaded successfully via R-TeleSwiftBot💖"
            else:
                # Only if no original caption, use filename with success message
                final_caption = f"📎 **{filename}**\n\n✅ Downloaded successfully via R-TeleSwiftBot💖"
            
            # Upload with real-time progress
            upload_start_time = time.time()
            
            if msg.document:
                await client.send_document(
                    message.chat.id,
                    file_path,
                    thumb=thumbnail,
                    caption=final_caption,
                    progress=progress,
                    progress_args=[status_msg, "up", upload_start_time]
                )
            elif msg.video:
                await client.send_video(
                    message.chat.id,
                    file_path,
                    thumb=thumbnail,
                    caption=final_caption,
                    progress=progress,
                    progress_args=[status_msg, "up", upload_start_time]
                )
            elif msg.photo:
                await client.send_photo(
                    message.chat.id,
                    file_path,
                    caption=final_caption
                )
            elif msg.audio:
                await client.send_audio(
                    message.chat.id,
                    file_path,
                    thumb=thumbnail,
                    caption=final_caption,
                    progress=progress,
                    progress_args=[status_msg, "up", upload_start_time]
                )
            
            # Just delete the status message silently
            try:
                await status_msg.delete()
            except Exception:
                pass
            
            return True
            
        except FloodWait as fw:
            await status_msg.edit(f"⏳ **Rate limited - waiting {fw.value}s**")
            await asyncio.sleep(fw.value)
            return False
        except Exception as e:
            logger.error(f"Upload error: {e}")
            await status_msg.edit(f"❌ **Upload failed:** `{str(e)[:50]}`")
            return False
            
    except Exception as e:
        logger.error(f"Error processing media: {e}")
        if not is_batch:
            await message.reply_text(f"❌ **Processing error:** `{str(e)[:100]}`")
        return False
    finally:
        # Clean up files
        if file_path:
            await safe_delete_file(file_path)
        if thumbnail:
            await safe_delete_file(thumbnail)

async def process_single_message(client, message, chat_id, msgid, is_batch=False, batch_info=None):
    """Process a single message for download with FIXED error handling"""
    acc = None
    try:
        user_id = message.from_user.id
        
        # Check if cancelled
        if SerialBatchManager.is_cancelled(user_id):
            return False
        
        # Get user session
        user_data = await db.get_session(user_id)
        if user_data is None:
            if not is_batch:
                await message.reply_text(ERROR_MESSAGES['not_logged_in'])
            return False
        
        # Create client connection
        try:
            acc = await create_client_with_retry(user_data)
        except Exception as e:
            error_msg = str(e)
            if "Session expired" in error_msg or "invalid" in error_msg:
                if not is_batch:
                    await message.reply_text(ERROR_MESSAGES['session_expired'])
                await db.set_session(user_id, None)
            else:
                if not is_batch:
                    await message.reply_text(f"❌ **Connection error:** `{error_msg[:100]}`")
            return False
        
        # Get the message with proper error handling
        try:
            msg = await asyncio.wait_for(
                acc.get_messages(chat_id, msgid),
                timeout=30.0
            )
            
            if not msg:
                if not is_batch:
                    await message.reply_text("❌ **Message not found or access denied**")
                return False
                
        except (ChannelPrivate, UserNotParticipant):
            if not is_batch:
                await message.reply_text(ERROR_MESSAGES['access_denied'])
            return False
        except (UsernameInvalid, UsernameNotOccupied):
            if not is_batch:
                await message.reply_text("❌ **Invalid username or channel not found**")
            return False
        except PeerIdInvalid:
            if not is_batch:
                await message.reply_text("❌ **Invalid chat ID or access denied**")
            return False
        except Exception as e:
            logger.error(f"Error getting message {msgid} from {chat_id}: {e}")
            if not is_batch:
                await message.reply_text(f"❌ **Failed to access message:** `{str(e)[:100]}`")
            return False
        
        # Process the message
        success = await process_media_message(client, message, acc, msg, user_id, is_batch, batch_info)
        return success
        
    except Exception as e:
        logger.error(f"Error in process_single_message: {e}")
        if not is_batch:
            await message.reply_text(f"❌ **Processing error:** `{str(e)[:100]}`")
        return False
    finally:
        # Clean up
        if acc:
            try:
                await acc.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting client: {e}")

# Start command
@Client.on_message(filters.command("start") & filters.private)
async def start(client, message):
    """Handle start command with enhanced interface"""
    try:
        user_id = message.from_user.id
        
        # Add user to database
        if not await db.is_user_exist(user_id):
            await db.add_user(user_id, message.from_user.first_name)
        
        await db.update_last_active(user_id)
        
        # Enhanced buttons
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📖 Help", callback_data="help"),
                InlineKeyboardButton("⚡ Features", callback_data="features")
            ],
            [
                InlineKeyboardButton("📢 Channel", url="https://t.me/Tech_VJ"),
                InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/VJ_Botz")
            ]
        ])
        
        await message.reply_text(
            START_TXT.format(user_mention=message.from_user.mention),
            reply_markup=buttons
        )
        
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await message.reply_text("❌ An error occurred. Please try again later.")

# Help command
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
            [InlineKeyboardButton("📢 Channel", url="https://t.me/Tech_VJ")]
        ])
        
        await message.reply_text(HELP_TXT, reply_markup=buttons)
        
    except Exception as e:
        logger.error(f"Error in help command: {e}")
        await message.reply_text("❌ An error occurred. Please try again later.")

# FIXED Cancel command
@Client.on_message(filters.command("cancel") & filters.private)
async def cancel_command(client, message):
    """Handle cancel command with ACTUAL cancellation"""
    try:
        user_id = message.from_user.id
        
        if SerialBatchManager.is_active(user_id):
            # ACTUALLY cancel the batch
            SerialBatchManager.cancel_batch(user_id)
            await message.reply_text(
                "🛑 **R-TeleSwiftBot💖 Cancelled!**\n\n"
                "✅ All downloads have been stopped successfully.\n"
                "🚀 You can start new downloads now."
            )
        else:
            await message.reply_text(
                "❌ **No active operation to cancel**\n\n"
                "You don't have any running downloads or uploads."
            )
            
    except Exception as e:
        logger.error(f"Error in cancel command: {e}")
        await message.reply_text("❌ An error occurred while cancelling.")

# Handle Telegram links with FIXED parsing
@Client.on_message(filters.private & filters.text)
async def handle_links(client, message):
    """Handle Telegram post links with FIXED link parsing and TRUE SERIAL batch processing"""
    try:
        if message.text.startswith('/'):
            return  # Ignore commands
        
        text = message.text.strip()
        
        if not is_valid_telegram_post_link(text):
            await message.reply_text(ERROR_MESSAGES['invalid_link'])
            return
        
        user_id = message.from_user.id
        
        # Check if user already has active batch
        if SerialBatchManager.is_active(user_id):
            await message.reply_text(
                "⏳ **Another batch is in progress**\n\n"
                "Please wait for completion or use /cancel to stop"
            )
            return
        
        await db.update_last_active(user_id)
        
        # FIXED: Parse the link properly
        chat_id, start_msg, end_msg = parse_telegram_link(text)
        
        if chat_id is None:
            await message.reply_text("❌ **Invalid link format**")
            return
        
        # Check for batch download
        if end_msg is not None:
            # Handle TRUE SERIAL batch download
            await handle_serial_batch_download(client, message, chat_id, start_msg, end_msg)
        else:
            # Handle single download
            await process_single_message(client, message, chat_id, start_msg)
        
    except Exception as e:
        logger.error(f"Error handling link: {e}")
        await message.reply_text(f"❌ **Link processing error:** `{str(e)[:100]}`")

async def handle_serial_batch_download(client, message, chat_id, start_msg, end_msg):
    """TRUE SERIAL batch download - one by one with proper cancellation"""
    user_id = message.from_user.id
    
    try:
        total_messages = end_msg - start_msg + 1
        
        if total_messages > MAX_BATCH_SIZE:
            await message.reply_text(
                f"❌ **Batch size too large!**\n\n"
                f"📊 **Requested:** `{total_messages} messages`\n"
                f"📏 **Max allowed:** `{MAX_BATCH_SIZE} messages`\n\n"
                f"💡 **Tip:** Split into smaller batches"
            )
            return
        
        # Start serial batch task
        SerialBatchManager.start_batch(user_id, {
            'total': total_messages,
            'current': 0,
            'start_time': time.time()
        })
        
        # Enhanced batch status
        batch_status = await message.reply_text(
            f"🚀 **R-TeleSwiftBot💖 Serial Batch Started**\n\n"
            f"📦 **Total Messages:** `{total_messages}`\n"
            f"🔢 **Range:** `{start_msg}` → `{end_msg}`\n"
            f"⚡ **Mode:** `True Serial - One by One`\n"
            f"🛑 **Use /cancel to stop anytime**"
        )
        
        success_count = 0
        failed_count = 0
        start_time = time.time()
        
        # TRUE SERIAL PROCESSING - One by one
        for i, msg_id in enumerate(range(start_msg, end_msg + 1), 1):
            try:
                # Check if cancelled BEFORE each download
                if SerialBatchManager.is_cancelled(user_id):
                    await batch_status.edit(
                        f"🛑 **R-TeleSwiftBot💖 Batch Cancelled**\n\n"
                        f"📊 **Processed:** `{i-1}/{total_messages}`\n"
                        f"✅ **Success:** `{success_count}`\n"
                        f"❌ **Failed:** `{failed_count}`\n\n"
                        f"🛑 **Cancelled by user request**"
                    )
                    return
                
                # Update progress every 3 messages or at start/end
                if i % 3 == 0 or i == 1 or i == total_messages:
                    elapsed = time.time() - start_time
                    rate = i / elapsed if elapsed > 0 else 0
                    eta_seconds = (total_messages - i) / rate if rate > 0 else 0
                    eta = time.strftime('%M:%S', time.gmtime(eta_seconds)) if eta_seconds < 3600 else "∞"
                    
                    progress_bar = create_progress_bar((i / total_messages) * 100)
                    
                    await batch_status.edit(
                        f"🚀 **R-TeleSwiftBot💖 Serial Processing**\n\n"
                        f"{progress_bar}\n\n"
                        f"📊 **Progress:** `{i}/{total_messages}` ({i/total_messages*100:.1f}%)\n"
                        f"✅ **Success:** `{success_count}`\n"
                        f"❌ **Failed:** `{failed_count}`\n"
                        f"⚡ **Speed:** `{rate:.1f} msg/s`\n"
                        f"⏱️ **ETA:** `{eta}`\n\n"
                        f"🔄 **Current:** `Message {msg_id}`\n"
                        f"💖 **True Serial Mode**"
                    )
                
                # Process message with batch info
                batch_info = {'current': i, 'total': total_messages}
                success = await process_single_message(client, message, chat_id, msg_id, True, batch_info)
                
                if success:
                    success_count += 1
                else:
                    failed_count += 1
                
                # Small delay between downloads for serial processing
                await asyncio.sleep(0.3)
                
            except Exception as e:
                logger.error(f"Error processing message {msg_id}: {e}")
                failed_count += 1
                continue
        
        # Final summary with enhanced statistics
        total_time = time.time() - start_time
        avg_speed = total_messages / total_time if total_time > 0 else 0
        
        await batch_status.edit(
            f"✅ **R-TeleSwiftBot💖 Batch Complete!**\n\n"
            f"📊 **Final Statistics:**\n"
            f"📦 **Total Messages:** `{total_messages}`\n"
            f"✅ **Successful:** `{success_count}`\n"
            f"❌ **Failed:** `{failed_count}`\n"
            f"📈 **Success Rate:** `{success_count/total_messages*100:.1f}%`\n\n"
            f"⏱️ **Performance:**\n"
            f"🕐 **Total Time:** `{time.strftime('%M:%S', time.gmtime(total_time))}`\n"
            f"⚡ **Average Speed:** `{avg_speed:.1f} msg/s`\n\n"
            f"🎉 **Serial batch processing completed!**\n"
            f"💖 **Powered by R-TeleSwiftBot**"
        )
        
    except Exception as e:
        logger.error(f"Error in batch download: {e}")
        await message.reply_text(f"❌ **Batch download error:** `{str(e)[:100]}`")
    finally:
        SerialBatchManager.clear_batch(user_id)

# Enhanced callback query handler
@Client.on_callback_query()
async def callback_handler(client, callback_query):
    """Handle callback queries with new features"""
    try:
        data = callback_query.data
        
        if data == "start":
            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📖 Help", callback_data="help"),
                    InlineKeyboardButton("⚡ Features", callback_data="features")
                ],
                [
                    InlineKeyboardButton("📢 Channel", url="https://t.me/Tech_VJ"),
                    InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/VJ_Botz")
                ]
            ])
            
            await callback_query.edit_message_text(
                START_TXT.format(user_mention=callback_query.from_user.mention),
                reply_markup=buttons
            )
            
        elif data == "help":
            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🏠 Home", callback_data="start"),
                    InlineKeyboardButton("⚡ Features", callback_data="features")
                ],
                [InlineKeyboardButton("📢 Channel", url="https://t.me/Tech_VJ")]
            ])
            
            await callback_query.edit_message_text(HELP_TXT, reply_markup=buttons)
            
        elif data == "features":
            features_text = (
                f"⚡ **R-TeleSwiftBot💖 Features**\n\n"
                f"🚀 **Ultra-Fast Downloads**\n"
                f"• High-speed serial processing\n"
                f"• Real-time progress tracking\n"
                f"• Optimized for large files\n\n"
                f"📦 **True Serial Batch Processing**\n"
                f"• Download up to {MAX_BATCH_SIZE} messages one by one\n"
                f"• Smart progress monitoring\n"
                f"• Instant cancellation support\n\n"
                f"🔒 **Security**\n"
                f"• Secure session management\n"
                f"• No data logging\n"
                f"• Privacy focused\n\n"
                f"💾 **Smart Features**\n"
                f"• Original caption preservation\n"
                f"• Auto cleanup\n"
                f"• Optimized thumbnails\n"
                f"• Space efficient\n\n"
                f"💖 **R-TeleSwiftBot Ultra High Speed Mode**"
            )
            
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Home", callback_data="start")]
            ])
            
            await callback_query.edit_message_text(features_text, reply_markup=buttons)
        
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error in callback handler: {e}")
        await callback_query.answer("❌ An error occurred", show_alert=True)

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
                               
