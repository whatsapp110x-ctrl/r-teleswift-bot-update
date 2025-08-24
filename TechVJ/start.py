# Don't Remove Credit Tg - @VJ_Botz  
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import asyncio 
import logging
import time
import io
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
    MAX_RETRIES, RETRY_DELAY, SLEEP_THRESHOLD, ADMINS, THUMBNAIL_QUALITY
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

class AggressiveCancelManager:
    """Enhanced aggressive cancellation manager for instant stop"""
    USER_TASKS = {}
    CANCEL_FLAGS = {}
    ACTIVE_DOWNLOADS = {}
    ACTIVE_UPLOADS = {}
    ACTIVE_CLIENTS = {}
    
    @classmethod
    def start_task(cls, user_id, task_type, task_info):
        """Start tracking a task for user"""
        if user_id not in cls.USER_TASKS:
            cls.USER_TASKS[user_id] = []
        cls.USER_TASKS[user_id].append({'type': task_type, 'info': task_info})
        cls.CANCEL_FLAGS[user_id] = False
    
    @classmethod
    def add_download(cls, user_id, task):
        """Add active download task"""
        if user_id not in cls.ACTIVE_DOWNLOADS:
            cls.ACTIVE_DOWNLOADS[user_id] = []
        cls.ACTIVE_DOWNLOADS[user_id].append(task)
    
    @classmethod
    def add_upload(cls, user_id, task):
        """Add active upload task"""
        if user_id not in cls.ACTIVE_UPLOADS:
            cls.ACTIVE_UPLOADS[user_id] = []
        cls.ACTIVE_UPLOADS[user_id].append(task)
    
    @classmethod
    def add_client(cls, user_id, client):
        """Add active client for cleanup"""
        cls.ACTIVE_CLIENTS[user_id] = client
    
    @classmethod
    def is_active(cls, user_id):
        """Check if user has any active tasks"""
        return (user_id in cls.USER_TASKS and len(cls.USER_TASKS[user_id]) > 0) or \
               (user_id in cls.ACTIVE_DOWNLOADS and len(cls.ACTIVE_DOWNLOADS[user_id]) > 0) or \
               (user_id in cls.ACTIVE_UPLOADS and len(cls.ACTIVE_UPLOADS[user_id]) > 0)
    
    @classmethod
    async def aggressive_cancel_all(cls, user_id):
        """Aggressively cancel ALL operations for user"""
        logger.info(f"AGGRESSIVE CANCEL initiated for user {user_id}")
        
        # Set cancel flag immediately
        cls.CANCEL_FLAGS[user_id] = True
        
        cancelled_tasks = 0
        
        # Cancel all download tasks
        if user_id in cls.ACTIVE_DOWNLOADS:
            for task in cls.ACTIVE_DOWNLOADS[user_id]:
                try:
                    if hasattr(task, 'cancel'):
                        task.cancel()
                        cancelled_tasks += 1
                    elif hasattr(task, 'close'):
                        await task.close()
                        cancelled_tasks += 1
                except Exception as e:
                    logger.warning(f"Error cancelling download task: {e}")
            cls.ACTIVE_DOWNLOADS[user_id] = []
        
        # Cancel all upload tasks
        if user_id in cls.ACTIVE_UPLOADS:
            for task in cls.ACTIVE_UPLOADS[user_id]:
                try:
                    if hasattr(task, 'cancel'):
                        task.cancel()
                        cancelled_tasks += 1
                    elif hasattr(task, 'close'):
                        await task.close()
                        cancelled_tasks += 1
                except Exception as e:
                    logger.warning(f"Error cancelling upload task: {e}")
            cls.ACTIVE_UPLOADS[user_id] = []
        
        # Disconnect client if active
        if user_id in cls.ACTIVE_CLIENTS:
            try:
                client = cls.ACTIVE_CLIENTS[user_id]
                if client and hasattr(client, 'disconnect'):
                    await client.disconnect()
                    logger.info(f"Client disconnected for user {user_id}")
            except Exception as e:
                logger.warning(f"Error disconnecting client: {e}")
            finally:
                del cls.ACTIVE_CLIENTS[user_id]
        
        # Clear all user tasks
        if user_id in cls.USER_TASKS:
            cls.USER_TASKS[user_id] = []
        
        logger.info(f"AGGRESSIVE CANCEL completed for user {user_id} - {cancelled_tasks} tasks cancelled")
        return cancelled_tasks
    
    @classmethod
    def is_cancelled(cls, user_id):
        """Check if user operations are cancelled"""
        return cls.CANCEL_FLAGS.get(user_id, False)
    
    @classmethod
    def clear_cancel_flag(cls, user_id):
        """Clear cancel flag"""
        cls.CANCEL_FLAGS[user_id] = False
    
    @classmethod
    def remove_download(cls, user_id, task):
        """Remove completed download task"""
        if user_id in cls.ACTIVE_DOWNLOADS and task in cls.ACTIVE_DOWNLOADS[user_id]:
            cls.ACTIVE_DOWNLOADS[user_id].remove(task)
    
    @classmethod
    def remove_upload(cls, user_id, task):
        """Remove completed upload task"""
        if user_id in cls.ACTIVE_UPLOADS and task in cls.ACTIVE_UPLOADS[user_id]:
            cls.ACTIVE_UPLOADS[user_id].remove(task)

