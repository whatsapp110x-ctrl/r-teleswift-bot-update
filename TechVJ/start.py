# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import asyncio 
import logging
import pyrogram
from pyrogram.client import Client
from pyrogram import filters, enums
from pyrogram.errors import (
    FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, 
    InviteHashExpired, UsernameNotOccupied, MessageNotModified, AuthKeyUnregistered, 
    SessionExpired, SessionRevoked, ChannelPrivate, ChatAdminRequired, UserNotParticipant,
    PeerIdInvalid, MessageIdInvalid, ChannelInvalid
)
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message 
from config import (
    API_ID, API_HASH, ERROR_MESSAGE, MAX_BATCH_SIZE, PROGRESS_UPDATE_INTERVAL, 
    MAX_FILE_SIZE, DOWNLOAD_CHUNK_SIZE, MAX_CONCURRENT_DOWNLOADS, CONNECTION_TIMEOUT,
    MAX_RETRIES, RETRY_DELAY, THUMBNAIL_QUALITY, THUMBNAIL_MAX_SIZE, CONNECTION_POOL_SIZE,
    MINIMAL_DELAY, UPLOAD_CHUNK_SIZE, PROGRESS_THROTTLE, SLEEP_THRESHOLD  # FIXED: Added SLEEP_THRESHOLD
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
    """Class to manage batch operations state"""
    IS_BATCH = {}
    USER_TASKS = {}
    
    @classmethod
    def set_batch_state(cls, user_id, state):
        cls.IS_BATCH[user_id] = state
    
    @classmethod
    def get_batch_state(cls, user_id):
        return cls.IS_BATCH.get(user_id, True)
    
    @classmethod
    def set_user_task(cls, user_id, task):
        cls.USER_TASKS[user_id] = task
    
    @classmethod
    def get_user_task(cls, user_id):
        return cls.USER_TASKS.get(user_id)
    
    @classmethod
    def clear_user_task(cls, user_id):
        if user_id in cls.USER_TASKS:
            del cls.USER_TASKS[user_id]

async def safe_delete_file(file_path):
    """Safely delete a file"""
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"Deleted file: {file_path}")
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {e}")

async def validate_session(session_string):
    """Validate if session is still active - optimized version"""
    try:
        test_client = Client(
            ":memory:", 
            session_string=session_string, 
            api_id=API_ID, 
            api_hash=API_HASH,
            sleep_threshold=SLEEP_THRESHOLD
        )
        await test_client.connect()
        await asyncio.wait_for(test_client.get_me(), timeout=10.0)
        await test_client.disconnect()
        return True
    except (AuthKeyUnregistered, SessionExpired, SessionRevoked):
        return False
    except Exception as e:
        logger.error(f"Session validation error: {e}")
        return False

