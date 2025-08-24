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
    """Ultra-enhanced progress callback with cancellation check"""
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
            f"💖 **Ultra High Speed Mode**\n"
            f"🛑 **Use /cancel to stop instantly**"
        )
        
        # Try to edit the message
        try:
            await message.edit(progress_text)
        except Exception:
            pass  # Ignore edit errors
            
    except asyncio.CancelledError:
        # Handle cancellation gracefully
        try:
            await message.edit(
                "🛑 **CANCELLED!**\n\n"
                "❌ **Operation stopped instantly**\n"
                "💖 **R-TeleSwiftBot💖**"
            )
        except Exception:
            pass
        raise
    except Exception as e:
        logger.error(f"Progress error: {e}")

async def ultra_fast_download(acc, msg, status_msg, user_id):
    """Ultra-fast download with aggressive cancellation support"""
    start_time = time.time()
    download_task = None
    
    try:
        for attempt in range(2):  # Quick retry for speed
            try:
                # Check if cancelled before starting
                if AggressiveCancelManager.is_cancelled(user_id):
                    logger.info(f"Download cancelled before start for user {user_id}")
                    return None
                    
                logger.info(f"R-TeleSwiftBot💖 ultra-fast download attempt {attempt + 1} for message {msg.id}")
                
                # Create download task
                download_task = asyncio.create_task(
                    acc.download_media(
                        msg, 
                        progress=progress, 
                        progress_args=[status_msg, "down", start_time]
                    )
                )
                
                # Track the task for cancellation
                AggressiveCancelManager.add_download(user_id, download_task)
                
                # Wait for download with cancellation check
                file = await download_task
                
                # Remove from tracking
                AggressiveCancelManager.remove_download(user_id, download_task)
                
                # Check if cancelled after download
                if AggressiveCancelManager.is_cancelled(user_id):
                    if file and os.path.exists(file):
                        await safe_delete_file(file)
                    return None
                
                if file and os.path.exists(file):
                    return file
                else:
                    raise Exception("Downloaded file not found")
                    
            except asyncio.CancelledError:
                logger.info(f"Download cancelled for user {user_id}")
                if download_task:
                    AggressiveCancelManager.remove_download(user_id, download_task)
                return None
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
        
    finally:
        if download_task:
            AggressiveCancelManager.remove_download(user_id, download_task)

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
        except Exception:
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

@Client.on_message(filters.command("cancel") & filters.private)
async def aggressive_cancel_operation(client, message):
    """AGGRESSIVE instant cancel - stops everything immediately"""
    try:
        user_id = message.from_user.id
        await db.update_last_active(user_id)
        
        logger.info(f"AGGRESSIVE CANCEL requested by user {user_id}")
        
        # Check if user has any active operations
        if AggressiveCancelManager.is_active(user_id):
            # Show immediate feedback
            cancel_msg = await message.reply_text(
                "🛑 **AGGRESSIVE CANCEL INITIATED!**\n\n"
                "⚡ **Stopping all operations immediately...**\n"
                "📥 **Cancelling downloads...**\n"
                "📤 **Cancelling uploads...**\n"
                "🔌 **Disconnecting clients...**"
            )
            
            # Perform aggressive cancellation
            cancelled_count = await AggressiveCancelManager.aggressive_cancel_all(user_id)
            
            # Update status
            await cancel_msg.edit(
                "✅ **ALL OPERATIONS CANCELLED SUCCESSFULLY!** 🛑\n\n"
                f"⚡ **Cancelled Tasks:** {cancelled_count}\n"
                f"📥 **Downloads:** Stopped instantly\n"
                f"📤 **Uploads:** Stopped instantly\n"
                f"🔌 **Clients:** Disconnected\n"
                f"💾 **Files:** Cleaned up\n\n"
                f"🚀 **R-TeleSwiftBot💖 ready for new tasks!**\n"
                f"💡 **Send any link to start downloading again**"
            )
            
            logger.info(f"AGGRESSIVE CANCEL completed for user {user_id} - {cancelled_count} tasks cancelled")
            
        else:
            await message.reply_text(
                "ℹ️ **No Active Operations Found**\n\n"
                "🔍 **Status:** No running downloads or uploads\n"
                "✅ **All systems ready**\n\n"
                "💡 **Tip:** Send any Telegram link to start downloading!\n"
                "🚀 **R-TeleSwiftBot💖 Ultra High Speed Mode**"
            )
        
    except Exception as e:
        logger.error(f"Aggressive cancel command error: {e}")
        await message.reply_text(
            "❌ **Error during cancellation!**\n\n"
            "⚠️ Operations may still be running\n"
            "🔄 Please try `/cancel` again if needed\n\n"
            "💖 **R-TeleSwiftBot💖**"
        )

