# Don't Remove Credit Tg - @VJ_Botz  
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import asyncio 
import logging
import time
import io
from PIL import Image
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

async def extract_high_quality_thumbnail(client, message):
    """Extract highest quality thumbnail from message - FIXED VERSION"""
    try:
        thumbnail_path = None
        
        # Create thumbnails directory
        os.makedirs("thumbnails", exist_ok=True)
        
        # Extract thumbnail based on media type
        if message.photo:
            # For photos - download the original and create thumbnail
            try:
                # Download original photo
                photo_path = await message.download(file_name=f"thumbnails/temp_photo_{int(time.time())}.jpg")
                if photo_path and os.path.exists(photo_path):
                    # Create high quality thumbnail using PIL
                    with Image.open(photo_path) as img:
                        # Convert to RGB if necessary
                        if img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")
                        
                        # Create high quality thumbnail (320x320 max)
                        img.thumbnail((320, 320), Image.Resampling.LANCZOS)
                        
                        # Save as high quality JPEG
                        thumbnail_path = f"thumbnails/thumb_{int(time.time())}.jpg"
                        img.save(thumbnail_path, "JPEG", quality=95, optimize=True)
                    
                    # Clean up original
                    await safe_delete_file(photo_path)
                    
            except Exception as e:
                logger.error(f"Photo thumbnail error: {e}")
        
        elif message.video:
            # For videos - try to get video thumbnail
            try:
                if hasattr(message.video, 'thumbs') and message.video.thumbs:
                    # Find largest thumbnail
                    largest_thumb = max(message.video.thumbs, 
                                      key=lambda x: getattr(x, 'file_size', 0) or (getattr(x, 'width', 0) * getattr(x, 'height', 0)))
                    
                    # Download the thumbnail
                    thumb_path = await client.download_media(
                        message, 
                        file_name=f"thumbnails/temp_thumb_{int(time.time())}.jpg",
                        thumb=largest_thumb.file_id
                    )
                    
                    if thumb_path and os.path.exists(thumb_path):
                        # Enhance thumbnail quality with PIL
                        with Image.open(thumb_path) as img:
                            # Convert to RGB if necessary
                            if img.mode in ("RGBA", "P"):
                                img = img.convert("RGB")
                            
                            # Enhance and resize
                            img.thumbnail((320, 320), Image.Resampling.LANCZOS)
                            
                            # Save as high quality
                            thumbnail_path = f"thumbnails/thumb_{int(time.time())}.jpg"
                            img.save(thumbnail_path, "JPEG", quality=95, optimize=True)
                        
                        # Clean up temp file
                        await safe_delete_file(thumb_path)
                        
            except Exception as e:
                logger.error(f"Video thumbnail error: {e}")
        
        elif message.animation:
            # For animations/GIFs
            try:
                if hasattr(message.animation, 'thumbs') and message.animation.thumbs:
                    largest_thumb = max(message.animation.thumbs, 
                                      key=lambda x: getattr(x, 'file_size', 0) or (getattr(x, 'width', 0) * getattr(x, 'height', 0)))
                    
                    thumb_path = await client.download_media(
                        message, 
                        file_name=f"thumbnails/temp_thumb_{int(time.time())}.jpg",
                        thumb=largest_thumb.file_id
                    )
                    
                    if thumb_path and os.path.exists(thumb_path):
                        with Image.open(thumb_path) as img:
                            if img.mode in ("RGBA", "P"):
                                img = img.convert("RGB")
                            img.thumbnail((320, 320), Image.Resampling.LANCZOS)
                            thumbnail_path = f"thumbnails/thumb_{int(time.time())}.jpg"
                            img.save(thumbnail_path, "JPEG", quality=95, optimize=True)
                        await safe_delete_file(thumb_path)
                        
            except Exception as e:
                logger.error(f"Animation thumbnail error: {e}")
        
        elif message.document:
            # For documents with thumbnails
            try:
                if hasattr(message.document, 'thumbs') and message.document.thumbs:
                    largest_thumb = max(message.document.thumbs, 
                                      key=lambda x: getattr(x, 'file_size', 0) or (getattr(x, 'width', 0) * getattr(x, 'height', 0)))
                    
                    thumb_path = await client.download_media(
                        message, 
                        file_name=f"thumbnails/temp_thumb_{int(time.time())}.jpg",
                        thumb=largest_thumb.file_id
                    )
                    
                    if thumb_path and os.path.exists(thumb_path):
                        with Image.open(thumb_path) as img:
                            if img.mode in ("RGBA", "P"):
                                img = img.convert("RGB")
                            img.thumbnail((320, 320), Image.Resampling.LANCZOS)
                            thumbnail_path = f"thumbnails/thumb_{int(time.time())}.jpg"
                            img.save(thumbnail_path, "JPEG", quality=95, optimize=True)
                        await safe_delete_file(thumb_path)
                        
            except Exception as e:
                logger.error(f"Document thumbnail error: {e}")
        
        # Return the high quality thumbnail path
        if thumbnail_path and os.path.exists(thumbnail_path):
            logger.info(f"High quality thumbnail created: {thumbnail_path}")
            return thumbnail_path
        else:
            logger.debug("No thumbnail available for this message")
            return None
            
    except Exception as e:
        logger.error(f"Thumbnail extraction error: {e}")
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
        
        # Update only when significant change or every 1.5 seconds
        if progress_key in progress_data:
            last_update_time, last_percentage = progress_data[progress_key]
            if (current_time - last_update_time < 1.5 and 
                abs(percentage - last_percentage) < 3.0 and 
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
    """Enhanced download and send with HIGH QUALITY thumbnail support and speed tracking"""
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
        
        # Extract HIGH QUALITY thumbnail first
        status_msg = await message.edit_text("🎨 **Extracting HIGH QUALITY thumbnail...**")
        thumbnail_path = await extract_high_quality_thumbnail(user_client, original_msg)
        
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
            await safe_delete_file(thumbnail_path)
            raise asyncio.CancelledError("Operation cancelled")
        
        # Upload with progress
        await status_msg.edit_text(f"⬆️ **Starting ultra-fast upload...**\n📁 **File:** `{file_name}`")
        
        upload_start_time = time.time()
        
        # Send based on media type with HIGH QUALITY thumbnail
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
                await bot_client.send_video(
                    chat_id=user_id,
                    video=downloaded_file,
                    thumb=thumbnail_path,  # HIGH QUALITY THUMBNAIL
                    caption=f"🎥 **Video via R-TeleSwiftBot💖**\n\n📁 **Filename:** `{file_name}`",
                    progress=progress,
                    progress_args=(status_msg, "up", upload_start_time, file_name)
                )
            elif media_type == "animation":
                await bot_client.send_animation(
                    chat_id=user_id,
                    animation=downloaded_file,
                    thumb=thumbnail_path,  # HIGH QUALITY THUMBNAIL
                    caption=f"🎞️ **Animation via R-TeleSwiftBot💖**\n\n📁 **Filename:** `{file_name}`",
                    progress=progress,
                    progress_args=(status_msg, "up", upload_start_time, file_name)
                )
            elif media_type == "audio":
                await bot_client.send_audio(
                    chat_id=user_id,
                    audio=downloaded_file,
                    thumb=thumbnail_path,  # HIGH QUALITY THUMBNAIL
                    caption=f"🎵 **Audio via R-TeleSwiftBot💖**\n\n📁 **Filename:** `{file_name}`",
                    progress=progress,
                    progress_args=(status_msg, "up", upload_start_time, file_name)
                )
            else:  # document
                await bot_client.send_document(
                    chat_id=user_id,
                    document=downloaded_file,
                    thumb=thumbnail_path,  # HIGH QUALITY THUMBNAIL
                    caption=f"📄 **Document via R-TeleSwiftBot💖**\n\n📁 **Filename:** `{file_name}`",
                    progress=progress,
                    progress_args=(status_msg, "up", upload_start_time, file_name)
                )
        
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
            f"🎯 **Thumbnail:** {'✅ HIGH QUALITY' if thumbnail_path else '❌ Not Available'}\n"
            f"📊 **Status:** Ultra High Speed Mode\n\n"
            f"💖 **R-TeleSwiftBot💖 - Mission Complete!**"
        )
        
        # Clean up files
        await safe_delete_file(downloaded_file)
        await safe_delete_file(thumbnail_path)
        
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
        await safe_delete_file(thumbnail_path)
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

