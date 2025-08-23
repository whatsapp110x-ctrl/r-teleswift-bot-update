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
    PeerIdInvalid, MessageIdInvalid, ChannelInvalid
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
                int(parts[4].split('-')[0])
                return True
            except (ValueError, IndexError):
                return False
    except Exception:
        return False

class BatchQueue:
    """Enhanced serial batch download queue system"""
    USER_QUEUES = {}
    PROCESSING = set()
    CANCELLED = set()
    
    @classmethod
    def add_to_queue(cls, user_id, items):
        """Add items to user's download queue"""
        if user_id not in cls.USER_QUEUES:
            cls.USER_QUEUES[user_id] = []
        cls.USER_QUEUES[user_id].extend(items)
        cls.CANCELLED.discard(user_id)
    
    @classmethod
    def get_queue(cls, user_id):
        """Get user's download queue"""
        return cls.USER_QUEUES.get(user_id, [])
    
    @classmethod
    def clear_queue(cls, user_id):
        """Clear user's download queue"""
        if user_id in cls.USER_QUEUES:
            del cls.USER_QUEUES[user_id]
        cls.PROCESSING.discard(user_id)
        cls.CANCELLED.discard(user_id)
    
    @classmethod
    def is_processing(cls, user_id):
        """Check if user has active download"""
        return user_id in cls.PROCESSING
    
    @classmethod
    def set_processing(cls, user_id, state):
        """Set user processing state"""
        if state:
            cls.PROCESSING.add(user_id)
        else:
            cls.PROCESSING.discard(user_id)
    
    @classmethod
    def cancel_user(cls, user_id):
        """Cancel user's downloads"""
        cls.CANCELLED.add(user_id)
        cls.clear_queue(user_id)
    
    @classmethod
    def is_cancelled(cls, user_id):
        """Check if user cancelled downloads"""
        return user_id in cls.CANCELLED

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
    """Ultra-fast download with maximum speed optimization"""
    start_time = time.time()
    
    for attempt in range(2):  # Quick retry for speed
        try:
            logger.info(f"R-TeleSwiftBot💖 ultra-fast download attempt {attempt + 1} for message {msg.id}")
            
            # Check if cancelled
            if BatchQueue.is_cancelled(user_id):
                await status_msg.edit("🛑 **Download cancelled by user**")
                return None
            
            file = await acc.download_media(
                msg, 
                progress=progress, 
                progress_args=[status_msg, "down", start_time]
            )
            
            if file and os.path.exists(file):
                return file
            else:
                raise Exception("Downloaded file not found")
                
        except FloodWait as fw:
            if fw.value > 20:  # Reduced flood wait tolerance for speed
                await status_msg.edit(f"❌ **Rate limited for {fw.value}s - try again later**")
                return None
            logger.warning(f"FloodWait {fw.value}s on attempt {attempt + 1}")
            await asyncio.sleep(fw.value)
        except Exception as e:
            logger.warning(f"Download attempt {attempt + 1} failed: {e}")
            if attempt == 0:  # Only retry once for speed
                await asyncio.sleep(1)
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
                timeout=15.0  # Reduced timeout for speed
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