async def safe_delete_file(file_path):
    """Safely delete a file"""
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"Deleted file: {file_path}")
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {e}")

async def extract_thumbnail(message):
    """Extract high-quality thumbnail from message using Pyrogram's built-in methods"""
    try:
        thumbnail_data = None
        temp_thumb_file = None
        
        # Try to get thumbnail from message
        if message.photo:
            # For photos, download the highest quality available but smaller size for thumbnail
            if hasattr(message.photo, 'thumbs') and message.photo.thumbs:
                # Get the largest thumbnail (not the full photo)
                largest_thumb = max(message.photo.thumbs, key=lambda x: x.width * x.height)
                temp_thumb_file = await message.download(thumb_size="m")  # Medium thumbnail
            else:
                # Fallback: download small version of photo
                temp_thumb_file = await message.download(thumb_size="s")
        
        elif message.video:
            # For videos, use video thumbnail
            if hasattr(message.video, 'thumbs') and message.video.thumbs:
                # Get the largest thumbnail available
                temp_thumb_file = await message.download(thumb_size="m")
            elif message.video.thumb:
                # Download the video thumbnail
                temp_thumb_file = await message.download(thumb_size="m")
        
        elif message.animation:
            # For GIFs/animations
            if hasattr(message.animation, 'thumbs') and message.animation.thumbs:
                temp_thumb_file = await message.download(thumb_size="m")
            elif message.animation.thumb:
                temp_thumb_file = await message.download(thumb_size="m")
        
        elif message.document:
            # For documents with thumbnails
            if hasattr(message.document, 'thumbs') and message.document.thumbs:
                temp_thumb_file = await message.download(thumb_size="m")
            elif message.document.thumb:
                temp_thumb_file = await message.download(thumb_size="m")
        
        # Read thumbnail data if file was downloaded
        if temp_thumb_file and os.path.exists(temp_thumb_file):
            with open(temp_thumb_file, 'rb') as f:
                thumbnail_data = f.read()
            # Clean up temp file
            await safe_delete_file(temp_thumb_file)
            logger.debug(f"Successfully extracted thumbnail: {len(thumbnail_data)} bytes")
            return thumbnail_data
        
        logger.debug("No thumbnail available for this message")
        return None
        
    except Exception as e:
        logger.error(f"Error extracting thumbnail: {e}")
        # Clean up temp file if it exists
        if temp_thumb_file and os.path.exists(temp_thumb_file):
            await safe_delete_file(temp_thumb_file)
        return None

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

# Enhanced progress tracking with speed calculation
progress_data = {}
speed_data = {}