async def create_client_with_retry(user_data, max_retries=2):  # Reduced retries
    """Create and connect client with optimized retry mechanism"""
    if not user_data:
        raise Exception("No session data provided")
    
    # First validate the session
    if not await validate_session(user_data):
        raise Exception("Session expired or invalid - please /logout and /login again")
    
    for attempt in range(max_retries):
        try:
            acc = Client(
                f":memory:{attempt}", 
                session_string=user_data, 
                api_hash=API_HASH, 
                api_id=API_ID,
                sleep_threshold=SLEEP_THRESHOLD,
                max_concurrent_transmissions=3  # Reduced for stability
            )
            await asyncio.wait_for(acc.connect(), timeout=15.0)  # Added timeout
            
            # Test connection
            await asyncio.wait_for(acc.get_me(), timeout=10.0)
            return acc
            
        except (AuthKeyUnregistered, SessionExpired, SessionRevoked):
            raise Exception("Session expired - please /logout and /login again")
        except Exception as e:
            logger.warning(f"Client connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2)  # Reduced delay
            else:
                raise Exception(f"Failed to connect: {str(e)[:100]}")

async def ultra_fast_download(acc, msg, message, max_retries=2):  # Reduced retries
    """Optimized download with retry mechanism"""
    for attempt in range(max_retries):
        try:
            logger.info(f"Download attempt {attempt + 1} for message {msg.id}")
            file = await asyncio.wait_for(
                acc.download_media(
                    msg, 
                    progress=progress, 
                    progress_args=[message, "down"]
                ),
                timeout=300.0  # 5 minutes timeout
            )
            if file and os.path.exists(file):
                return file
            else:
                raise Exception("Downloaded file not found")
        except FloodWait as fw:
            logger.warning(f"FloodWait {fw.value}s on attempt {attempt + 1}")
            await asyncio.sleep(fw.value)
        except asyncio.TimeoutError:
            logger.error(f"Download timeout on attempt {attempt + 1}")
            if attempt < max_retries - 1:
                await asyncio.sleep(3)
            else:
                raise Exception("Download timeout")
        except Exception as e:
            logger.warning(f"Download attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(3)
            else:
                raise e

async def get_ultra_hd_thumbnail(acc, msg):
    """Get the highest quality thumbnail available - optimized"""
    try:
        thumbnail_path = None
        
        # For videos
        if msg.video and hasattr(msg.video, 'thumbs') and msg.video.thumbs:
            largest_thumb = max(msg.video.thumbs, key=lambda x: getattr(x, 'file_size', 0))
            thumbnail_path = await asyncio.wait_for(
                acc.download_media(largest_thumb.file_id),
                timeout=30.0
            )
                
        # For documents
        elif msg.document and hasattr(msg.document, 'thumbs') and msg.document.thumbs:
            largest_thumb = max(msg.document.thumbs, key=lambda x: getattr(x, 'file_size', 0))
            thumbnail_path = await asyncio.wait_for(
                acc.download_media(largest_thumb.file_id),
                timeout=30.0
            )
        
        # For photos
        elif msg.photo:
            thumbnail_path = await asyncio.wait_for(
                acc.download_media(msg.photo.file_id),
                timeout=30.0
            )
        
        if thumbnail_path and os.path.exists(thumbnail_path):
            return thumbnail_path
        else:
            return None
            
    except Exception as e:
        logger.error(f"Error getting thumbnail: {e}")
        return None

_last_progress_update = {}

def progress(current, total, message, type):
    """Progress callback with optimized throttling"""
    try:
        percentage = current * 100 / total
        progress_key = f"{message.id}_{type}"
        
        if progress_key in _last_progress_update:
            if abs(percentage - _last_progress_update[progress_key]) < 10:  # Update every 10%
                return
        
        _last_progress_update[progress_key] = percentage
        
        with open(f'{message.id}{type}status.txt', "w") as fileup:
            fileup.write(f"{percentage:.1f}% | {current/1024/1024:.1f}MB/{total/1024/1024:.1f}MB")
    except Exception:
        pass

async def process_media_message(client, message, acc, msg):
    """Process media message for download - optimized version"""
    file_path = None
    thumbnail = None
    
    try:
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
            return False
        
        if file_size > MAX_FILE_SIZE:
            await message.reply_text(f"❌ File too large: {file_size/1024/1024:.1f}MB (Max: {MAX_FILE_SIZE/1024/1024:.1f}MB)")
            return False
        
        # Send download status
        status_msg = await message.reply_text(f"⬇️ Downloading {filename[:50]}...")
        
        try:
            # Download file
            file_path = await ultra_fast_download(acc, msg, status_msg)
            
            if not file_path or not os.path.exists(file_path):
                await status_msg.edit("❌ Download failed - file not found")
                return False
            
            await status_msg.edit("⬆️ Uploading...")
            
            # Get thumbnail
            thumbnail = await get_ultra_hd_thumbnail(acc, msg)
            
            # Upload based on media type
            caption = f"📎 {filename}\n\n✅ Downloaded successfully!"
            
            if msg.document:
                await client.send_document(
                    message.chat.id,
                    file_path,
                    thumb=thumbnail,
                    caption=caption,
                    progress=progress,
                    progress_args=[status_msg, "up"]
                )
            elif msg.video:
                await client.send_video(
                    message.chat.id,
                    file_path,
                    thumb=thumbnail,
                    caption=caption,
                    progress=progress,
                    progress_args=[status_msg, "up"]
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
                    progress_args=[status_msg, "up"]
                )
            
            await status_msg.delete()
            return True
            
        except FloodWait as fw:
            logger.warning(f"FloodWait {fw.value}s during upload")
            await asyncio.sleep(fw.value)
            await status_msg.edit(f"❌ Rate limited - wait {fw.value}s")
            return False
        except Exception as e:
            logger.error(f"Upload error: {e}")
            await status_msg.edit(f"❌ Upload failed: {str(e)[:50]}")
            return False
            
    except Exception as e:
        logger.error(f"Error processing media: {e}")
        return False
    finally:
        # Clean up files
        if file_path:
            await safe_delete_file(file_path)
        if thumbnail:
            await safe_delete_file(thumbnail)

async def process_single_message(client, message, datas, msgid):
    """Process a single message for download - optimized"""
    acc = None
    try:
        # Check if user has active task
        if BatchTemp.get_user_task(message.from_user.id):
            await message.reply_text("⏳ Another task is in progress. Please wait or use /cancel")
            return False
        
        # Set user task
        BatchTemp.set_user_task(message.from_user.id, "single_download")
        
        # Get user session
        user_data = await db.get_session(message.from_user.id)
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
                # Clear invalid session
                await db.set_session(message.from_user.id, None)
            else:
                await message.reply_text(f"❌ Connection error: {error_msg}")
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
                timeout=20.0
            )
            
            if not msg:
                await message.reply_text("❌ Message not found or access denied")
                return False
                
        except ChannelPrivate:
            await message.reply_text(ERROR_MESSAGES['access_denied'])
            return False
        except Exception as e:
            logger.error(f"Error getting message: {e}")
            await message.reply_text(f"❌ Failed to access message: {str(e)[:100]}")
            return False
        
        # Process the message
        success = await process_media_message(client, message, acc, msg)
        return success
        
    except Exception as e:
        logger.error(f"Error in process_single_message: {e}")
        await message.reply_text(f"❌ Processing error: {str(e)[:100]}")
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
    """Handle start command"""
    try:
        user_id = message.from_user.id
        
        # Add user to database
        if not await db.is_user_exist(user_id):
            await db.add_user(user_id, message.from_user.first_name)
        
        await db.update_last_active(user_id)
        
        # Create buttons
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📖 Help", callback_data="help")],
            [InlineKeyboardButton("📢 Channel", url="https://t.me/Tech_VJ")]
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
            [InlineKeyboardButton("🏠 Home", callback_data="start")],
            [InlineKeyboardButton("📢 Channel", url="https://t.me/Tech_VJ")]
        ])
        
        await message.reply_text(HELP_TXT, reply_markup=buttons)
        
    except Exception as e:
        logger.error(f"Error in help command: {e}")
        await message.reply_text("❌ An error occurred. Please try again later.")