async def process_media_message(client, message, acc, msg, user_id):
    """Process media message with ultra-high-speed download and enhanced interface"""
    file_path = None
    thumbnail = None
    
    try:
        # Check if cancelled
        if BatchQueue.is_cancelled(user_id):
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
            await message.reply_text("❌ **No downloadable media found**")
            return False
        
        if file_size > MAX_FILE_SIZE:
            await message.reply_text(
                f"❌ **File too large!**\n\n"
                f"📊 **Size:** `{file_size/1024/1024:.1f} MB`\n"
                f"📏 **Max allowed:** `{MAX_FILE_SIZE/1024/1024:.1f} MB`"
            )
            return False
        
        # Ultra-enhanced status message
        status_msg = await message.reply_text(
            f"🚀 **R-TeleSwiftBot💖 Ultra-Fast Download**\n\n"
            f"📁 **File:** `{filename[:35]}...`\n"
            f"📊 **Size:** `{file_size/1024/1024:.1f} MB`\n"
            f"⚡ **Mode:** `Ultra High Speed`\n"
            f"💖 **Starting download...**"
        )
        
        try:
            # Ultra-fast download
            file_path = await ultra_fast_download(acc, msg, status_msg, user_id)
            
            if not file_path:
                await status_msg.edit("❌ **Download failed!** Unable to download the file.")
                return False
            
            # Check file size
            actual_size = os.path.getsize(file_path)
            if actual_size == 0:
                await status_msg.edit("❌ **Download failed!** File is empty.")
                await safe_delete_file(file_path)
                return False
            
            # Get thumbnail in parallel for speed
            thumbnail_task = asyncio.create_task(get_optimized_thumbnail(acc, msg))
            
            # Prepare upload
            await status_msg.edit(
                f"📤 **R-TeleSwiftBot💖 Ultra-Fast Upload**\n\n"
                f"📁 **File:** `{filename[:35]}...`\n"
                f"📊 **Size:** `{actual_size/1024/1024:.1f} MB`\n"
                f"💖 **Preparing ultra-fast upload...**"
            )
            
            # Get thumbnail result
            try:
                thumbnail = await asyncio.wait_for(thumbnail_task, timeout=10.0)
            except:
                thumbnail = None
            
            # Enhanced caption
            caption = (
                f"📥 **Downloaded successfully via R-TeleSwiftBot💖**\n\n"
                f"📁 **File:** `{filename}`\n"
                f"📊 **Size:** `{actual_size/1024/1024:.1f} MB`\n"
                f"💖 **Ultra High Speed Download**"
            )
            
            # Ultra-fast upload
            start_upload = time.time()
            
            if msg.document:
                await client.send_document(
                    chat_id=message.chat.id,
                    document=file_path,
                    thumb=thumbnail,
                    caption=caption,
                    progress=progress,
                    progress_args=[status_msg, "up", start_upload]
                )
            elif msg.video:
                await client.send_video(
                    chat_id=message.chat.id,
                    video=file_path,
                    thumb=thumbnail,
                    caption=caption,
                    progress=progress,
                    progress_args=[status_msg, "up", start_upload]
                )
            elif msg.photo:
                await client.send_photo(
                    chat_id=message.chat.id,
                    photo=file_path,
                    caption=caption,
                    progress=progress,
                    progress_args=[status_msg, "up", start_upload]
                )
            elif msg.audio:
                await client.send_audio(
                    chat_id=message.chat.id,
                    audio=file_path,
                    thumb=thumbnail,
                    caption=caption,
                    progress=progress,
                    progress_args=[status_msg, "up", start_upload]
                )
            
            # Success message
            total_time = time.time() - (status_msg.date.timestamp() if hasattr(status_msg, 'date') else time.time())
            await status_msg.edit(
                f"✅ **R-TeleSwiftBot💖 Ultra-Fast Complete!**\n\n"
                f"📁 **File:** `{filename}`\n"
                f"📊 **Size:** `{actual_size/1024/1024:.1f} MB`\n"
                f"⚡ **Speed:** `{(actual_size/1024/1024)/max(1, total_time):.1f} MB/s`\n"
                f"⏱️ **Time:** `{total_time:.1f}s`\n"
                f"💖 **Ultra High Speed Mode**"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Process media error: {e}")
            await status_msg.edit(f"❌ **Process failed!** {str(e)[:100]}")
            return False
            
    except Exception as e:
        logger.error(f"Media processing error: {e}")
        await message.reply_text(f"❌ **Media processing failed!** {str(e)[:100]}")
        return False
        
    finally:
        # Cleanup files
        if file_path:
            await safe_delete_file(file_path)
        if thumbnail:
            await safe_delete_file(thumbnail)

async def serial_batch_download(client, message, acc, chat_id, start_msg_id, end_msg_id, user_id):
    """Enhanced serial batch download with queue system"""
    try:
        BatchQueue.set_processing(user_id, True)
        total_messages = end_msg_id - start_msg_id + 1
        
        status_msg = await message.reply_text(
            f"📦 **R-TeleSwiftBot💖 Serial Batch Download**\n\n"
            f"📊 **Total Messages:** {total_messages}\n"
            f"⚡ **Mode:** Ultra High Speed Serial\n"
            f"🔄 **Queue:** Processing one by one\n"
            f"💖 **Starting batch download...**",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🛑 Cancel", callback_data=f"cancel_batch_{user_id}")
            ]])
        )
        
        processed = 0
        successful = 0
        failed = 0
        start_time = time.time()
        
        # Process messages serially (one by one) in queue
        for msg_id in range(start_msg_id, end_msg_id + 1):
            try:
                # Check if cancelled
                if BatchQueue.is_cancelled(user_id):
                    await status_msg.edit("🛑 **Batch download cancelled by user**")
                    break
                
                # Update progress
                processed += 1
                percentage = (processed / total_messages) * 100
                elapsed = time.time() - start_time
                eta_seconds = (elapsed / processed) * (total_messages - processed) if processed > 0 else 0
                eta = time.strftime('%M:%S', time.gmtime(eta_seconds)) if eta_seconds < 3600 else "∞"
                
                progress_bar = create_progress_bar(percentage)
                
                await status_msg.edit(
                    f"📦 **R-TeleSwiftBot💖 Serial Batch Download**\n\n"
                    f"{progress_bar}\n\n"
                    f"📊 **Progress:** `{processed}/{total_messages}` ({percentage:.1f}%)\n"
                    f"✅ **Success:** {successful}\n"
                    f"❌ **Failed:** {failed}\n"
                    f"⏱️ **ETA:** `{eta}`\n"
                    f"🔄 **Current:** Message {msg_id}\n"
                    f"💖 **Serial processing...**",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🛑 Cancel", callback_data=f"cancel_batch_{user_id}")
                    ]])
                )
                
                # Get and process message
                try:
                    msg = await acc.get_messages(chat_id, msg_id)
                    if msg and (msg.document or msg.video or msg.photo or msg.audio):
                        # Process media message serially
                        success = await process_media_message(client, message, acc, msg, user_id)
                        if success:
                            successful += 1
                        else:
                            failed += 1
                        
                        # Small delay between downloads for queue processing
                        await asyncio.sleep(0.5)
                    else:
                        failed += 1
                        
                except Exception as msg_error:
                    logger.error(f"Error processing message {msg_id}: {msg_error}")
                    failed += 1
                    continue
                    
            except Exception as e:
                logger.error(f"Error in batch processing: {e}")
                failed += 1
                continue
        
        # Final summary
        total_time = time.time() - start_time
        avg_speed = successful / max(1, total_time)
        
        final_text = (
            f"✅ **R-TeleSwiftBot💖 Batch Complete!**\n\n"
            f"📊 **Summary:**\n"
            f"📝 **Total:** {total_messages}\n"
            f"✅ **Success:** {successful}\n"
            f"❌ **Failed:** {failed}\n"
            f"⏱️ **Time:** `{total_time:.1f}s`\n"
            f"⚡ **Avg Speed:** `{avg_speed:.1f} files/sec`\n\n"
            f"💖 **Serial Queue Processing Complete!**"
        )
        
        await status_msg.edit(final_text)
        
    except Exception as e:
        logger.error(f"Serial batch download error: {e}")
        await message.reply_text(f"❌ **Batch download failed!** {str(e)[:100]}")
    finally:
        BatchQueue.set_processing(user_id, False)