def create_progress_bar(percentage):
    """Create an enhanced visual progress bar"""
    filled = int(percentage // 5)  # 20 blocks for 100%
    bar = "🟩" * filled + "⬜" * (20 - filled)
    return bar

def calculate_speed(current, start_time, last_current=0, last_time=None):
    """Calculate real-time download/upload speed"""
    try:
        current_time = time.time()
        if last_time and last_current and current > last_current:
            # Calculate speed based on recent progress
            time_diff = current_time - last_time
            bytes_diff = current - last_current
            if time_diff > 0:
                speed = bytes_diff / time_diff
                return speed, current_time
        
        # Fallback to overall speed
        total_time = current_time - start_time
        if total_time > 0:
            speed = current / total_time
            return speed, current_time
        return 0, current_time
    except:
        return 0, time.time()

async def progress(current, total, message, type_op, start_time=None, filename=""):
    """Ultra-enhanced progress callback with real-time speed tracking"""
    try:
        # Check for cancellation immediately
        user_id = message.chat.id
        if AggressiveCancelManager.is_cancelled(user_id):
            logger.info(f"Progress cancelled for user {user_id}")
            raise asyncio.CancelledError("Operation cancelled by user")
        
        if start_time is None:
            start_time = time.time()
        
        percentage = current * 100 / total
        progress_key = f"{message.chat.id}_{message.id}_{type_op}"
        
        # Enhanced speed calculation with real-time tracking
        current_time = time.time()
        if progress_key in speed_data:
            last_current, last_time = speed_data[progress_key]
            speed, _ = calculate_speed(current, start_time, last_current, last_time)
        else:
            speed, _ = calculate_speed(current, start_time)
        
        # Store current data for next calculation
        speed_data[progress_key] = (current, current_time)
        
        # Update only when significant change or every 2 seconds
        if progress_key in progress_data:
            last_update_time, last_percentage = progress_data[progress_key]
            if (current_time - last_update_time < 2.0 and 
                abs(percentage - last_percentage) < 5.0 and 
                percentage < 100):
                return
        
        progress_data[progress_key] = (current_time, percentage)
        
        # Calculate ETA
        elapsed_time = current_time - start_time
        if speed > 0 and current > 0:
            eta_seconds = (total - current) / speed
            eta = time.strftime('%M:%S', time.gmtime(eta_seconds)) if eta_seconds < 3600 else "∞"
        else:
            eta = "Calculating..."
        
        # Convert sizes to human readable
        current_mb = current / (1024 * 1024)
        total_mb = total / (1024 * 1024)
        speed_mb = speed / (1024 * 1024)
        
        # Create enhanced progress bar
        progress_bar = create_progress_bar(percentage)
        
        # Enhanced emoji and operation text with speed indicators
        if type_op == "down":
            emoji = "⬇️"
            operation = "Downloading"
            if speed_mb > 10:
                speed_indicator = "🚀"
            elif speed_mb > 5:
                speed_indicator = "⚡"
            elif speed_mb > 1:
                speed_indicator = "📥"
            else:
                speed_indicator = "🐌"
        else:
            emoji = "⬆️" 
            operation = "Uploading"
            if speed_mb > 5:
                speed_indicator = "🚀"
            elif speed_mb > 2:
                speed_indicator = "⚡"
            elif speed_mb > 0.5:
                speed_indicator = "📤"
            else:
                speed_indicator = "🐌"
        
        # Create filename display (truncated if too long)
        file_display = filename[:25] + "..." if len(filename) > 25 else filename
        
        # Enhanced progress message with real-time data
        progress_text = (
            f"{emoji} **R-TeleSwiftBot💖 {operation}**\n\n"
            f"📁 **File:** `{file_display}`\n"
            f"📊 **Progress:** {percentage:.1f}%\n\n"
            f"{progress_bar}\n\n"
            f"💾 **Size:** {current_mb:.1f} / {total_mb:.1f} MB\n"
            f"{speed_indicator} **Speed:** {speed_mb:.2f} MB/s\n"
            f"⏱️ **ETA:** {eta}\n"
            f"⏳ **Time:** {time.strftime('%M:%S', time.gmtime(elapsed_time))}\n\n"
            f"💖 **Ultra High Speed Mode Active!**"
        )
        
        try:
            await message.edit_text(progress_text)
        except Exception as edit_error:
            # If edit fails, it might be because message content is the same
            if "message is not modified" not in str(edit_error).lower():
                logger.debug(f"Progress edit error: {edit_error}")
        
    except asyncio.CancelledError:
        raise
    except Exception as e:
        logger.error(f"Progress update error: {e}")

async def download_and_send_media(bot_client, user_client, user_id, message, original_msg, retries=0):
    """Enhanced download and send with thumbnail support and speed tracking"""
    try:
        # Check for cancellation
        if AggressiveCancelManager.is_cancelled(user_id):
            raise asyncio.CancelledError("Operation cancelled")
        
        # Determine file info and type
        media_type = None
        file_size = 0
        file_name = None
        downloaded_file = None
        
        if original_msg.photo:
            media_type = "photo"
            file_size = original_msg.photo.file_size
            file_name = f"photo_{original_msg.photo.file_unique_id}.jpg"
        elif original_msg.video:
            media_type = "video"
            file_size = original_msg.video.file_size
            file_name = original_msg.video.file_name or f"video_{original_msg.video.file_unique_id}.mp4"
        elif original_msg.document:
            media_type = "document"
            file_size = original_msg.document.file_size
            file_name = original_msg.document.file_name or f"document_{original_msg.document.file_unique_id}"
        elif original_msg.animation:
            media_type = "animation"
            file_size = original_msg.animation.file_size
            file_name = original_msg.animation.file_name or f"animation_{original_msg.animation.file_unique_id}.gif"
        elif original_msg.audio:
            media_type = "audio"
            file_size = original_msg.audio.file_size
            file_name = original_msg.audio.file_name or f"audio_{original_msg.audio.file_unique_id}.mp3"
        else:
            # Handle text or other messages
            if original_msg.text or original_msg.caption:
                content = original_msg.text or original_msg.caption
                await bot_client.send_message(
                    chat_id=user_id,
                    text=f"📝 **Text Message via R-TeleSwiftBot💖**\n\n{content}"
                )
                await message.delete()
                return True
            else:
                await message.edit_text("❌ **Unsupported media type!**")
                return False
        
        # Check file size
        if file_size > MAX_FILE_SIZE:
            await message.edit_text(f"❌ **File too large!** ({file_size/(1024*1024):.1f} MB)\n\nMaximum size: {MAX_FILE_SIZE/(1024*1024):.1f} MB")
            return False
        
        # Extract thumbnail first
        status_msg = await message.edit_text("🔍 **Extracting high-quality thumbnail...**")
        thumbnail_data = await extract_thumbnail(original_msg)
        
        # Start download with progress
        await status_msg.edit_text(f"⬇️ **Starting ultra-fast download...**\n📁 **File:** `{file_name}`\n💾 **Size:** {file_size/(1024*1024):.1f} MB")
        
        # Ensure downloads directory exists
        os.makedirs("downloads", exist_ok=True)
        
        start_time = time.time()
        
        # Download the file with enhanced progress tracking
        downloaded_file = await original_msg.download(
            file_name=f"downloads/{file_name}",
            progress=progress,
            progress_args=(status_msg, "down", start_time, file_name)
        )
        
        # Check for cancellation after download
        if AggressiveCancelManager.is_cancelled(user_id):
            await safe_delete_file(downloaded_file)
            raise asyncio.CancelledError("Operation cancelled")
        
        # Upload with progress
        await status_msg.edit_text(f"⬆️ **Starting ultra-fast upload...**\n📁 **File:** `{file_name}`")
        
        upload_start_time = time.time()
        
        # Send based on media type with thumbnail
        try:
            if media_type == "photo":
                await bot_client.send_photo(
                    chat_id=user_id,
                    photo=downloaded_file,
                    caption=f"📸 **Photo via R-TeleSwiftBot💖**\n\n📁 **Filename:** `{file_name}`",
                    progress=progress,
                    progress_args=(status_msg, "up", upload_start_time, file_name)
                )
            elif media_type == "video":
                # Use thumbnail if available
                thumb_file = None
                if thumbnail_data:
                    thumb_file = f"thumb_{int(time.time())}.jpg"
                    with open(thumb_file, 'wb') as f:
                        f.write(thumbnail_data)
                
                await bot_client.send_video(
                    chat_id=user_id,
                    video=downloaded_file,
                    thumb=thumb_file,
                    caption=f"🎥 **Video via R-TeleSwiftBot💖**\n\n📁 **Filename:** `{file_name}`",
                    progress=progress,
                    progress_args=(status_msg, "up", upload_start_time, file_name)
                )
                
                # Clean up thumbnail file
                if thumb_file:
                    await safe_delete_file(thumb_file)
                    
            elif media_type == "animation":
                # Use thumbnail if available
                thumb_file = None
                if thumbnail_data:
                    thumb_file = f"thumb_{int(time.time())}.jpg"
                    with open(thumb_file, 'wb') as f:
                        f.write(thumbnail_data)
                
                await bot_client.send_animation(
                    chat_id=user_id,
                    animation=downloaded_file,
                    thumb=thumb_file,
                    caption=f"🎞️ **Animation via R-TeleSwiftBot💖**\n\n📁 **Filename:** `{file_name}`",
                    progress=progress,
                    progress_args=(status_msg, "up", upload_start_time, file_name)
                )
                
                # Clean up thumbnail file
                if thumb_file:
                    await safe_delete_file(thumb_file)
                    
            elif media_type == "audio":
                # Use thumbnail if available
                thumb_file = None
                if thumbnail_data:
                    thumb_file = f"thumb_{int(time.time())}.jpg"
                    with open(thumb_file, 'wb') as f:
                        f.write(thumbnail_data)
                
                await bot_client.send_audio(
                    chat_id=user_id,
                    audio=downloaded_file,
                    thumb=thumb_file,
                    caption=f"🎵 **Audio via R-TeleSwiftBot💖**\n\n📁 **Filename:** `{file_name}`",
                    progress=progress,
                    progress_args=(status_msg, "up", upload_start_time, file_name)
                )
                
                # Clean up thumbnail file
                if thumb_file:
                    await safe_delete_file(thumb_file)
                    
            else:  # document
                # Use thumbnail if available
                thumb_file = None
                if thumbnail_data:
                    thumb_file = f"thumb_{int(time.time())}.jpg"
                    with open(thumb_file, 'wb') as f:
                        f.write(thumbnail_data)
                
                await bot_client.send_document(
                    chat_id=user_id,
                    document=downloaded_file,
                    thumb=thumb_file,
                    caption=f"📄 **Document via R-TeleSwiftBot💖**\n\n📁 **Filename:** `{file_name}`",
                    progress=progress,
                    progress_args=(status_msg, "up", upload_start_time, file_name)
                )
                
                # Clean up thumbnail file
                if thumb_file:
                    await safe_delete_file(thumb_file)
        
        except Exception as upload_error:
            logger.error(f"Upload error: {upload_error}")
            await status_msg.edit_text(f"❌ **Upload failed!**\n\nError: {str(upload_error)[:100]}")
            return False
        
        # Success message with detailed stats
        total_time = time.time() - start_time
        avg_speed = file_size / total_time if total_time > 0 else 0
        avg_speed_mb = avg_speed / (1024 * 1024)
        
        await status_msg.edit_text(
            f"✅ **Transfer Complete!**\n\n"
            f"📁 **File:** `{file_name}`\n"
            f"💾 **Size:** {file_size/(1024*1024):.1f} MB\n"
            f"⏱️ **Total Time:** {time.strftime('%M:%S', time.gmtime(total_time))}\n"
            f"🚀 **Avg Speed:** {avg_speed_mb:.2f} MB/s\n"
            f"🎯 **Thumbnail:** {'✅ High Quality' if thumbnail_data else '❌ Not Available'}\n"
            f"📊 **Status:** Ultra High Speed Mode\n\n"
            f"💖 **R-TeleSwiftBot💖 - Mission Complete!**"
        )
        
        # Clean up downloaded file
        await safe_delete_file(downloaded_file)
        
        # Clean up progress tracking data
        progress_key_down = f"{user_id}_{status_msg.id}_down"
        progress_key_up = f"{user_id}_{status_msg.id}_up"
        progress_data.pop(progress_key_down, None)
        progress_data.pop(progress_key_up, None)
        speed_data.pop(progress_key_down, None)
        speed_data.pop(progress_key_up, None)
        
        # Delete status message after 15 seconds
        await asyncio.sleep(15)
        try:
            await status_msg.delete()
        except:
            pass
        
        return True
        
    except asyncio.CancelledError:
        await safe_delete_file(downloaded_file)
        raise
    except FloodWait as e:
        if retries < MAX_RETRIES:
            logger.warning(f"FloodWait {e.value}s, retrying after delay...")
            await asyncio.sleep(e.value)
            return await download_and_send_media(bot_client, user_client, user_id, message, original_msg, retries + 1)
        else:
            await message.edit_text(f"❌ **Rate limited!** Please try again after {e.value} seconds.")
            return False
    except Exception as e:
        logger.error(f"Download error: {e}")
        await message.edit_text(f"❌ **Download failed!**\n\nError: {str(e)[:100]}...")
        return False

@Client.on_message(filters.private & ~filters.forwarded & filters.command(["start"]))
async def start(bot, message):
    """Handle start command"""
    try:
        await db.update_last_active(message.from_user.id)
        user_exist = await db.is_user_exist(message.from_user.id)
        if not user_exist:
            await db.add_user(message.from_user.id, message.from_user.first_name)
            logger.info(f"New user registered: {message.from_user.id}")
        
        await message.reply_text(
            START_TXT.format(user_mention=message.from_user.mention),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📖 Help & Commands", callback_data="help")],
                [InlineKeyboardButton("🔐 Login", callback_data="login_btn")],
                [InlineKeyboardButton("💖 Developer", url="https://t.me/fightermonk110")]
            ])
        )
    except Exception as e:
        logger.error(f"Start error: {e}")
        await message.reply_text("❌ An error occurred. Please try again.")