@Client.on_message(filters.text & filters.private & ~filters.forwarded & ~filters.command(['start', 'help', 'login', 'logout', 'cancel']))
async def handle_message(client, message):
    """Enhanced message handler with aggressive cancellation support"""
    try:
        user_id = message.from_user.id
        await db.update_last_active(user_id)
        
        # Clear any previous cancel flags
        AggressiveCancelManager.clear_cancel_flag(user_id)
        
        # Check if user has active operations
        if AggressiveCancelManager.is_active(user_id):
            return await message.reply_text(
                "⏳ **R-TeleSwiftBot💖 Busy!**\n\n"
                "🔄 You have an active download in progress.\n"
                "🛑 Use `/cancel` to stop it instantly!\n\n"
                "💡 **Tip:** Aggressive cancellation available!\n"
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
    """Handle single message download with aggressive cancellation"""
    user_id = message.from_user.id
    acc = None
    file_path = None
    thumbnail_path = None
    upload_task = None
    
    try:
        # Track this operation
        AggressiveCancelManager.start_task(user_id, 'single_download', {'chat_id': chat_id, 'msg_id': msg_id})
        
        # Create status message
        status_msg = await message.reply_text(
            "🚀 **R-TeleSwiftBot💖 Initializing...**\n\n"
            "⚡ **Ultra High Speed Mode Activated**\n"
            "📥 **Preparing to download...**\n\n"
            "🛑 **Use /cancel for instant stop**"
        )
        
        # Create client
        try:
            acc = await create_client_with_retry(user_data)
            AggressiveCancelManager.add_client(user_id, acc)
            
            # Check if cancelled during client creation
            if AggressiveCancelManager.is_cancelled(user_id):
                return await status_msg.edit("🛑 **Cancelled during initialization**")
                
        except Exception as e:
            return await status_msg.edit(f"❌ **Connection failed:** `{str(e)[:150]}`")
        
        # Fetch message
        try:
            msg = await acc.get_messages(chat_id, msg_id)
            if not msg:
                return await status_msg.edit("❌ **Message not found!**")
                
            # Check if cancelled after getting message
            if AggressiveCancelManager.is_cancelled(user_id):
                return await status_msg.edit("🛑 **Cancelled after fetching message**")
                
        except Exception as e:
            return await status_msg.edit(f"❌ **Error fetching message:** `{str(e)[:150]}`")
        
        # Check media
        if not (msg.video or msg.document or msg.photo or msg.audio or msg.voice):
            return await status_msg.edit("❌ **No downloadable media found!**")
        
        # Download file
        await status_msg.edit(
            "📥 **R-TeleSwiftBot💖 Downloading...**\n\n"
            "⚡ **Ultra High Speed Processing**\n"
            "🛑 **Use /cancel to stop instantly**"
        )
        
        file_path = await ultra_fast_download(acc, msg, status_msg, user_id)
        
        # Check if download was cancelled
        if file_path is None or AggressiveCancelManager.is_cancelled(user_id):
            if file_path and os.path.exists(file_path):
                await safe_delete_file(file_path)
            return await status_msg.edit("🛑 **Download cancelled successfully**")
        
        # Get thumbnail
        thumbnail_path = await get_optimized_thumbnail(acc, msg)
        
        # Check if cancelled before upload
        if AggressiveCancelManager.is_cancelled(user_id):
            await safe_delete_file(file_path)
            if thumbnail_path:
                await safe_delete_file(thumbnail_path)
            return await status_msg.edit("🛑 **Cancelled before upload**")
        
        # Upload file
        caption = f"💖 **Ashish 😏**\n\n{msg.caption or ''}\n\n🚀 **R-TeleSwiftBot Ultra High Speed**"
        
        await status_msg.edit(
            "📤 **R-TeleSwiftBot💖 Uploading...**\n\n"
            "⚡ **Ultra High Speed Mode**\n"
            "🛑 **Use /cancel to stop instantly**"
        )
        
        # Create upload task
        if msg.video:
            upload_task = asyncio.create_task(
                client.send_video(
                    chat_id=message.chat.id,
                    video=file_path,
                    caption=caption,
                    thumb=thumbnail_path,
                    progress=progress,
                    progress_args=[status_msg, "up"]
                )
            )
        elif msg.document:
            upload_task = asyncio.create_task(
                client.send_document(
                    chat_id=message.chat.id,
                    document=file_path,
                    caption=caption,
                    thumb=thumbnail_path,
                    progress=progress,
                    progress_args=[status_msg, "up"]
                )
            )
        elif msg.photo:
            upload_task = asyncio.create_task(
                client.send_photo(
                    chat_id=message.chat.id,
                    photo=file_path,
                    caption=caption,
                    progress=progress,
                    progress_args=[status_msg, "up"]
                )
            )
        elif msg.audio:
            upload_task = asyncio.create_task(
                client.send_audio(
                    chat_id=message.chat.id,
                    audio=file_path,
                    caption=caption,
                    thumb=thumbnail_path,
                    progress=progress,
                    progress_args=[status_msg, "up"]
                )
            )
        
        # Track upload task
        if upload_task:
            AggressiveCancelManager.add_upload(user_id, upload_task)
            
            # Wait for upload
            await upload_task
            
            # Remove from tracking
            AggressiveCancelManager.remove_upload(user_id, upload_task)
        
        # Success message
        await status_msg.edit(
            "✅ **R-TeleSwiftBot💖 Complete!**\n\n"
            "🚀 **Ultra High Speed Download & Upload**\n"
            "💖 **Powered by Ashish 😏**\n\n"
            "📥 Send another link to continue!"
        )
        
    except asyncio.CancelledError:
        await status_msg.edit("🛑 **Operation cancelled successfully**")
        
    except Exception as e:
        logger.error(f"Single download error: {e}")
        await status_msg.edit(f"❌ **Error:** `{str(e)[:200]}`")
        
    finally:
        # Cleanup
        if file_path:
            await safe_delete_file(file_path)
        if thumbnail_path:
            await safe_delete_file(thumbnail_path)
        if acc:
            try:
                await acc.disconnect()
            except Exception:
                pass
        if upload_task:
            AggressiveCancelManager.remove_upload(user_id, upload_task)
        
        # Clear user tasks
        if user_id in AggressiveCancelManager.USER_TASKS:
            AggressiveCancelManager.USER_TASKS[user_id] = []

async def handle_serial_batch_download(client, message, user_data, chat_id, start_msg_id, end_msg_id, original_link):
    """Handle serial batch download with aggressive cancellation"""
    user_id = message.from_user.id
    acc = None
    
    try:
        # Track batch operation
        AggressiveCancelManager.start_task(user_id, 'batch_download', {
            'chat_id': chat_id, 
            'start': start_msg_id, 
            'end': end_msg_id
        })
        
        # Validate batch size
        total_messages = abs(end_msg_id - start_msg_id) + 1
        if total_messages > MAX_BATCH_SIZE:
            return await message.reply_text(f"❌ **Batch too large!** Max {MAX_BATCH_SIZE} messages allowed.")
        
        # Create status message
        batch_status = await message.reply_text(
            f"🚀 **R-TeleSwiftBot💖 Serial Batch Starting...**\n\n"
            f"📦 **Total Messages:** `{total_messages}`\n"
            f"⚡ **Ultra High Speed Serial Mode**\n"
            f"🛑 **Use /cancel to stop instantly**"
        )
        
        # Create client
        try:
            acc = await create_client_with_retry(user_data)
            AggressiveCancelManager.add_client(user_id, acc)
            
            # Check if cancelled during client creation
            if AggressiveCancelManager.is_cancelled(user_id):
                return await batch_status.edit("🛑 **Batch cancelled during initialization**")
                
        except Exception as e:
            return await batch_status.edit(f"❌ **Connection failed:** `{str(e)[:150]}`")
        
        # Serial processing
        success_count = 0
        failed_count = 0
        start_time = time.time()
        
        # Process messages serially
        for i, msg_id in enumerate(range(start_msg_id, end_msg_id + 1), 1):
            try:
                # Check for cancellation at the start of each iteration
                if AggressiveCancelManager.is_cancelled(user_id):
                    await batch_status.edit(
                        f"🛑 **BATCH CANCELLED!**\n\n"
                        f"📊 **Progress when stopped:**\n"
                        f"✅ **Successful:** `{success_count}`\n"
                        f"❌ **Failed:** `{failed_count}`\n"
                        f"⏹️ **Remaining:** `{total_messages - i + 1}`"
                    )
                    return
                
                # Update progress
                elapsed = time.time() - start_time
                avg_time = elapsed / i if i > 0 else 0
                remaining = total_messages - i
                eta = time.strftime('%M:%S', time.gmtime(avg_time * remaining))
                
                await batch_status.edit(
                    f"🚀 **R-TeleSwiftBot💖 Serial Processing** `{i}/{total_messages}`\n\n"
                    f"📊 **Progress:** `{i/total_messages*100:.1f}%`\n"
                    f"✅ **Success:** `{success_count}` | ❌ **Failed:** `{failed_count}`\n"
                    f"⏱️ **ETA:** `{eta}`\n\n"
                    f"🔄 **Current:** `Message {msg_id}`\n"
                    f"💖 **True Serial Mode**\n"
                    f"🛑 **Use /cancel to stop instantly**"
                )
                
                # Process single message
                success = await process_single_message_for_batch(acc, client, message, chat_id, msg_id, user_id)
                
                if success:
                    success_count += 1
                else:
                    failed_count += 1
                
                # Small delay for serial processing
                await asyncio.sleep(0.3)
                
            except Exception as e:
                logger.error(f"Error processing message {msg_id}: {e}")
                failed_count += 1
                continue
        
        # Final summary
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
            f"💖 **Powered by Ashish 😏**"
        )
        
    except Exception as e:
        logger.error(f"Batch download error: {e}")
        await message.reply_text(f"❌ **Batch download error:** `{str(e)[:100]}`")
        
    finally:
        if acc:
            try:
                await acc.disconnect()
            except Exception:
                pass
        
        # Clear user tasks
        if user_id in AggressiveCancelManager.USER_TASKS:
            AggressiveCancelManager.USER_TASKS[user_id] = []

