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

async def resolve_peer_with_retry(acc, chat_id, max_retries=3):
    """Resolve peer with enhanced retry logic to fix PEER_ID_INVALID errors"""
    for attempt in range(max_retries):
        try:
            if isinstance(chat_id, str):
                # For usernames, try to get chat first
                chat = await acc.get_chat(chat_id)
                return chat.id
            else:
                # For IDs, try to get chat
                chat = await acc.get_chat(chat_id)
                return chat.id
        except PeerIdInvalid:
            if attempt < max_retries - 1:
                logger.warning(f"PeerIdInvalid attempt {attempt + 1}, retrying...")
                await asyncio.sleep(1)
                # Try alternative resolution methods
                try:
                    if isinstance(chat_id, str):
                        # Try joining/getting chat info
                        await acc.join_chat(chat_id)
                        chat = await acc.get_chat(chat_id)
                        return chat.id
                except:
                    continue
            else:
                raise PeerIdInvalid("Unable to resolve peer after retries")
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Peer resolution attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(1)
            else:
                raise e
    
    raise Exception("Failed to resolve peer")

async def ultra_fast_forward_with_progress(bot, acc, msg, user_id, status_msg, position_info=""):
    """Forward message with ultra-fast progress tracking"""
    try:
        start_time = time.time()
        
        # Get file size for progress calculation
        file_size = 0
        if msg.document:
            file_size = getattr(msg.document, 'file_size', 0)
        elif msg.video:
            file_size = getattr(msg.video, 'file_size', 0)
        elif msg.audio:
            file_size = getattr(msg.audio, 'file_size', 0)
        elif msg.photo:
            file_size = getattr(msg.photo, 'file_size', 0) if hasattr(msg.photo, 'file_size') else 0
        
        # Update status with file info
        media_type = "📄 Document" if msg.document else "🎥 Video" if msg.video else "🎵 Audio" if msg.audio else "📷 Photo" if msg.photo else "💬 Message"
        
        # Enhanced forwarding status
        await status_msg.edit(
            f"⚡ **R-TeleSwiftBot💖 Processing** {position_info}\n\n"
            f"{media_type}\n"
            f"📊 **Size:** `{file_size / (1024*1024):.1f} MB`\n"
            f"🚀 **Status:** Preparing ultra-fast forward...\n"
            f"💖 **Ultra High Speed Mode**"
        )
        
        # Check for cancellation
        if SerialBatchManager.is_cancelled(user_id):
            return False
        
        # Enhanced caption with bot branding
        original_caption = msg.caption or ""
        enhanced_caption = f"{original_caption}\n\n📥 **Downloaded via R-TeleSwiftBot💖**" if original_caption else "📥 **Downloaded via R-TeleSwiftBot💖**"
        
        # Forward message with optimized settings
        if msg.document:
            await bot.send_document(
                user_id,
                msg.document.file_id,
                caption=enhanced_caption,
                progress=progress,
                progress_args=[status_msg, "up", start_time]
            )
        elif msg.video:
            await bot.send_video(
                user_id,
                msg.video.file_id,
                caption=enhanced_caption,
                progress=progress,
                progress_args=[status_msg, "up", start_time]
            )
        elif msg.audio:
            await bot.send_audio(
                user_id,
                msg.audio.file_id,
                caption=enhanced_caption,
                progress=progress,
                progress_args=[status_msg, "up", start_time]
            )
        elif msg.photo:
            await bot.send_photo(
                user_id,
                msg.photo.file_id,
                caption=enhanced_caption
            )
        else:
            # For text messages or other types
            await bot.send_message(
                user_id,
                f"💬 **Message Content:**\n\n{msg.text or 'No text content'}\n\n📥 **Forwarded via R-TeleSwiftBot💖**"
            )
        
        return True
        
    except Exception as e:
        logger.error(f"Forward error: {e}")
        return False