async def process_batch_download(bot_client, user_client, user_id, message, chat_id, start_id, end_id):
    """Process batch download with enhanced progress tracking"""
    try:
        AggressiveCancelManager.start_task(user_id, "batch", {"chat_id": chat_id, "start": start_id, "end": end_id})
        AggressiveCancelManager.clear_cancel_flag(user_id)
        
        # Validate batch size
        batch_size = end_id - start_id + 1
        if batch_size > MAX_BATCH_SIZE:
            await message.edit_text(f"❌ **Batch too large!** ({batch_size} messages)\n\nMaximum batch size: {MAX_BATCH_SIZE}")
            return
        
        # Initialize batch progress
        batch_start_time = time.time()
        completed = 0
        successful = 0
        failed = 0
        
        # Create initial status message
        status_text = (
            f"🔄 **R-TeleSwiftBot💖 Batch Download**\n\n"
            f"📂 **Processing:** {batch_size} messages\n"
            f"📊 **Progress:** {completed}/{batch_size}\n"
            f"✅ **Successful:** {successful}\n"
            f"❌ **Failed:** {failed}\n\n"
            f"⚡ **Ultra High Speed Mode Active!**"
        )
        
        batch_msg = await message.edit_text(status_text)
        
        # Process each message in the batch
        for msg_id in range(start_id, end_id + 1):
            try:
                # Check for cancellation before each download
                if AggressiveCancelManager.is_cancelled(user_id):
                    await batch_msg.edit_text("🛑 **Batch download cancelled by user!**")
                    return
                
                # Get the message
                try:
                    original_msg = await user_client.get_messages(chat_id, msg_id)
                    if not original_msg or original_msg.empty:
                        logger.debug(f"Message {msg_id} not found or empty")
                        failed += 1
                        completed += 1
                        continue
                except Exception as get_error:
                    logger.error(f"Error getting message {msg_id}: {get_error}")
                    failed += 1
                    completed += 1
                    continue
                
                # Update status for current message
                current_status = (
                    f"🔄 **R-TeleSwiftBot💖 Batch Download**\n\n"
                    f"📂 **Total:** {batch_size} messages\n"
                    f"📊 **Progress:** {completed}/{batch_size}\n"
                    f"✅ **Successful:** {successful}\n"
                    f"❌ **Failed:** {failed}\n\n"
                    f"⚡ **Current:** Message {msg_id}\n"
                    f"💖 **Ultra High Speed Processing...**"
                )
                
                try:
                    await batch_msg.edit_text(current_status)
                except:
                    pass  # Ignore edit errors
                
                # Download and send the message
                temp_msg = await bot_client.send_message(user_id, f"📥 Processing message {msg_id}...")
                
                try:
                    success = await download_and_send_media(bot_client, user_client, user_id, temp_msg, original_msg)
                    if success:
                        successful += 1
                    else:
                        failed += 1
                except Exception as download_error:
                    logger.error(f"Download error for message {msg_id}: {download_error}")
                    await temp_msg.edit_text(f"❌ **Failed to download message {msg_id}**")
                    failed += 1
                
                completed += 1
                
                # Small delay between downloads to avoid rate limits
                await asyncio.sleep(0.5)
                
            except Exception as msg_error:
                logger.error(f"Error processing message {msg_id}: {msg_error}")
                failed += 1
                completed += 1
                continue
        
        # Final batch summary
        total_time = time.time() - batch_start_time
        success_rate = (successful / batch_size) * 100 if batch_size > 0 else 0
        
        final_text = (
            f"✅ **Batch Download Complete!**\n\n"
            f"📂 **Total Messages:** {batch_size}\n"
            f"✅ **Successful:** {successful}\n"
            f"❌ **Failed:** {failed}\n"
            f"📊 **Success Rate:** {success_rate:.1f}%\n"
            f"⏱️ **Total Time:** {time.strftime('%M:%S', time.gmtime(total_time))}\n"
            f"⚡ **Avg Speed:** {successful/max(1, total_time/60):.1f} files/min\n\n"
            f"💖 **R-TeleSwiftBot💖 - Batch Complete!**"
        )
        
        await batch_msg.edit_text(final_text)
        
        logger.info(f"Batch download completed for user {user_id}: {successful}/{batch_size} successful")
        
    except Exception as e:
        logger.error(f"Batch download error: {e}")
        await message.edit_text(f"❌ **Batch download failed!**\n\nError: {str(e)[:100]}...")
    finally:
        # Clean up tracking
        if user_id in AggressiveCancelManager.USER_TASKS:
            AggressiveCancelManager.USER_TASKS[user_id] = []
        AggressiveCancelManager.clear_cancel_flag(user_id)

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
            f"✅ **All operations cancelled!**\n\n"
            f"🔄 **Cancelled tasks:** {cancelled_count}\n"
            f"🧹 **Cleanup:** Complete\n"
            f"💖 **R-TeleSwiftBot💖** ready for new tasks!"
        )
        
        logger.info(f"User {user_id} cancelled all operations - {cancelled_count} tasks")
        
    except Exception as e:
        logger.error(f"Cancel error: {e}")
        await message.reply_text("❌ **Cancel operation failed!** Please try again.")