async def process_single_message_for_batch(acc, bot_client, original_message, chat_id, msg_id, user_id):
    """Process single message in batch with cancellation check"""
    try:
        # Check for cancellation
        if AggressiveCancelManager.is_cancelled(user_id):
            return False
        
        # Get message
        msg = await acc.get_messages(chat_id, msg_id)
        if not msg or not (msg.video or msg.document or msg.photo or msg.audio):
            return False
        
        # Quick download
        file_path = await acc.download_media(msg)
        if not file_path or not os.path.exists(file_path):
            return False
        
        # Check for cancellation before upload
        if AggressiveCancelManager.is_cancelled(user_id):
            await safe_delete_file(file_path)
            return False
        
        # Quick upload
        caption = f"💖 **Ashish 😏**\n\n{msg.caption or ''}\n\n🚀 **R-TeleSwiftBot Serial Mode**"
        
        if msg.video:
            await bot_client.send_video(
                chat_id=original_message.chat.id,
                video=file_path,
                caption=caption
            )
        elif msg.document:
            await bot_client.send_document(
                chat_id=original_message.chat.id,
                document=file_path,
                caption=caption
            )
        elif msg.photo:
            await bot_client.send_photo(
                chat_id=original_message.chat.id,
                photo=file_path,
                caption=caption
            )
        elif msg.audio:
            await bot_client.send_audio(
                chat_id=original_message.chat.id,
                audio=file_path,
                caption=caption
            )
        
        # Cleanup
        await safe_delete_file(file_path)
        return True
        
    except Exception as e:
        logger.error(f"Error processing message {msg_id}: {e}")
        return False

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