@Client.on_message(filters.private & filters.text)
async def handle_telegram_links(bot, message):
    """Enhanced main handler for Telegram links with improved peer resolution"""
    try:
        await db.update_last_active(message.from_user.id)
        
        # Check if user is logged in
        user_data = await db.get_session(message.from_user.id)
        if not user_data:
            return await message.reply_text(ERROR_MESSAGES['not_logged_in'])
        
        text = message.text.strip()
        
        # Enhanced link validation
        if not is_valid_telegram_post_link(text):
            return
        
        # Parse the link with enhanced error handling
        try:
            chat_id, start_msg_id, end_msg_id = parse_telegram_link(text)
            if not chat_id or not start_msg_id:
                return await message.reply_text(ERROR_MESSAGES['invalid_link'])
        except Exception as e:
            logger.error(f"Link parsing error: {e}")
            return await message.reply_text(ERROR_MESSAGES['invalid_link'])
        
        user_id = message.from_user.id
        
        # Check for active batch operations
        if SerialBatchManager.is_active(user_id):
            return await message.reply_text(
                "⚠️ **Batch download in progress!**\n\n"
                "Please wait for the current batch to complete or use /cancel to stop it.\n\n"
                "💖 R-TeleSwiftBot💖"
            )
        
        # Determine if it's batch or single download
        is_batch = end_msg_id is not None
        
        if is_batch:
            # Validate batch size
            batch_size = end_msg_id - start_msg_id + 1
            if batch_size > MAX_BATCH_SIZE:
                return await message.reply_text(
                    f"❌ **Batch too large!**\n\n"
                    f"Maximum batch size: {MAX_BATCH_SIZE} messages\n"
                    f"Your batch size: {batch_size} messages\n\n"
                    f"Please reduce the range and try again.\n\n"
                    f"💖 R-TeleSwiftBot💖"
                )
            
            # Start batch processing
            SerialBatchManager.start_batch(user_id, {
                'chat_id': chat_id,
                'start_msg_id': start_msg_id,
                'end_msg_id': end_msg_id,
                'total': batch_size
            })
            
            await process_batch_download(bot, message, user_data, chat_id, start_msg_id, end_msg_id)
        else:
            # Single download
            await process_single_download(bot, message, user_data, chat_id, start_msg_id)
            
    except Exception as e:
        logger.error(f"Main handler error: {e}")
        await message.reply_text(ERROR_MESSAGES['unknown_error'])

async def process_single_download(bot, message, user_data, chat_id, msg_id):
    """Process single message download with enhanced peer resolution"""
    user_id = message.from_user.id
    acc = None
    
    try:
        # Create status message
        status = await message.reply_text(
            "🚀 **R-TeleSwiftBot💖 Initializing...**\n\n"
            "⚡ **Status:** Connecting to ultra-fast servers...\n"
            "💖 **Ultra High Speed Mode**"
        )
        
        # Create client with retry
        acc = await create_client_with_retry(user_data)
        
        await status.edit(
            "🔗 **R-TeleSwiftBot💖 Connected!**\n\n"
            "⚡ **Status:** Resolving channel...\n"
            "💖 **Ultra High Speed Mode**"
        )
        
        # Enhanced peer resolution
        try:
            resolved_chat_id = await resolve_peer_with_retry(acc, chat_id)
        except PeerIdInvalid:
            await status.edit(ERROR_MESSAGES['access_denied'])
            return
        except Exception as e:
            logger.error(f"Peer resolution failed: {e}")
            await status.edit(ERROR_MESSAGES['access_denied'])
            return
        
        await status.edit(
            "📡 **R-TeleSwiftBot💖 Accessing...**\n\n"
            "⚡ **Status:** Fetching message...\n"
            "💖 **Ultra High Speed Mode**"
        )
        
        # Get the message
        try:
            msg = await acc.get_messages(resolved_chat_id, msg_id)
            if not msg:
                await status.edit("❌ **Message not found!**\n\nThe message may have been deleted or doesn't exist.")
                return
        except Exception as e:
            logger.error(f"Error getting message: {e}")
            await status.edit(ERROR_MESSAGES['access_denied'])
            return
        
        # Check if message has media or text content
        if not (msg.document or msg.video or msg.audio or msg.photo or msg.text):
            await status.edit("❌ **No downloadable content!**\n\nThis message doesn't contain any media or text.")
            return
        
        # Forward the message with progress
        success = await ultra_fast_forward_with_progress(bot, acc, msg, user_id, status)
        
        if success:
            await status.edit(
                "✅ **R-TeleSwiftBot💖 Complete!**\n\n"
                "🎉 **Status:** Downloaded successfully!\n"
                "⚡ **Speed:** Ultra-fast mode\n"
                "💖 **Thank you for using R-TeleSwiftBot💖**"
            )
        else:
            await status.edit("❌ **Download failed!** Please try again.")
            
    except Exception as e:
        logger.error(f"Single download error: {e}")
        if 'status' in locals():
            await status.edit(ERROR_MESSAGES['download_failed'])
    finally:
        if acc:
            try:
                await acc.disconnect()
            except:
                pass