@Client.on_message(filters.private & ~filters.forwarded & filters.command(["help"]))
async def help_command(bot, message):
    """Handle help command"""
    try:
        await db.update_last_active(message.from_user.id)
        await message.reply_text(HELP_TXT)
    except Exception as e:
        logger.error(f"Help error: {e}")
        await message.reply_text("❌ An error occurred. Please try again.")

@Client.on_message(filters.private & ~filters.forwarded & filters.command(["cancel"]))
async def cancel_operations(bot, message):
    """Handle cancel command - ENHANCED"""
    try:
        user_id = message.from_user.id
        
        # Check if user has active operations
        if not AggressiveCancelManager.is_active(user_id):
            await message.reply_text("❌ **No active operations to cancel!**")
            return
        
        # Show canceling message
        cancel_msg = await message.reply_text("🛑 **Cancelling all operations...**")
        
        # Perform aggressive cancellation
        cancelled_count = await AggressiveCancelManager.aggressive_cancel_all(user_id)
        
        await cancel_msg.edit_text(
            f"✅ **All operations cancelled successfully!**\n\n"
            f"🔄 **Cancelled tasks:** {cancelled_count}\n"
            f"🧹 **Cleanup:** Complete\n"
            f"🚀 **Status:** Ready for new operations\n\n"
            f"💖 **R-TeleSwiftBot💖** is ready!"
        )
        
        logger.info(f"User {user_id} cancelled all operations - {cancelled_count} tasks")
        
    except Exception as e:
        logger.error(f"Cancel error: {e}")
        await message.reply_text("❌ **Cancel operation failed!** Please try again.")