@Client.on_callback_query(filters.regex(r"cancel_batch_(\d+)"))
async def cancel_batch_callback(client, callback_query):
    """Handle batch download cancellation"""
    try:
        user_id = int(callback_query.matches[0].group(1))
        if callback_query.from_user.id == user_id:
            BatchQueue.cancel_user(user_id)
            await callback_query.answer("🛑 Batch download cancelled!", show_alert=True)
            await callback_query.message.edit(
                f"🛑 **Batch Download Cancelled**\n\n"
                f"The serial batch download has been cancelled by user.\n"
                f"💖 **R-TeleSwiftBot💖**"
            )
        else:
            await callback_query.answer("❌ Not your operation!", show_alert=True)
    except Exception as e:
        logger.error(f"Cancel callback error: {e}")
        await callback_query.answer("❌ Error cancelling!", show_alert=True)

@Client.on_message(filters.private & ~filters.forwarded & filters.command(["start"]))
async def start(client, message):
    """Enhanced start command"""
    try:
        user_id = message.from_user.id
        
        # Add user to database
        if not await db.is_user_exist(user_id):
            await db.add_user(user_id, message.from_user.first_name)
        
        await db.update_last_active(user_id)
        
        # Enhanced start message
        await message.reply_text(
            START_TXT.format(user_mention=message.from_user.mention),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💖 Help", callback_data="help"),
                 InlineKeyboardButton("⚡ Login", callback_data="login")],
                [InlineKeyboardButton("📊 Stats", callback_data="stats"),
                 InlineKeyboardButton("💎 About", callback_data="about")]
            ])
        )
        
    except Exception as e:
        logger.error(f"Start command error: {e}")
        await message.reply_text("❌ **Error!** Please try again.")

