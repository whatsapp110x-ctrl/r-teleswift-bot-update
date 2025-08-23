# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import asyncio 
import logging
import pyrogram
from pyrogram.client import Client
from pyrogram import filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied, MessageNotModified
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message 
from config import (
    API_ID, API_HASH, ERROR_MESSAGE, MAX_BATCH_SIZE, PROGRESS_UPDATE_INTERVAL, 
    MAX_FILE_SIZE, DOWNLOAD_CHUNK_SIZE, MAX_CONCURRENT_DOWNLOADS, CONNECTION_TIMEOUT,
    MAX_RETRIES, RETRY_DELAY, THUMBNAIL_QUALITY, THUMBNAIL_MAX_SIZE, CONNECTION_POOL_SIZE,
    MINIMAL_DELAY, UPLOAD_CHUNK_SIZE, PROGRESS_THROTTLE
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
    
    @classmethod
    def set_batch_state(cls, user_id, state):
        cls.IS_BATCH[user_id] = state
    
    @classmethod
    def get_batch_state(cls, user_id):
        return cls.IS_BATCH.get(user_id, True)

async def safe_delete_file(file_path):
    """Safely delete a file"""
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"Deleted file: {file_path}")
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {e}")

async def ultra_fast_download(acc, msg, message, max_retries=MAX_RETRIES):
    """Ultra-fast download with retry mechanism"""
    for attempt in range(max_retries):
        try:
            logger.info(f"Ultra-fast download attempt {attempt + 1}")
            file = await acc.download_media(msg, progress=progress, progress_args=[message, "down"])
            return file
        except Exception as e:
            logger.warning(f"Download attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(RETRY_DELAY)
            else:
                raise e

async def get_ultra_hd_thumbnail(acc, media_obj):
    """Get the highest quality thumbnail available"""
    try:
        if hasattr(media_obj, 'thumbs') and media_obj.thumbs:
            # Sort thumbnails by size to get the largest (highest quality)
            best_thumb = None
            max_size = 0
            
            for thumb in media_obj.thumbs:
                if hasattr(thumb, 'width') and hasattr(thumb, 'height'):
                    thumb_size = thumb.width * thumb.height
                    if thumb_size > max_size:
                        max_size = thumb_size
                        best_thumb = thumb
            
            if best_thumb:
                logger.info(f"Downloading ultra HD thumbnail: {best_thumb.width}x{best_thumb.height}")
                return await acc.download_media(best_thumb.file_id)
    except Exception as e:
        logger.error(f"Error getting ultra HD thumbnail: {e}")
    return None

async def create_client_with_retry(user_data):
    """Create and connect client with retry mechanism"""
    for attempt in range(MAX_RETRIES):
        try:
            acc = Client(
                ":memory:", 
                session_string=user_data, 
                api_hash=API_HASH, 
                api_id=API_ID
            )
            await acc.connect()
            return acc
        except Exception as e:
            logger.warning(f"Client connection attempt {attempt + 1} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY)
            else:
                raise e

async def downstatus(client, statusfile, message, chat):
    """Lightning-fast download status monitor"""
    try:
        last_txt = ""
        while True:
            if os.path.exists(statusfile):
                break
            await asyncio.sleep(MINIMAL_DELAY)
          
        while os.path.exists(statusfile):
            try:
                with open(statusfile, "r") as downread:
                    txt = downread.read()
                if txt != last_txt:
                    await client.edit_message_text(chat, message.id, f"⚡ **Downloading:** {txt}")
                    last_txt = txt
                await asyncio.sleep(PROGRESS_THROTTLE)
            except Exception:
                pass
    except Exception:
        pass

async def upstatus(client, statusfile, message, chat):
    """Lightning-fast upload status monitor"""
    try:
        last_txt = ""
        while True:
            if os.path.exists(statusfile):
                break
            await asyncio.sleep(MINIMAL_DELAY)      
            
        while os.path.exists(statusfile):
            try:
                with open(statusfile, "r") as upread:
                    txt = upread.read()
                if txt != last_txt:
                    await client.edit_message_text(chat, message.id, f"⚡ **Uploading:** {txt}")
                    last_txt = txt
                await asyncio.sleep(PROGRESS_THROTTLE)
            except Exception:
                pass
    except Exception:
        pass

_last_progress_update = {}

def progress(current, total, message, type):
    """Lightning-fast progress with throttling"""
    try:
        percentage = current * 100 / total
        progress_key = f"{message.id}_{type}"
        
        if progress_key in _last_progress_update:
            if percentage - _last_progress_update[progress_key] < 5:
                return
        
        _last_progress_update[progress_key] = percentage
        speed = (current / 1024 / 1024) * 8
        
        with open(f'{message.id}{type}status.txt', "w") as fileup:
            fileup.write(f"⚡ {percentage:.1f}% | {speed:.1f}MB/s")
    except Exception:
        pass

@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    """Handle /start command"""
    try:
        await db.update_last_active(message.from_user.id)
        
        if not await db.is_user_exist(message.from_user.id):
            await db.add_user(message.from_user.id, message.from_user.first_name)
            logger.info(f"New user registered: {message.from_user.id}")
        
        buttons = [[
            InlineKeyboardButton("❣️ Developer", url="https://t.me/fightermonk110")
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await client.send_message(
            chat_id=message.chat.id, 
            text=START_TXT.format(user_mention=message.from_user.mention), 
            reply_markup=reply_markup, 
            reply_to_message_id=message.id
        )
        
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await message.reply_text("❌ An error occurred. Please try again later.")

@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    """Handle /help command"""
    try:
        await db.update_last_active(message.from_user.id)
        await client.send_message(
            chat_id=message.chat.id, 
            text=HELP_TXT
        )
    except Exception as e:
        logger.error(f"Error in help command: {e}")
        await message.reply_text("❌ An error occurred. Please try again later.")

@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    """Handle /cancel command"""
    try:
        await db.update_last_active(message.from_user.id)
        BatchTemp.set_batch_state(message.from_user.id, True)
        await client.send_message(
            chat_id=message.chat.id, 
            text="🛑 **Batch Successfully Cancelled.**"
        )
        logger.info(f"User {message.from_user.id} cancelled batch operation")
    except Exception as e:
        logger.error(f"Error in cancel command: {e}")
        await message.reply_text("❌ An error occurred. Please try again later.")

async def process_single_message(client, message, datas, msgid):
    """Process a single message for download"""
    acc = None
    try:
        # Get user session
        user_data = await db.get_session(message.from_user.id)
        if user_data is None:
            logger.error("User not logged in")
            return False
        
        # Create client connection
        acc = await create_client_with_retry(user_data)
        
        # Determine chat ID based on URL format
        if "/c/" in message.text:
            chat_id = int("-100" + str(datas[4]))
        else:
            chat_id = datas[3]
        
        # Get message - FIXED: Handle single message properly
        try:
            msg = await acc.get_messages(chat_id, msgid)
            
            # Check if message exists and is not empty
            if not msg or (hasattr(msg, 'empty') and msg.empty):
                logger.warning(f"Empty or non-existent message {msgid}")
                return False
            
            # Process media content
            if msg.media:
                success = await process_media_message(client, message, acc, msg)
                return success
            elif msg.text:
                # Forward text message
                await client.send_message(
                    message.chat.id,
                    f"📝 **Text Message:**\n\n{msg.text}"
                )
                return True
            else:
                logger.warning(f"Message {msgid} has no media or text")
                return False
                
        except Exception as msg_error:
            logger.error(f"Error getting message {msgid}: {msg_error}")
            return False
            
    except Exception as e:
        logger.error(f"Error processing message {msgid}: {e}")
        return False
    finally:
        if acc:
            try:
                await acc.disconnect()
            except:
                pass

async def process_media_message(client, message, acc, msg):
    """Process media message for download and upload"""
    file_path = None
    thumbnail = None
    download_msg = None
    
    try:
        # Check file size
        if hasattr(msg.media, 'file_size') and msg.media.file_size > MAX_FILE_SIZE:
            await message.reply_text("❌ **File too large!**")
            return False
        
        # Send download status message
        download_msg = await client.send_message(
            message.chat.id,
            "⚡ **Starting ultra-fast download...**"
        )
        
        # Start download status monitoring
        status_file = f"{download_msg.id}downstatus.txt"
        status_task = asyncio.create_task(
            downstatus(client, status_file, download_msg, message.chat.id)
        )
        
        try:
            # Download with progress
            file_path = await ultra_fast_download(acc, msg, download_msg)
            
            if not file_path:
                await download_msg.edit("❌ **Download failed!**")
                return False
            
            # Get thumbnail if available
            thumbnail = await get_ultra_hd_thumbnail(acc, msg.media)
            
            # Upload file
            await download_msg.edit("⚡ **Starting ultra-fast upload...**")
            
            upload_status_file = f"{download_msg.id}upstatus.txt"
            upload_task = asyncio.create_task(
                upstatus(client, upload_status_file, download_msg, message.chat.id)
            )
            
            # Determine file type and upload accordingly
            if msg.photo:
                await client.send_photo(
                    message.chat.id,
                    file_path,
                    caption=msg.caption or "📸 **Photo downloaded successfully!**"
                )
            elif msg.video:
                await client.send_video(
                    message.chat.id,
                    file_path,
                    thumb=thumbnail,
                    caption=msg.caption or "🎥 **Video downloaded successfully!**",
                    supports_streaming=True,
                    progress=progress,
                    progress_args=[download_msg, "up"]
                )
            elif msg.document:
                await client.send_document(
                    message.chat.id,
                    file_path,
                    thumb=thumbnail,
                    caption=msg.caption or "📄 **Document downloaded successfully!**",
                    progress=progress,
                    progress_args=[download_msg, "up"]
                )
            elif msg.audio:
                await client.send_audio(
                    message.chat.id,
                    file_path,
                    thumb=thumbnail,
                    caption=msg.caption or "🎵 **Audio downloaded successfully!**"
                )
            else:
                await client.send_document(
                    message.chat.id,
                    file_path,
                    caption=msg.caption or "📎 **File downloaded successfully!**"
                )
            
            await download_msg.edit("✅ **Download and upload completed!**")
            return True
            
        finally:
            # Cleanup tasks
            status_task.cancel()
            if 'upload_task' in locals():
                upload_task.cancel()
            
            # Clean up status files
            await safe_delete_file(status_file)
            if 'upload_status_file' in locals():
                await safe_delete_file(upload_status_file)
                
    except Exception as e:
        logger.error(f"Error processing media: {e}")
        if download_msg:
            try:
                await download_msg.edit("❌ **Processing failed!**")
            except:
                pass
        return False
    finally:
        # Clean up downloaded files
        if file_path:
            await safe_delete_file(file_path)
        if thumbnail:
            await safe_delete_file(thumbnail)

@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    """Handle text messages with Telegram links"""
    try:
        await db.update_last_active(message.from_user.id)
        
        # Skip if message doesn't contain a Telegram link or is a command
        if "https://t.me/" not in message.text or message.text.startswith('/'):
            return
            
        # Validate it's actually a post link
        if not is_valid_telegram_post_link(message.text.strip()):
            await message.reply_text("❌ **Invalid Telegram link!**\n\nPlease send a valid Telegram post link.")
            return
            
        # Check if another task is running
        if BatchTemp.get_batch_state(message.from_user.id) == False:
            await message.reply_text("⚠️ **Another task is already running!**\n\nPlease wait for it to complete or use /cancel to stop it.")
            return
        
        # Parse the link
        try:
            datas = message.text.strip().split("/")
            temp = datas[-1].replace("?single", "").split("-")
            fromID = int(temp[0].strip())
            try:
                toID = int(temp[1].strip())
            except:
                toID = fromID
        except Exception as e:
            logger.error(f"Error parsing link: {e}")
            await message.reply_text("❌ **Invalid link format!**")
            return
        
        # Check batch size limit
        batch_size = toID - fromID + 1
        if batch_size > MAX_BATCH_SIZE:
            await message.reply_text(f"❌ **Batch size too large!**\n\nMaximum {MAX_BATCH_SIZE} messages allowed at once.")
            return
        
        BatchTemp.set_batch_state(message.from_user.id, False)
        
        # Process messages
        processed = 0
        failed = 0
        
        # Single message handling
        if batch_size == 1:
            success = await process_single_message(client, message, datas, fromID)
            if success:
                processed = 1
            else:
                failed = 1
        else:
            # Batch processing
            status_msg = await message.reply_text(
                f"📥 **Starting Batch Download**\n\n"
                f"📊 **Range:** {fromID} to {toID}\n"
                f"📝 **Total:** {batch_size} messages\n"
                f"⏳ **Status:** Processing..."
            )
            
            for i, msgid in enumerate(range(fromID, toID + 1)):
                if BatchTemp.get_batch_state(message.from_user.id):
                    break
                
                # Update progress every 5 messages
                if i % 5 == 0 and batch_size > 5:
                    try:
                        await status_msg.edit(
                            f"📥 **Batch Download in Progress**\n\n"
                            f"📊 **Range:** {fromID} to {toID}\n"
                            f"📝 **Total:** {batch_size} messages\n"
                            f"✅ **Processed:** {processed}\n"
                            f"❌ **Failed:** {failed}\n"
                            f"⏳ **Current:** {msgid}"
                        )
                    except:
                        pass
                    
                try:
                    success = await process_single_message(client, message, datas, msgid)
                    if success:
                        processed += 1
                    else:
                        failed += 1
                except Exception as e:
                    logger.error(f"Failed to process message {msgid}: {e}")
                    failed += 1
                
                # Small delay between messages
                await asyncio.sleep(MINIMAL_DELAY)
            
            # Update final status
            try:
                await status_msg.edit(
                    f"✅ **Batch Download Completed!**\n\n"
                    f"📊 **Final Summary:**\n"
                    f"✅ **Success:** {processed}\n"
                    f"❌ **Failed:** {failed}\n"
                    f"📝 **Total:** {processed + failed}/{batch_size}"
                )
            except:
                pass
        
        # Reset batch state
        BatchTemp.set_batch_state(message.from_user.id, True)
        
    except Exception as e:
        logger.error(f"Error in save handler: {e}")
        BatchTemp.set_batch_state(message.from_user.id, True)
        await message.reply_text("❌ **An error occurred!** Please try again later.")

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