@Client.on_message(filters.private & filters.text & ~filters.command(["start", "help", "login", "logout", "cancel"]))
async def handle_links(bot, message):
    """Enhanced link handler with improved error handling and speed tracking"""
    try:
        user_id = message.from_user.id
        await db.update_last_active(user_id)
        
        # Clear any previous cancel flags
        AggressiveCancelManager.clear_cancel_flag(user_id)
        
        # Check if user is logged in
        session_data = await db.get_session(user_id)
        if not session_data:
            await message.reply_text(ERROR_MESSAGES['not_logged_in'])
            return
        
        # Validate telegram link
        if not is_valid_telegram_post_link(message.text):
            await message.reply_text(ERROR_MESSAGES['invalid_link'])
            return
        
        # Parse the link
        chat_id, start_msg_id, end_msg_id = parse_telegram_link(message.text)
        if not chat_id or not start_msg_id:
            await message.reply_text("❌ **Invalid link format!** Please check the link and try again.")
            return
        
        # Create client connection
        try:
            status_msg = await message.reply_text("🔄 **Connecting to Telegram...**")
            user_client = await create_client_with_retry(session_data)
            AggressiveCancelManager.add_client(user_id, user_client)
            
        except Exception as conn_error:
            await message.reply_text(f"❌ **Connection failed!**\n\n{str(conn_error)}")
            return
        
        try:
            if end_msg_id:  # Batch download
                await status_msg.edit_text(f"📦 **Serial Batch Processing**\n\n⏳ **Range:** {start_msg_id} to {end_msg_id}")
                
                # Limit batch size
                batch_size = min(end_msg_id - start_msg_id + 1, MAX_BATCH_SIZE)
                if batch_size > MAX_BATCH_SIZE:
                    await status_msg.edit_text(f"❌ **Batch too large!** Maximum: {MAX_BATCH_SIZE} messages")
                    await user_client.disconnect()
                    return
                
                # Process messages serially
                successful = 0
                failed = 0
                
                for msg_id in range(start_msg_id, start_msg_id + batch_size):
                    # Check for cancellation
                    if AggressiveCancelManager.is_cancelled(user_id):
                        await status_msg.edit_text("🛑 **Batch operation cancelled by user!**")
                        break
                    
                    try:
                        await status_msg.edit_text(f"📥 **Processing message {msg_id}** ({msg_id - start_msg_id + 1}/{batch_size})")
                        
                        original_msg = await user_client.get_messages(chat_id, msg_id)
                        if original_msg and not original_msg.empty:
                            # Start task tracking
                            AggressiveCancelManager.start_task(user_id, "download", f"msg_{msg_id}")
                            
                            result = await download_and_send_media(bot, user_client, user_id, status_msg, original_msg)
                            if result:
                                successful += 1
                            else:
                                failed += 1
                        else:
                            failed += 1
                            
                        # Small delay between messages to prevent rate limiting
                        await asyncio.sleep(1)
                        
                    except Exception as msg_error:
                        logger.error(f"Error processing message {msg_id}: {msg_error}")
                        failed += 1
                        continue
                
                # Final batch summary
                await status_msg.edit_text(
                    f"✅ **Batch Processing Complete!**\n\n"
                    f"📊 **Results:**\n"
                    f"✅ **Success:** {successful}\n"
                    f"❌ **Failed:** {failed}\n"
                    f"📦 **Total:** {successful + failed}\n\n"
                    f"💖 **R-TeleSwiftBot💖 - Serial Processing Complete!**"
                )
                
            else:  # Single message download
                try:
                    await status_msg.edit_text("📥 **Fetching message...**")
                    original_msg = await user_client.get_messages(chat_id, start_msg_id)
                    
                    if not original_msg or original_msg.empty:
                        await status_msg.edit_text("❌ **Message not found or inaccessible!**")
                        return
                    
                    # Start task tracking
                    AggressiveCancelManager.start_task(user_id, "download", f"single_{start_msg_id}")
                    
                    # Download and send
                    await download_and_send_media(bot, user_client, user_id, status_msg, original_msg)
                    
                except (ChannelPrivate, UserNotParticipant):
                    await status_msg.edit_text(ERROR_MESSAGES['access_denied'])
                except (MessageIdInvalid, ChannelInvalid):
                    await status_msg.edit_text("❌ **Message not found!** The message may have been deleted or the ID is invalid.")
                except Exception as download_error:
                    await status_msg.edit_text(f"❌ **Download failed!**\n\nError: {str(download_error)[:150]}")
        
        finally:
            # Clean up
            try:
                if user_client and hasattr(user_client, 'disconnect'):
                    await user_client.disconnect()
                AggressiveCancelManager.USER_TASKS.pop(user_id, None)
                AggressiveCancelManager.ACTIVE_CLIENTS.pop(user_id, None)
            except Exception as cleanup_error:
                logger.error(f"Cleanup error: {cleanup_error}")
    
    except Exception as e:
        logger.error(f"Handler error: {e}")
        await message.reply_text("❌ **An unexpected error occurred!** Please try again later.")

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