# Cancel command
@Client.on_message(filters.command("cancel") & filters.private)
async def cancel_command(client, message):
    """Handle cancel command"""
    try:
        user_id = message.from_user.id
        
        if BatchTemp.get_user_task(user_id):
            BatchTemp.clear_user_task(user_id)
            await message.reply_text("🛑 **Operation cancelled successfully!**")
        else:
            await message.reply_text("❌ **No active operation to cancel.**")
            
    except Exception as e:
        logger.error(f"Error in cancel command: {e}")
        await message.reply_text("❌ An error occurred while cancelling.")

# Handle Telegram links
@Client.on_message(filters.private & filters.text)
async def handle_links(client, message):
    """Handle Telegram post links - optimized"""
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
                await message.reply_text("❌ Invalid message ID in the link")
        
    except Exception as e:
        logger.error(f"Error handling link: {e}")
        await message.reply_text(f"❌ Link processing error: {str(e)[:100]}")

async def handle_batch_download(client, message, datas):
    """Handle batch download - simplified version"""
    try:
        # Extract range
        range_part = datas[-1]
        start_msg, end_msg = map(int, range_part.split("-"))
        
        if end_msg - start_msg > MAX_BATCH_SIZE:
            await message.reply_text(f"❌ Batch size too large! Max allowed: {MAX_BATCH_SIZE}")
            return
        
        total_messages = end_msg - start_msg + 1
        await message.reply_text(f"📦 **Processing {total_messages} messages...**\n\nUse /cancel to stop")
        
        success_count = 0
        failed_count = 0
        
        for msg_id in range(start_msg, end_msg + 1):
            try:
                if not BatchTemp.get_user_task(message.from_user.id):
                    break  # User cancelled
                
                success = await process_single_message(client, message, datas, msg_id)
                if success:
                    success_count += 1
                else:
                    failed_count += 1
                
                # Brief delay between downloads
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error processing message {msg_id}: {e}")
                failed_count += 1
                continue
        
        # Send summary
        await message.reply_text(
            f"✅ **Batch completed!**\n\n"
            f"📊 **Summary:**\n"
            f"✅ Success: {success_count}\n"
            f"❌ Failed: {failed_count}\n"
            f"📝 Total: {total_messages}"
        )
        
    except Exception as e:
        logger.error(f"Error in batch download: {e}")
        await message.reply_text(f"❌ Batch download error: {str(e)[:100]}")
    finally:
        BatchTemp.clear_user_task(message.from_user.id)

# Callback query handler
@Client.on_callback_query()
async def callback_handler(client, callback_query):
    """Handle callback queries"""
    try:
        data = callback_query.data
        
        if data == "start":
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("📖 Help", callback_data="help")],
                [InlineKeyboardButton("📢 Channel", url="https://t.me/Tech_VJ")]
            ])
            
            await callback_query.edit_message_text(
                START_TXT.format(user_mention=callback_query.from_user.mention),
                reply_markup=buttons
            )
            
        elif data == "help":
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Home", callback_data="start")],
                [InlineKeyboardButton("📢 Channel", url="https://t.me/Tech_VJ")]
            ])
            
            await callback_query.edit_message_text(HELP_TXT, reply_markup=buttons)
        
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error in callback handler: {e}")
        await callback_query.answer("❌ An error occurred", show_alert=True)

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