@Client.on_message(filters.private & filters.text & ~filters.command(["start", "help", "login", "logout", "cancel"]))
async def handle_links(bot, message):
    """Handle Telegram links with enhanced batch processing"""
    try:
        await db.update_last_active(message.from_user.id)
        user_id = message.from_user.id
        text = message.text.strip()
        
        # Check if logged in
        user_data = await db.get_session(user_id)
        if not user_data:
            await message.reply_text(ERROR_MESSAGES['not_logged_in'])
            return
        
        # Validate link format
        if not is_valid_telegram_post_link(text):
            await message.reply_text(ERROR_MESSAGES['invalid_link'])
            return
        
        # Parse the link
        chat_id, start_id, end_id = parse_telegram_link(text)
        if chat_id is None:
            await message.reply_text(ERROR_MESSAGES['invalid_link'])
            return
        
        # Create user client
        try:
            user_client = await create_client_with_retry(user_data)
            AggressiveCancelManager.add_client(user_id, user_client)
        except Exception as client_error:
            await message.reply_text(f"❌ **Connection failed!**\n\n{str(client_error)}")
            return
        
        try:
            # Check if it's batch download or single
            if end_id is not None:
                # Batch download
                await message.reply_text(f"🔄 **Starting batch download...**\n\n📂 **Messages:** {start_id} to {end_id} ({end_id - start_id + 1} total)")
                await process_batch_download(bot, user_client, user_id, message, chat_id, start_id, end_id)
            else:
                # Single download
                await message.reply_text("📥 **Starting download...**")
                
                # Get the message
                original_msg = await user_client.get_messages(chat_id, start_id)
                if not original_msg or original_msg.empty:
                    await message.reply_text("❌ **Message not found or empty!**")
                    return
                
                # Download and send
                await download_and_send_media(bot, user_client, user_id, message, original_msg)
                
        finally:
            # Always disconnect client
            try:
                await user_client.disconnect()
                if user_id in AggressiveCancelManager.ACTIVE_CLIENTS:
                    del AggressiveCancelManager.ACTIVE_CLIENTS[user_id]
            except:
                pass
        
    except (ChannelPrivate, UserNotParticipant):
        await message.reply_text(ERROR_MESSAGES['access_denied'])
    except (AuthKeyUnregistered, SessionExpired, SessionRevoked):
        await message.reply_text(ERROR_MESSAGES['session_expired'])
    except Exception as e:
        logger.error(f"Handle links error: {e}")
        await message.reply_text(f"❌ **An error occurred!**\n\n{str(e)[:200]}")

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