async def process_batch_download(bot, message, user_data, chat_id, start_msg_id, end_msg_id):
    """Process batch download with enhanced serial processing"""
    user_id = message.from_user.id
    acc = None
    
    try:
        total_messages = end_msg_id - start_msg_id + 1
        
        # Create batch status message
        status = await message.reply_text(
            f"🚀 **R-TeleSwiftBot💖 Serial Batch Started!**\n\n"
            f"📦 **Total Messages:** {total_messages}\n"
            f"⚡ **Mode:** Ultra-fast serial processing\n"
            f"🔄 **Status:** Initializing...\n\n"
            f"💖 **R-TeleSwiftBot💖 - One by one processing**"
        )
        
        # Create client
        acc = await create_client_with_retry(user_data)
        
        # Resolve peer
        try:
            resolved_chat_id = await resolve_peer_with_retry(acc, chat_id)
        except Exception as e:
            logger.error(f"Batch peer resolution failed: {e}")
            await status.edit(ERROR_MESSAGES['access_denied'])
            SerialBatchManager.clear_batch(user_id)
            return
        
        # Process messages serially
        successful = 0
        failed = 0
        
        for current_msg_id in range(start_msg_id, end_msg_id + 1):
            # Check for cancellation
            if SerialBatchManager.is_cancelled(user_id):
                await status.edit(
                    f"🛑 **R-TeleSwiftBot💖 Cancelled!**\n\n"
                    f"📊 **Progress:** {successful + failed}/{total_messages}\n"
                    f"✅ **Success:** {successful}\n"
                    f"❌ **Failed:** {failed}\n\n"
                    f"💖 **Batch operation cancelled by user**"
                )
                break
            
            try:
                # Update progress
                progress_num = current_msg_id - start_msg_id + 1
                percentage = (progress_num / total_messages) * 100
                
                # Create progress bar
                filled = int(percentage // 5)  # 20 blocks for 100%
                progress_bar = "🟩" * filled + "⬜" * (20 - filled)
                
                await status.edit(
                    f"⚡ **R-TeleSwiftBot💖 Processing** `{percentage:.1f}%`\n\n"
                    f"{progress_bar}\n\n"
                    f"📦 **Processing:** {progress_num}/{total_messages}\n"
                    f"🔢 **Current ID:** {current_msg_id}\n"
                    f"✅ **Success:** {successful}\n"
                    f"❌ **Failed:** {failed}\n\n"
                    f"💖 **Ultra-fast serial processing...**"
                )
                
                # Get and process message
                try:
                    msg = await acc.get_messages(resolved_chat_id, current_msg_id)
                    if msg and (msg.document or msg.video or msg.audio or msg.photo or msg.text):
                        # Forward message
                        forward_success = await ultra_fast_forward_with_progress(
                            bot, acc, msg, user_id, status, 
                            f"({progress_num}/{total_messages})"
                        )
                        if forward_success:
                            successful += 1
                        else:
                            failed += 1
                    else:
                        failed += 1  # Message not found or no content
                        
                except Exception as msg_error:
                    logger.warning(f"Error processing message {current_msg_id}: {msg_error}")
                    failed += 1
                
                # Small delay between messages for stability
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error processing message {current_msg_id}: {e}")
                failed += 1
        
        # Final summary
        if not SerialBatchManager.is_cancelled(user_id):
            success_rate = (successful / total_messages) * 100 if total_messages > 0 else 0
            await status.edit(
                f"✅ **R-TeleSwiftBot💖 Batch Complete!**\n\n"
                f"📊 **Final Results:**\n"
                f"📦 **Total:** {total_messages}\n"
                f"✅ **Success:** {successful}\n"
                f"❌ **Failed:** {failed}\n"
                f"📈 **Success Rate:** {success_rate:.1f}%\n\n"
                f"💖 **Thank you for using R-TeleSwiftBot💖**"
            )
        
        # Clear batch task
        SerialBatchManager.clear_batch(user_id)
        
    except Exception as e:
        logger.error(f"Batch download error: {e}")
        if 'status' in locals():
            await status.edit(ERROR_MESSAGES['download_failed'])
        SerialBatchManager.clear_batch(user_id)
    finally:
        if acc:
            try:
                await acc.disconnect()
            except:
                pass

@Client.on_message(filters.command("start"))
async def start_command(bot, message):
    """Enhanced start command handler"""
    try:
        await db.update_last_active(message.from_user.id)
        
        # Add user to database if not exists
        if not await db.is_user_exist(message.from_user.id):
            await db.add_user(message.from_user.id, message.from_user.first_name)
            logger.info(f"New user added: {message.from_user.id}")
        
        # Create enhanced start message with buttons
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔐 Login", callback_data="login_help"),
             InlineKeyboardButton("📖 Help", callback_data="help_guide")],
            [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/VJ_Botz"),
             InlineKeyboardButton("📢 Channel", url="https://t.me/Tech_VJ")]
        ])
        
        await message.reply_text(
            START_TXT.format(user_mention=message.from_user.mention),
            reply_markup=buttons
        )
        
    except Exception as e:
        logger.error(f"Start command error: {e}")
        await message.reply_text("❌ An error occurred. Please try again.")