@Client.on_message(filters.private & ~filters.forwarded & filters.command(["help"]))
async def help_command(client, message):
    """Enhanced help command"""
    try:
        await db.update_last_active(message.from_user.id)
        await message.reply_text(
            HELP_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="start"),
                 InlineKeyboardButton("⚡ Login", callback_data="login")]
            ])
        )
    except Exception as e:
        logger.error(f"Help command error: {e}")
        await message.reply_text("❌ **Error!** Please try again.")

@Client.on_message(filters.private & ~filters.forwarded & filters.command(["cancel"]))
async def cancel_command(client, message):
    """Enhanced cancel command"""
    try:
        user_id = message.from_user.id
        await db.update_last_active(user_id)
        
        if BatchQueue.is_processing(user_id):
            BatchQueue.cancel_user(user_id)
            await message.reply_text(
                f"🛑 **All operations cancelled!**\n\n"
                f"✅ Serial downloads stopped\n"
                f"✅ Queue cleared\n"
                f"💖 **R-TeleSwiftBot💖**"
            )
        else:
            await message.reply_text(
                f"❌ **Nothing to cancel**\n\n"
                f"No active downloads found.\n"
                f"💖 **R-TeleSwiftBot💖**"
            )
    except Exception as e:
        logger.error(f"Cancel command error: {e}")
        await message.reply_text("❌ **Error!** Please try again.")

@Client.on_message(filters.private & ~filters.forwarded & filters.text)
async def handle_message(client, message):
    """Enhanced main message handler with ultra-fast processing"""
    try:
        user_id = message.from_user.id
        await db.update_last_active(user_id)
        
        # Check if user is logged in
        user_data = await db.get_session(user_id)
        if not user_data:
            return await message.reply_text(ERROR_MESSAGES['not_logged_in'])
        
        # Check if valid Telegram link
        if not is_valid_telegram_post_link(message.text):
            return await message.reply_text(ERROR_MESSAGES['invalid_link'])
        
        # Check if user is already processing
        if BatchQueue.is_processing(user_id):
            return await message.reply_text(
                f"⚠️ **Already processing!**\n\n"
                f"You have an active download in progress.\n"
                f"Use /cancel to stop current downloads.\n"
                f"💖 **R-TeleSwiftBot💖**"
            )
        
        # Parse the link
        try:
            url = message.text.strip()
            parts = url.split('/')
            
            # Extract chat and message info
            if parts[3] == 'c':
                chat_id = int('-100' + parts[4])
                message_info = parts[5]
            elif parts[3] == 'b':
                chat_id = parts[4]
                message_info = parts[5]
            else:
                chat_id = parts[3]
                message_info = parts[4]
            
            # Check if batch download
            if '-' in message_info:
                # Batch download
                start_id, end_id = map(int, message_info.split('-'))
                if end_id - start_id + 1 > MAX_BATCH_SIZE:
                    return await message.reply_text(
                        f"❌ **Batch too large!**\n\n"
                        f"📊 **Requested:** {end_id - start_id + 1} messages\n"
                        f"📏 **Max allowed:** {MAX_BATCH_SIZE} messages\n"
                        f"💖 **R-TeleSwiftBot💖**"
                    )
                
                # Create client and start serial batch download
                acc = await create_client_with_retry(user_data)
                await serial_batch_download(client, message, acc, chat_id, start_id, end_id, user_id)
                await acc.disconnect()
                
            else:
                # Single download
                msg_id = int(message_info)
                acc = await create_client_with_retry(user_data)
                
                try:
                    msg = await acc.get_messages(chat_id, msg_id)
                    if msg and (msg.document or msg.video or msg.photo or msg.audio):
                        await process_media_message(client, message, acc, msg, user_id)
                    else:
                        await message.reply_text("❌ **No media found** in the specified message.")
                finally:
                    await acc.disconnect()
        
        except Exception as e:
            logger.error(f"Message processing error: {e}")
            await message.reply_text(f"❌ **Processing failed!** {str(e)[:100]}")
    
    except Exception as e:
        logger.error(f"Handle message error: {e}")
        await message.reply_text("❌ **Unexpected error!** Please try again.")

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
