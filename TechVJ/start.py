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
import gc

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
    USER_CONNECTIONS = {}
    
    @classmethod
    def set_batch_state(cls, user_id, state):
        cls.IS_BATCH[user_id] = state
        if not state:
            if user_id in cls.USER_CONNECTIONS:
                del cls.USER_CONNECTIONS[user_id]
    
    @classmethod
    def get_batch_state(cls, user_id):
        return cls.IS_BATCH.get(user_id, True)

async def safe_delete_file(file_path):
    """Safely delete a file with retry mechanism"""
    if not file_path or not os.path.exists(file_path):
        return
        
    for attempt in range(3):
        try:
            os.remove(file_path)
            logger.debug(f"Deleted file: {file_path}")
            return
        except Exception as e:
            if attempt == 2:
                logger.error(f"Failed to delete file {file_path}: {e}")
            await asyncio.sleep(0.5)

async def ultra_fast_download(acc, msg, message, max_retries=3):
    """Ultra-fast download with better error handling"""
    for attempt in range(max_retries):
        try:
            logger.info(f"Download attempt {attempt + 1}")
            file = await acc.download_media(msg, progress=progress, progress_args=[message, "down"])
            return file
        except FloodWait as e:
            logger.warning(f"FloodWait: waiting {e.value} seconds")
            await asyncio.sleep(e.value)
        except Exception as e:
            logger.warning(f"Download attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2)
            else:
                raise e

async def get_ultra_hd_thumbnail(acc, media_obj):
    """Get the highest quality thumbnail available with timeout"""
    try:
        return await asyncio.wait_for(_get_thumbnail_internal(acc, media_obj), timeout=30)
    except asyncio.TimeoutError:
        logger.warning("Thumbnail download timed out")
        return None
    except Exception as e:
        logger.error(f"Error getting thumbnail: {e}")
        return None

async def _get_thumbnail_internal(acc, media_obj):
    """Internal thumbnail extraction logic"""
    if hasattr(media_obj, 'photo') and media_obj.photo:
        if hasattr(media_obj.photo, 'sizes') and media_obj.photo.sizes:
            largest = max(media_obj.photo.sizes, key=lambda x: x.width * x.height)
            return await acc.download_media(largest.file_id)
    
    elif hasattr(media_obj, 'video') and media_obj.video:
        if hasattr(media_obj.video, 'thumbs') and media_obj.video.thumbs:
            best_thumb = max(media_obj.video.thumbs, 
                           key=lambda x: getattr(x, 'width', 0) * getattr(x, 'height', 0))
            if best_thumb and hasattr(best_thumb, 'file_id'):
                return await acc.download_media(best_thumb.file_id)
    
    elif hasattr(media_obj, 'document') and media_obj.document:
        if hasattr(media_obj.document, 'thumbs') and media_obj.document.thumbs:
            best_thumb = max(media_obj.document.thumbs,
                           key=lambda x: getattr(x, 'width', 0) * getattr(x, 'height', 0))
            if best_thumb and hasattr(best_thumb, 'file_id'):
                return await acc.download_media(best_thumb.file_id)
    
    return None

async def create_client_with_retry(user_data, user_id):
    """Create and connect client with retry and connection tracking"""
    if user_id in BatchTemp.USER_CONNECTIONS:
        try:
            existing_client = BatchTemp.USER_CONNECTIONS[user_id]
            await existing_client.get_me()
            return existing_client
        except:
            try:
                await existing_client.disconnect()
            except:
                pass
            del BatchTemp.USER_CONNECTIONS[user_id]
    
    for attempt in range(3):
        try:
            acc = Client(
                ":memory:", 
                session_string=user_data, 
                api_hash=API_HASH, 
                api_id=API_ID
            )
            await acc.connect()
            BatchTemp.USER_CONNECTIONS[user_id] = acc
            return acc
        except Exception as e:
            logger.warning(f"Client connection attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                await asyncio.sleep(3)
            else:
                raise e

def progress(current, total, message, type):
    """Improved progress with better error handling"""
    try:
        if total <= 0:
            return
            
        percentage = current * 100 / total
        progress_key = f"{message.id}_{type}"
        
        if progress_key in _last_progress_update:
            if percentage - _last_progress_update[progress_key] < 10:
                return
        
        _last_progress_update[progress_key] = percentage
        speed = (current / 1024 / 1024) if current > 0 else 0
        
        status_text = f"⚡ {percentage:.1f}% | {speed:.1f}MB processed"
        
        try:
            with open(f'{message.id}{type}status.txt', "w") as fileup:
                fileup.write(status_text)
        except:
            pass
            
    except Exception:
        pass

_last_progress_update = {}

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
        try:
            await message.reply_text("❌ An error occurred. Please try again later.")
        except:
            pass

@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    """Handle /help command"""
    try:
        await db.update_last_active(message.from_user.id)
        await client.send_message(chat_id=message.chat.id, text=HELP_TXT)
    except Exception as e:
        logger.error(f"Error in help command: {e}")
        try:
            await message.reply_text("❌ An error occurred. Please try again later.")
        except:
            pass

@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    """Handle /cancel command with proper cleanup"""
    try:
        user_id = message.from_user.id
        await db.update_last_active(user_id)
        
        if user_id in BatchTemp.USER_CONNECTIONS:
            try:
                await BatchTemp.USER_CONNECTIONS[user_id].disconnect()
            except:
                pass
            del BatchTemp.USER_CONNECTIONS[user_id]
        
        BatchTemp.set_batch_state(user_id, True)
        
        await client.send_message(
            chat_id=message.chat.id, 
            text="🛑 **Batch Successfully Cancelled.**\n\n✅ All connections cleaned up."
        )
        logger.info(f"User {user_id} cancelled batch operation")
        
    except Exception as e:
        logger.error(f"Error in cancel command: {e}")
        try:
            await message.reply_text("❌ An error occurred during cancellation.")
        except:
            pass

async def process_single_message(client, message, datas, msgid, user_id):
    """Process a single message with better error handling and cleanup"""
    acc = None
    try:
        user_data = await db.get_session(user_id)
        if user_data is None:
            return False, "Not logged in"
        
        acc = await create_client_with_retry(user_data, user_id)
        
        if "/c/" in message.text:
            chat_id = int("-100" + str(datas[4]))
        else:
            chat_id = datas[3]
        
        msg_list = await asyncio.wait_for(acc.get_messages(chat_id, msgid), timeout=30)
        
        if not msg_list or len(msg_list) == 0:
            logger.warning(f"Empty message {msgid}")
            return False, "Empty message"
            
        msg = msg_list[0] if isinstance(msg_list, list) else msg_list
        
        if msg.media:
            success = await process_media_message(client, message, acc, msg, user_id)
            return success, "Media processed" if success else "Media failed"
        elif msg.text:
            await client.send_message(
                message.chat.id,
                f"📝 **Text Message {msgid}:**\n\n{msg.text[:1000]}{'...' if len(msg.text) > 1000 else ''}"
            )
            return True, "Text processed"
        
        return True, "Processed"
        
    except asyncio.TimeoutError:
        logger.error(f"Timeout processing message {msgid}")
        return False, "Timeout"
    except Exception as e:
        logger.error(f"Error processing message {msgid}: {e}")
        return False, f"Error: {str(e)[:50]}"
    finally:
        gc.collect()

async def process_media_message(client, message, acc, msg, user_id):
    """Process media message with better cleanup and error handling"""
    download_msg = None
    file_path = None
    thumbnail = None
    
    try:
        if BatchTemp.get_batch_state(user_id):
            return False
            
        if hasattr(msg.media, 'file_size') and msg.media.file_size > MAX_FILE_SIZE:
            await message.reply_text("📦 **File too large!** Skipping...")
            return False
        
        download_msg = await client.send_message(
            message.chat.id,
            f"⚡ **Processing media...**"
        )
        
        file_path = await asyncio.wait_for(
            ultra_fast_download(acc, msg, download_msg), 
            timeout=600
        )
        
        if not file_path:
            await download_msg.edit("❌ **Download failed!**")
            return False
        
        thumbnail = await get_ultra_hd_thumbnail(acc, msg.media)
        
        await download_msg.edit("⚡ **Uploading...**")
        
        if msg.photo:
            await client.send_photo(
                message.chat.id,
                file_path,
                caption=msg.caption or "📸 **Photo**"
            )
        elif msg.video:
            await client.send_video(
                message.chat.id,
                file_path,
                thumb=thumbnail,
                caption=msg.caption or "🎥 **Video**",
                supports_streaming=True
            )
        elif msg.document:
            await client.send_document(
                message.chat.id,
                file_path,
                thumb=thumbnail,
                caption=msg.caption or "📄 **Document**"
            )
        elif msg.audio:
            await client.send_audio(
                message.chat.id,
                file_path,
                thumb=thumbnail,
                caption=msg.caption or "🎵 **Audio**"
            )
        else:
            await client.send_document(
                message.chat.id,
                file_path,
                caption=msg.caption or "📎 **File**"
            )
        
        try:
            await download_msg.delete()
        except:
            pass
            
        return True
        
    except asyncio.TimeoutError:
        logger.error("Media processing timed out")
        try:
            if download_msg:
                await download_msg.edit("⏰ **Process timed out!**")
        except:
            pass
        return False
    except FloodWait as e:
        logger.warning(f"FloodWait in media processing: {e.value}s")
        await asyncio.sleep(e.value)
        return False
    except Exception as e:
        logger.error(f"Error processing media: {e}")
        try:
            if download_msg:
                await download_msg.edit("❌ **Processing failed!**")
        except:
            pass
        return False
    finally:
        if file_path:
            await safe_delete_file(file_path)
        if thumbnail:
            await safe_delete_file(thumbnail)
        gc.collect()

@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    """Handle text messages with improved batch processing"""
    user_id = message.from_user.id
    
    try:
        await db.update_last_active(user_id)
        
        if "https://t.me/" not in message.text or message.text.startswith('/'):
            return
            
        if not is_valid_telegram_post_link(message.text.strip()):
            await message.reply_text(ERROR_MESSAGES['invalid_link'])
            return
            
        if BatchTemp.get_batch_state(user_id) == False:
            await message.reply_text(ERROR_MESSAGES['task_in_progress'])
            return
        
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
            await message.reply_text(ERROR_MESSAGES['invalid_link'])
            return
        
        batch_size = toID - fromID + 1
        max_safe_batch = min(MAX_BATCH_SIZE, 50)
        
        if batch_size > max_safe_batch:
            await message.reply_text(f"❌ **Batch too large!**\n\nMaximum {max_safe_batch} messages allowed. You requested {batch_size} messages.")
            return
        
        BatchTemp.set_batch_state(user_id, False)
        
        status_msg = await message.reply_text(
            f"📥 **Starting Batch Download**\n\n"
            f"📊 **Range:** {fromID} to {toID}\n"
            f"📝 **Total:** {batch_size} messages\n"
            f"⏳ **Status:** Initializing..."
        )
        
        processed = 0
        failed = 0
        skipped = 0
        
        try:
            for i, msgid in enumerate(range(fromID, toID + 1)):
                if BatchTemp.get_batch_state(user_id):
                    break
                
                if i % 5 == 0:
                    try:
                        await status_msg.edit(
                            f"📥 **Batch Download in Progress**\n\n"
                            f"📊 **Range:** {fromID} to {toID}\n"
                            f"📝 **Total:** {batch_size} messages\n"
                            f"✅ **Processed:** {processed}\n"
                            f"❌ **Failed:** {failed}\n"
                            f"⏳ **Current:** {msgid}"
                        )
                    except MessageNotModified:
                        pass
                    except:
                        pass
                
                try:
                    success, reason = await process_single_message(client, message, datas, msgid, user_id)
                    if success:
                        processed += 1
                    else:
                        if "empty" in reason.lower():
                            skipped += 1
                        else:
                            failed += 1
                            
                except Exception as e:
                    logger.error(f"Failed to process message {msgid}: {e}")
                    failed += 1
                
                await asyncio.sleep(2)
                
                if (i + 1) % 10 == 0:
                    await asyncio.sleep(5)
            
        except Exception as e:
            logger.error(f"Batch processing error: {e}")
            
        finally:
            BatchTemp.set_batch_state(user_id, True)
            
            if user_id in BatchTemp.USER_CONNECTIONS:
                try:
                    await BatchTemp.USER_CONNECTIONS[user_id].disconnect()
                except:
                    pass
                del BatchTemp.USER_CONNECTIONS[user_id]
            
            total_attempted = processed + failed
            summary_text = (
                f"✅ **Batch Download Completed!**\n\n"
                f"📊 **Final Summary:**\n"
                f"✅ **Success:** {processed}\n"
                f"❌ **Failed:** {failed}\n"
                f"⏭️ **Skipped:** {skipped}\n"
                f"📝 **Total Attempted:** {total_attempted}/{batch_size}\n\n"
                f"🎉 **Download Complete!**"
            )
            
            try:
                await status_msg.edit(summary_text)
            except:
                await message.reply_text(summary_text)
        
    except Exception as e:
        logger.error(f"Error in save handler: {e}")
        BatchTemp.set_batch_state(user_id, True)
        try:
            await message.reply_text("❌ **An error occurred!** Please try again later.")
        except:
            pass

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
