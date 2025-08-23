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

class BatchTemp:
    """Enhanced class to manage batch operations state"""
    IS_BATCH = {}
    USER_TASKS = {}
    CANCELLED_TASKS = set()
    
    @classmethod
    def set_batch_state(cls, user_id, state):
        cls.IS_BATCH[user_id] = state
    
    @classmethod
    def get_batch_state(cls, user_id):
        return cls.IS_BATCH.get(user_id, True)
    
    @classmethod
    def set_user_task(cls, user_id, task):
        cls.USER_TASKS[user_id] = task
        cls.CANCELLED_TASKS.discard(user_id)
    
    @classmethod
    def get_user_task(cls, user_id):
        return cls.USER_TASKS.get(user_id)
    
    @classmethod
    def clear_user_task(cls, user_id):
        if user_id in cls.USER_TASKS:
            del cls.USER_TASKS[user_id]
        cls.CANCELLED_TASKS.discard(user_id)
    
    @classmethod
    def cancel_user_task(cls, user_id):
        cls.CANCELLED_TASKS.add(user_id)
        cls.clear_user_task(user_id)
    
    @classmethod
    def is_cancelled(cls, user_id):
        return user_id in cls.CANCELLED_TASKS

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
    """Create and connect client with optimized settings for high speed"""
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
                sleep_threshold=10,  # Reduced for faster responses
                max_concurrent_transmissions=10,  # Increased for speed
                takeout=False,
                device_model="VJ Speed Bot",
                system_version="High Speed 2.0"
            )
            await asyncio.wait_for(acc.connect(), timeout=15.0)
            
            # Test connection
            await asyncio.wait_for(acc.get_me(), timeout=10.0)
            return acc
            
        except (AuthKeyUnregistered, SessionExpired, SessionRevoked):
            raise Exception("Session expired - please /logout and /login again")
        except Exception as e:
            logger.warning(f"Client connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2)
            else:
                raise Exception(f"Failed to connect: {str(e)[:100]}")

# Real-time progress tracking with enhanced interface
progress_data = {}

def create_progress_bar(percentage):
    """Create a visual progress bar"""
    filled = int(percentage // 5)  # 20 blocks for 100%
    bar = "🟩" * filled + "⬜" * (20 - filled)
    return bar

async def progress(current, total, message, type_op, start_time=None):
    """Enhanced progress callback with real-time tracking and beautiful interface"""
    try:
        if start_time is None:
            start_time = time.time()
        
        percentage = current * 100 / total
        progress_key = f"{message.chat.id}_{message.id}_{type_op}"
        
        # Throttle updates - update every 3% or every 2 seconds
        current_time = time.time()
        if progress_key in progress_data:
            last_update_time, last_percentage = progress_data[progress_key]
            if (current_time - last_update_time < 2.0 and 
                abs(percentage - last_percentage) < 3.0 and 
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
        
        # Create progress bar
        progress_bar = create_progress_bar(percentage)
        
        # Choose emoji based on operation
        emoji = "⬇️" if type_op == "down" else "⬆️"
        operation = "Downloading" if type_op == "down" else "Uploading"
        
        # Enhanced progress message
        progress_text = (
            f"{emoji} **{operation}** `{percentage:.1f}%`\n\n"
            f"{progress_bar}\n\n"
            f"📊 **Size:** `{current_mb:.1f} MB` / `{total_mb:.1f} MB`\n"
            f"⚡ **Speed:** `{speed_mb:.2f} MB/s`\n"
            f"⏱️ **ETA:** `{eta}`\n"
            f"🕐 **Elapsed:** `{time.strftime('%M:%S', time.gmtime(elapsed_time))}`"
        )
        
        # Try to edit the message
        try:
            await message.edit(progress_text)
        except Exception:
            pass  # Ignore edit errors
            
    except Exception as e:
        logger.error(f"Progress error: {e}")

async def ultra_fast_download(acc, msg, status_msg, user_id):
    """Ultra-fast download with enhanced speed and real-time tracking"""
    start_time = time.time()
    
    for attempt in range(2):  # Reduced retries for speed
        try:
            logger.info(f"High-speed download attempt {attempt + 1} for message {msg.id}")
            
            # Check if cancelled
            if BatchTemp.is_cancelled(user_id):
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
    """Get optimized thumbnail for fast processing"""
    try:
        thumbnail_path = None
        
        # Quick thumbnail extraction with timeout
        if msg.video and hasattr(msg.video, 'thumbs') and msg.video.thumbs:
            largest_thumb = max(msg.video.thumbs, key=lambda x: getattr(x, 'file_size', 0))
            thumbnail_path = await asyncio.wait_for(
                acc.download_media(largest_thumb.file_id),
                timeout=20.0
            )
        elif msg.document and hasattr(msg.document, 'thumbs') and msg.document.thumbs:
            largest_thumb = max(msg.document.thumbs, key=lambda x: getattr(x, 'file_size', 0))
            thumbnail_path = await asyncio.wait_for(
                acc.download_media(largest_thumb.file_id),
                timeout=20.0
            )
        elif msg.photo:
            thumbnail_path = await asyncio.wait_for(
                acc.download_media(msg.photo.file_id),
                timeout=20.0
            )
        
        return thumbnail_path if thumbnail_path and os.path.exists(thumbnail_path) else None
            
    except Exception as e:
        logger.error(f"Error getting thumbnail: {e}")
        return None

async def process_media_message(client, message, acc, msg, user_id):
    """Process media message with high-speed download and enhanced interface"""
    file_path = None
    thumbnail = None
    
    try:
        # Check if cancelled
        if BatchTemp.is_cancelled(user_id):
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
        
        # Enhanced status message with file info
        status_msg = await message.reply_text(
            f"🚀 **Starting High-Speed Download**\n\n"
            f"📁 **File:** `{filename[:40]}...`\n"
            f"📊 **Size:** `{file_size/1024/1024:.1f} MB`\n"
            f"⚡ **Mode:** `Ultra Fast`"
        )
        
        try:
            # High-speed download
            file_path = await ultra_fast_download(acc, msg, status_msg, user_id)
            
            if not file_path or not os.path.exists(file_path):
                await status_msg.edit("❌ **Download failed - file not accessible**")
                return False
            
            # Check if cancelled after download
            if BatchTemp.is_cancelled(user_id):
                await safe_delete_file(file_path)
                await status_msg.edit("🛑 **Operation cancelled**")
                return False
            
            # Get thumbnail quickly
            thumbnail = await get_optimized_thumbnail(acc, msg)
            
            # Enhanced upload status
            await status_msg.edit(
                f"⬆️ **Starting Ultra Upload**\n\n"
                f"📁 **File:** `{filename[:40]}...`\n"
                f"⚡ **Mode:** `High Speed`"
            )
            
            # Upload with real-time progress
            start_time = time.time()
            caption = f"📎 **{filename}**\n\n✅ **Downloaded successfully via VJ Speed Bot!**"
            
            if msg.document:
                await client.send_document(
                    message.chat.id,
                    file_path,
                    thumb=thumbnail,
                    caption=caption,
                    progress=progress,
                    progress_args=[status_msg, "up", start_time]
                )
            elif msg.video:
                await client.send_video(
                    message.chat.id,
                    file_path,
                    thumb=thumbnail,
                    caption=caption,
                    progress=progress,
                    progress_args=[status_msg, "up", start_time]
                )
            elif msg.photo:
                await client.send_photo(
                    message.chat.id,
                    file_path,
                    caption=caption
                )
            elif msg.audio:
                await client.send_audio(
                    message.chat.id,
                    file_path,
                    thumb=thumbnail,
                    caption=caption,
                    progress=progress,
                    progress_args=[status_msg, "up", start_time]
                )
            
            # Success message
            await status_msg.edit(
                f"✅ **Upload Completed Successfully!**\n\n"
                f"📁 **File:** `{filename}`\n"
                f"⚡ **Total Time:** `{time.time() - start_time:.1f}s`"
            )
            
            # Auto-delete status after 10 seconds
            asyncio.create_task(delete_message_after_delay(status_msg, 10))
            
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
        await message.reply_text(f"❌ **Processing error:** `{str(e)[:100]}`")
        return False
    finally:
        # Clean up files
        if file_path:
            await safe_delete_file(file_path)
        if thumbnail:
            await safe_delete_file(thumbnail)

async def delete_message_after_delay(message, delay):
    """Delete message after specified delay"""
    try:
        await asyncio.sleep(delay)
        await message.delete()
    except Exception:
        pass

async def process_single_message(client, message, datas, msgid):
    """Process a single message for download with enhanced error handling"""
    acc = None
    try:
        user_id = message.from_user.id
        
        # Check if user has active task
        if BatchTemp.get_user_task(user_id):
            await message.reply_text(
                "⏳ **Another task is in progress**\n\n"
                "Please wait for completion or use /cancel to stop"
            )
            return False
        
        # Set user task
        BatchTemp.set_user_task(user_id, "single_download")
        
        # Get user session
        user_data = await db.get_session(user_id)
        if user_data is None:
            await message.reply_text(ERROR_MESSAGES['not_logged_in'])
            return False
        
        # Create client connection
        try:
            acc = await create_client_with_retry(user_data)
        except Exception as e:
            error_msg = str(e)
            if "Session expired" in error_msg or "invalid" in error_msg:
                await message.reply_text(ERROR_MESSAGES['session_expired'])
                await db.set_session(user_id, None)
            else:
                await message.reply_text(f"❌ **Connection error:** `{error_msg[:100]}`")
            return False
        
        # Determine chat ID
        try:
            if "/c/" in message.text:
                chat_id = int("-100" + str(datas[4]))
            else:
                chat_id = datas[3]
        except (ValueError, IndexError):
            await message.reply_text(ERROR_MESSAGES['invalid_link'])
            return False
        
        # Get the message
        try:
            msg = await asyncio.wait_for(
                acc.get_messages(chat_id, msgid),
                timeout=30.0
            )
            
            if not msg:
                await message.reply_text("❌ **Message not found or access denied**")
                return False
                
        except ChannelPrivate:
            await message.reply_text(ERROR_MESSAGES['access_denied'])
            return False
        except Exception as e:
            logger.error(f"Error getting message: {e}")
            await message.reply_text(f"❌ **Failed to access message:** `{str(e)[:100]}`")
            return False
        
        # Process the message
        success = await process_media_message(client, message, acc, msg, user_id)
        return success
        
    except Exception as e:
        logger.error(f"Error in process_single_message: {e}")
        await message.reply_text(f"❌ **Processing error:** `{str(e)[:100]}`")
        return False
    finally:
        # Clean up
        BatchTemp.clear_user_task(message.from_user.id)
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

# Cancel command
@Client.on_message(filters.command("cancel") & filters.private)
async def cancel_command(client, message):
    """Handle cancel command with immediate response"""
    try:
        user_id = message.from_user.id
        
        if BatchTemp.get_user_task(user_id):
            BatchTemp.cancel_user_task(user_id)
            await message.reply_text(
                "🛑 **Operation cancelled successfully!**\n\n"
                "All downloads and uploads have been stopped."
            )
        else:
            await message.reply_text(
                "❌ **No active operation to cancel**\n\n"
                "You don't have any running downloads or uploads."
            )
            
    except Exception as e:
        logger.error(f"Error in cancel command: {e}")
        await message.reply_text("❌ An error occurred while cancelling.")

# Handle Telegram links with enhanced batch support
@Client.on_message(filters.private & filters.text)
async def handle_links(client, message):
    """Handle Telegram post links with enhanced batch processing"""
    try:
        if message.text.startswith('/'):
            return  # Ignore commands
        
        text = message.text.strip()
        
        if not is_valid_telegram_post_link(text):
            await message.reply_text(ERROR_MESSAGES['invalid_link'])
            return
        
        await db.update_last_active(message.from_user.id)
        
        # Parse the link
        datas = text.split("/")
        
        # Check for batch download
        if "-" in datas[-1]:
            # Handle batch download
            await handle_batch_download(client, message, datas)
        else:
            # Handle single download
            try:
                msgid = int(datas[-1])
                await process_single_message(client, message, datas, msgid)
            except ValueError:
                await message.reply_text("❌ **Invalid message ID in the link**")
        
    except Exception as e:
        logger.error(f"Error handling link: {e}")
        await message.reply_text(f"❌ **Link processing error:** `{str(e)[:100]}`")

async def handle_batch_download(client, message, datas):
    """Enhanced batch download with real-time progress and speed optimization"""
    user_id = message.from_user.id
    
    try:
        # Extract range
        range_part = datas[-1]
        start_msg, end_msg = map(int, range_part.split("-"))
        
        total_messages = end_msg - start_msg + 1
        
        if total_messages > MAX_BATCH_SIZE:
            await message.reply_text(
                f"❌ **Batch size too large!**\n\n"
                f"📊 **Requested:** `{total_messages} messages`\n"
                f"📏 **Max allowed:** `{MAX_BATCH_SIZE} messages`\n\n"
                f"💡 **Tip:** Split into smaller batches"
            )
            return
        
        # Set batch task
        BatchTemp.set_user_task(user_id, "batch_download")
        
        # Enhanced batch status
        batch_status = await message.reply_text(
            f"🚀 **Starting High-Speed Batch Download**\n\n"
            f"📦 **Total Messages:** `{total_messages}`\n"
            f"🔢 **Range:** `{start_msg}` → `{end_msg}`\n"
            f"⚡ **Mode:** `Ultra Fast Batch`\n"
            f"🛑 **Use /cancel to stop**"
        )
        
        success_count = 0
        failed_count = 0
        start_time = time.time()
        
        for i, msg_id in enumerate(range(start_msg, end_msg + 1), 1):
            try:
                # Check if cancelled
                if BatchTemp.is_cancelled(user_id):
                    await batch_status.edit(
                        f"🛑 **Batch Download Cancelled**\n\n"
                        f"📊 **Processed:** `{i-1}/{total_messages}`\n"
                        f"✅ **Success:** `{success_count}`\n"
                        f"❌ **Failed:** `{failed_count}`"
                    )
                    return
                
                # Update progress every 5 messages or at start/end
                if i % 5 == 0 or i == 1 or i == total_messages:
                    elapsed = time.time() - start_time
                    rate = i / elapsed if elapsed > 0 else 0
                    eta_seconds = (total_messages - i) / rate if rate > 0 else 0
                    eta = time.strftime('%M:%S', time.gmtime(eta_seconds)) if eta_seconds < 3600 else "∞"
                    
                    progress_bar = create_progress_bar((i / total_messages) * 100)
                    
                    await batch_status.edit(
                        f"🚀 **High-Speed Batch Download**\n\n"
                        f"{progress_bar}\n\n"
                        f"📊 **Progress:** `{i}/{total_messages}` ({i/total_messages*100:.1f}%)\n"
                        f"✅ **Success:** `{success_count}`\n"
                        f"❌ **Failed:** `{failed_count}`\n"
                        f"⚡ **Speed:** `{rate:.1f} msg/s`\n"
                        f"⏱️ **ETA:** `{eta}`\n\n"
                        f"🔄 **Current:** `Message {msg_id}`"
                    )
                
                success = await process_single_message(client, message, datas, msg_id)
                if success:
                    success_count += 1
                else:
                    failed_count += 1
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error processing message {msg_id}: {e}")
                failed_count += 1
                continue
        
        # Final summary with enhanced statistics
        total_time = time.time() - start_time
        avg_speed = total_messages / total_time if total_time > 0 else 0
        
        await batch_status.edit(
            f"✅ **Batch Download Completed!**\n\n"
            f"📊 **Final Statistics:**\n"
            f"📦 **Total Messages:** `{total_messages}`\n"
            f"✅ **Successful:** `{success_count}`\n"
            f"❌ **Failed:** `{failed_count}`\n"
            f"📈 **Success Rate:** `{success_count/total_messages*100:.1f}%`\n\n"
            f"⏱️ **Performance:**\n"
            f"🕐 **Total Time:** `{time.strftime('%M:%S', time.gmtime(total_time))}`\n"
            f"⚡ **Average Speed:** `{avg_speed:.1f} msg/s`\n\n"
            f"🎉 **Batch processing completed successfully!**"
        )
        
    except Exception as e:
        logger.error(f"Error in batch download: {e}")
        await message.reply_text(f"❌ **Batch download error:** `{str(e)[:100]}`")
    finally:
        BatchTemp.clear_user_task(user_id)

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
                f"⚡ **VJ Speed Bot Features**\n\n"
                f"🚀 **Ultra-Fast Downloads**\n"
                f"• High-speed parallel processing\n"
                f"• Real-time progress tracking\n"
                f"• Optimized for large files\n\n"
                f"📦 **Batch Processing**\n"
                f"• Download up to {MAX_BATCH_SIZE} messages at once\n"
                f"• Smart progress monitoring\n"
                f"• Cancellation support\n\n"
                f"🔒 **Security**\n"
                f"• Secure session management\n"
                f"• No data logging\n"
                f"• Privacy focused\n\n"
                f"💾 **Smart Storage**\n"
                f"• Auto cleanup\n"
                f"• Optimized thumbnails\n"
                f"• Space efficient"
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
