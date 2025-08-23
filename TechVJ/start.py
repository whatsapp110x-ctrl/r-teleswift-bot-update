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
    """Validate if session is still active"""
    try:
        test_client = Client(":memory:", session_string=session_string, api_id=API_ID, api_hash=API_HASH)
        await test_client.connect()
        me = await test_client.get_me()
        await test_client.disconnect()
        return True
    except (AuthKeyUnregistered, SessionExpired, SessionRevoked):
        return False
    except Exception as e:
        logger.error(f"Session validation error: {e}")
        return False

async def create_client_with_retry(user_data, max_retries=3):
    """Create and connect client with retry mechanism and session validation"""
    if not user_data:
        raise Exception("No session data provided")
    
    # First validate the session
    if not await validate_session(user_data):
        raise Exception("Session expired or invalid")
    
    for attempt in range(max_retries):
        try:
            acc = Client(
                f":memory:{attempt}", 
                session_string=user_data, 
                api_hash=API_HASH, 
                api_id=API_ID,
                sleep_threshold=SLEEP_THRESHOLD,
                max_concurrent_transmissions=5
            )
            await acc.connect()
            
            # Test connection
            await acc.get_me()
            return acc
            
        except (AuthKeyUnregistered, SessionExpired, SessionRevoked):
            raise Exception("Session expired - please login again")
        except Exception as e:
            logger.warning(f"Client connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(RETRY_DELAY * (attempt + 1))
            else:
                raise Exception(f"Failed to connect after {max_retries} attempts: {str(e)}")

async def ultra_fast_download(acc, msg, message, max_retries=MAX_RETRIES):
    """Ultra-fast download with retry mechanism"""
    for attempt in range(max_retries):
        try:
            logger.info(f"Download attempt {attempt + 1} for message {msg.id}")
            file = await acc.download_media(
                msg, 
                progress=progress, 
                progress_args=[message, "down"]
            )
            if file and os.path.exists(file):
                return file
            else:
                raise Exception("Downloaded file not found")
        except FloodWait as fw:
            logger.warning(f"FloodWait {fw.value}s on attempt {attempt + 1}")
            await asyncio.sleep(fw.value)
        except Exception as e:
            logger.warning(f"Download attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(RETRY_DELAY * (attempt + 1))
            else:
                raise e

async def get_ultra_hd_thumbnail(acc, msg):
    """Get the highest quality thumbnail available"""
    try:
        thumbnail_path = None
        
        # For videos
        if msg.video and hasattr(msg.video, 'thumbs') and msg.video.thumbs:
            largest_thumb = max(msg.video.thumbs, key=lambda x: getattr(x, 'file_size', 0))
            thumbnail_path = await acc.download_media(largest_thumb.file_id)
                
        # For documents
        elif msg.document and hasattr(msg.document, 'thumbs') and msg.document.thumbs:
            largest_thumb = max(msg.document.thumbs, key=lambda x: getattr(x, 'file_size', 0))
            thumbnail_path = await acc.download_media(largest_thumb.file_id)
        
        # For photos
        elif msg.photo:
            thumbnail_path = await acc.download_media(msg.photo.file_id)
        
        if thumbnail_path and os.path.exists(thumbnail_path):
            return thumbnail_path
        else:
            return None
            
    except Exception as e:
        logger.error(f"Error getting thumbnail: {e}")
        return None

_last_progress_update = {}

def progress(current, total, message, type):
    """Progress callback with throttling"""
    try:
        percentage = current * 100 / total
        progress_key = f"{message.id}_{type}"
        
        if progress_key in _last_progress_update:
            if abs(percentage - _last_progress_update[progress_key]) < 5:
                return
        
        _last_progress_update[progress_key] = percentage
        
        with open(f'{message.id}{type}status.txt', "w") as fileup:
            fileup.write(f"{percentage:.1f}% | {current/1024/1024:.1f}MB/{total/1024/1024:.1f}MB")
    except Exception:
        pass

async def process_media_message(client, message, acc, msg):
    """Process media message for download"""
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
        status_msg = await message.reply_text(f"⬇️ Downloading {filename}...")
        
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
            caption = f"📎 {filename}\n\nDownloaded successfully!"
            
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
    """Process a single message for download"""
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
                await message.reply_text(f"❌ Connection error: {error_msg[:100]}")
            return False
        
        # Determine chat ID
        try:
            if "/c/" in message.text:
                chat_id = int("-100" + str(datas[4]))
            else:
                chat_id = datas[3]
        except Exception:
            await message.reply_text("❌ Invalid link format")
            return False
        
        # Get message
        try:
            msg = await acc.get_messages(chat_id, msgid)
            
            if not msg or (hasattr(msg, 'empty') and msg.empty):
                await message.reply_text("❌ Message not found or empty")
                return False
            
            # Process the message
            if msg.media:
                success = await process_media_message(client, message, acc, msg)
                return success
            elif msg.text:
                await client.send_message(
                    message.chat.id,
                    f"📝 **Text Message:**\n\n{msg.text}"
                )
                return True
            else:
                await message.reply_text("❌ Message has no content")
                return False
                
        except (ChannelPrivate, ChatAdminRequired, UserNotParticipant):
            await message.reply_text("❌ Cannot access private channel. Make sure you're a member.")
            return False
        except (PeerIdInvalid, ChannelInvalid, MessageIdInvalid):
            await message.reply_text("❌ Invalid channel or message ID")
            return False
        except Exception as msg_error:
            logger.error(f"Error getting message {msgid}: {msg_error}")
            await message.reply_text(f"❌ Failed to get message: {str(msg_error)[:100]}")
            return False
            
    except Exception as e:
        logger.error(f"Error processing message {msgid}: {e}")
        await message.reply_text(f"❌ Processing error: {str(e)[:100]}")
        return False
    finally:
        # Clean up
        if acc:
            try:
                await acc.disconnect()
                await asyncio.sleep(1)  # Brief pause to ensure clean disconnect
            except:
                pass
        BatchTemp.clear_user_task(message.from_user.id)

async def process_single_message_batch(client, message, datas, msgid, acc):
    """Process single message in batch mode with shared client"""
    try:
        # Determine chat ID
        try:
            if "/c/" in message.text:
                chat_id = int("-100" + str(datas[4]))
            else:
                chat_id = datas[3]
        except Exception:
            return False
        
        # Get message
        try:
            msg = await acc.get_messages(chat_id, msgid)
            
            if not msg or (hasattr(msg, 'empty') and msg.empty):
                return False
            
            # Process the message
            if msg.media:
                success = await process_media_message_batch(client, message, acc, msg)
                return success
            elif msg.text:
                await client.send_message(
                    message.chat.id,
                    f"📝 **Message {msgid}:**\n\n{msg.text[:500]}..."
                )
                return True
            else:
                return False
                
        except (ChannelPrivate, ChatAdminRequired, UserNotParticipant):
            logger.warning(f"Access denied for message {msgid}")
            return False
        except (PeerIdInvalid, ChannelInvalid, MessageIdInvalid):
            logger.warning(f"Invalid message {msgid}")
            return False
        except FloodWait as fw:
            logger.warning(f"FloodWait {fw.value}s for message {msgid}")
            await asyncio.sleep(fw.value)
            return False
        except Exception as e:
            logger.error(f"Error getting batch message {msgid}: {e}")
            return False
            
    except Exception:
        return False

async def process_media_message_batch(client, message, acc, msg):
    """Process media message in batch mode (simplified)"""
    try:
        file_size = 0
        filename = f"file_{msg.id}"
        
        if msg.document:
            file_size = msg.document.file_size
            filename = getattr(msg.document, 'file_name', f'document_{msg.id}')
        elif msg.video:
            file_size = msg.video.file_size
            filename = f'video_{msg.id}.mp4'
        elif msg.photo:
            file_size = msg.photo.file_size
            filename = f'photo_{msg.id}.jpg'
        elif msg.audio:
            file_size = msg.audio.file_size
            filename = getattr(msg.audio, 'file_name', f'audio_{msg.id}.mp3')
        else:
            return False
        
        # Skip large files in batch mode
        if file_size > MAX_FILE_SIZE // 2:  # Half the limit for batch
            return False
        
        try:
            # Download without progress for batch
            file_path = await acc.download_media(msg)
            
            if not file_path or not os.path.exists(file_path):
                return False
            
            # Upload based on media type (simplified)
            caption = f"📎 {filename}"
            
            if msg.document:
                await client.send_document(message.chat.id, file_path, caption=caption)
            elif msg.video:
                await client.send_video(message.chat.id, file_path, caption=caption)
            elif msg.photo:
                await client.send_photo(message.chat.id, file_path, caption=caption)
            elif msg.audio:
                await client.send_audio(message.chat.id, file_path, caption=caption)
            
            # Clean up
            await safe_delete_file(file_path)
            return True
            
        except Exception as e:
            logger.error(f"Batch media error: {e}")
            return False
            
    except Exception:
        return False

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
        BatchTemp.clear_user_task(message.from_user.id)
        await client.send_message(
            chat_id=message.chat.id, 
            text="🛑 **All tasks cancelled successfully.**"
        )
        logger.info(f"User {message.from_user.id} cancelled operations")
    except Exception as e:
        logger.error(f"Error in cancel command: {e}")
        await message.reply_text("❌ An error occurred. Please try again later.")

@Client.on_message((filters.regex(r"https://t.me/\S+") | filters.regex(r"t.me/\S+")) & filters.private & ~filters.command(["login", "logout", "start", "help", "cancel"]))
async def save_restricted_content(client, message):
    """Handle Telegram link processing"""
    try:
        await db.update_last_active(message.from_user.id)
        
        # Extract URL
        url = message.text.strip()
        if not url.startswith('https://'):
            url = 'https://' + url
        
        if not is_valid_telegram_post_link(url):
            await message.reply_text(ERROR_MESSAGES['invalid_link'])
            return
        
        try:
            datas = url.split('/')
        except:
            await message.reply_text(ERROR_MESSAGES['invalid_link'])
            return
        
        # Handle batch downloads
        if '-' in datas[-1]:
            await handle_batch_download(client, message, url, datas)
        else:
            # Single message download
            try:
                msgid = int(datas[-1])
            except ValueError:
                await message.reply_text("❌ Invalid message ID")
                return
                
            success = await process_single_message(client, message, datas, msgid)
            if success:
                logger.info(f"Single download completed for user {message.from_user.id}")
            else:
                logger.warning(f"Single download failed for user {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error in save_restricted_content: {e}")
        await message.reply_text("❌ An unexpected error occurred. Please try again.")

async def handle_batch_download(client, message, url, datas):
    """Handle batch download processing with improved session management"""
    acc = None
    try:
        # Check if user has active task
        if BatchTemp.get_user_task(message.from_user.id):
            await message.reply_text("⏳ Another task is in progress. Please wait or use /cancel")
            return
        
        # Parse range
        try:
            temp = datas[-1].split('-')
            start_id = int(temp[0])
            end_id = int(temp[1])
        except (ValueError, IndexError):
            await message.reply_text("❌ Invalid batch range format")
            return
        
        if end_id - start_id > MAX_BATCH_SIZE:
            await message.reply_text(f"❌ Batch size too large. Max: {MAX_BATCH_SIZE}")
            return
        
        if start_id >= end_id:
            await message.reply_text("❌ Invalid range: start must be less than end")
            return
        
        # Set batch state
        BatchTemp.set_batch_state(message.from_user.id, False)
        BatchTemp.set_user_task(message.from_user.id, "batch_download")
        
        # Get user session
        user_data = await db.get_session(message.from_user.id)
        if user_data is None:
            await message.reply_text(ERROR_MESSAGES['not_logged_in'])
            BatchTemp.clear_user_task(message.from_user.id)
            return
        
        # Create persistent client for batch operation
        try:
            acc = await create_client_with_retry(user_data)
        except Exception as e:
            error_msg = str(e)
            if "Session expired" in error_msg or "invalid" in error_msg:
                await message.reply_text(ERROR_MESSAGES['session_expired'])
                await db.set_session(message.from_user.id, None)
            else:
                await message.reply_text(f"❌ Connection error: {error_msg[:100]}")
            BatchTemp.clear_user_task(message.from_user.id)
            return
        
        # Send batch start message
        batch_msg = await message.reply_text(
            f"📦 **Batch Download Started**\n\n"
            f"📊 **Range:** {start_id} to {end_id}\n"
            f"📈 **Total:** {end_id - start_id + 1} messages\n"
            f"⏳ **Status:** Starting...\n\n"
            f"Use /cancel to stop"
        )
        
        success_count = 0
        failed_count = 0
        total_count = end_id - start_id + 1
        
        # Process each message with shared client
        for msg_id in range(start_id, end_id + 1):
            try:
                # Check if cancelled
                if BatchTemp.get_batch_state(message.from_user.id):
                    await batch_msg.edit(
                        f"🛑 **Batch Download Cancelled!**\n\n"
                        f"✅ Success: {success_count}\n"
                        f"❌ Failed: {failed_count}\n"
                        f"📝 Total: {success_count + failed_count}/{total_count}"
                    )
                    break
                
                # Process single message with shared client
                success = await process_single_message_batch(client, message, datas, msg_id, acc)
                
                if success:
                    success_count += 1
                else:
                    failed_count += 1
                
                # Update progress every 3 messages or at end
                if (success_count + failed_count) % 3 == 0 or (success_count + failed_count) == total_count:
                    try:
                        await batch_msg.edit(
                            f"📦 **Batch Download Progress**\n\n"
                            f"✅ Success: {success_count}\n"
                            f"❌ Failed: {failed_count}\n"
                            f"📝 Processed: {success_count + failed_count}/{total_count}\n"
                            f"📊 Progress: {((success_count + failed_count)/total_count)*100:.1f}%\n\n"
                            f"⏳ Current: {msg_id}"
                        )
                    except MessageNotModified:
                        pass
                
                # Small delay to prevent rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error processing batch message {msg_id}: {e}")
                failed_count += 1
                continue
        
        # Final summary
        await batch_msg.edit(
            f"✅ **Batch Download Completed!**\n\n"
            f"📊 **Final Summary:**\n"
            f"✅ Success: {success_count}\n"
            f"❌ Failed: {failed_count}\n"
            f"📝 Total: {total_count}/{total_count}"
        )
        
        logger.info(f"Batch download completed for user {message.from_user.id}: {success_count}/{total_count}")
        
    except Exception as e:
        logger.error(f"Error in batch download: {e}")
        await message.reply_text(f"❌ Batch download error: {str(e)[:100]}")
    finally:
        # Clean up
        if acc:
            try:
                await acc.disconnect()
                await asyncio.sleep(2)  # Ensure clean disconnect
            except:
                pass
        BatchTemp.clear_user_task(message.from_user.id)
        BatchTemp.set_batch_state(message.from_user.id, True)

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