@Client.on_message(filters.command("help"))
async def help_command(bot, message):
    """Enhanced help command handler"""
    try:
        await db.update_last_active(message.from_user.id)
        
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔐 Login Guide", callback_data="login_help")],
            [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/VJ_Botz"),
             InlineKeyboardButton("📢 Channel", url="https://t.me/Tech_VJ")]
        ])
        
        await message.reply_text(HELP_TXT, reply_markup=buttons)
        
    except Exception as e:
        logger.error(f"Help command error: {e}")
        await message.reply_text("❌ An error occurred. Please try again.")

@Client.on_message(filters.command("cancel"))
async def cancel_command(bot, message):
    """Enhanced cancel command handler"""
    try:
        user_id = message.from_user.id
        await db.update_last_active(user_id)
        
        if SerialBatchManager.is_active(user_id):
            SerialBatchManager.cancel_batch(user_id)
            await message.reply_text(
                "🛑 **R-TeleSwiftBot💖 Cancellation**\n\n"
                "✅ **Batch download cancelled successfully!**\n\n"
                "You can now start a new download operation.\n\n"
                "💖 R-TeleSwiftBot💖"
            )
        else:
            await message.reply_text(
                "ℹ️ **No active operations**\n\n"
                "There are no active download operations to cancel.\n\n"
                "💖 R-TeleSwiftBot💖"
            )
            
    except Exception as e:
        logger.error(f"Cancel command error: {e}")
        await message.reply_text("❌ An error occurred. Please try again.")

@Client.on_callback_query()
async def callback_handler(bot, callback_query):
    """Enhanced callback query handler"""
    try:
        data = callback_query.data
        user_id = callback_query.from_user.id
        
        await db.update_last_active(user_id)
        
        if data == "login_help":
            from TechVJ.strings import LOGIN_HELP
            await callback_query.message.edit_text(
                LOGIN_HELP,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Start", callback_data="back_to_start")]
                ])
            )
        elif data == "help_guide":
            await callback_query.message.edit_text(
                HELP_TXT,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back to Start", callback_data="back_to_start")]
                ])
            )
        elif data == "back_to_start":
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔐 Login", callback_data="login_help"),
                 InlineKeyboardButton("📖 Help", callback_data="help_guide")],
                [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/VJ_Botz"),
                 InlineKeyboardButton("📢 Channel", url="https://t.me/Tech_VJ")]
            ])
            
            await callback_query.message.edit_text(
                START_TXT.format(user_mention=callback_query.from_user.mention),
                reply_markup=buttons
            )
        
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Callback handler error: {e}")
        try:
            await callback_query.answer("❌ An error occurred. Please try again.")
        except:
            pass

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
